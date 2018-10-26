import asyncio
import json
import random
import secrets
import time
import uuid

import websockets
from game import GameHost, channels
from game.lobby import LobbyState, LobbyUser
from game.namespace import namespaced
from game.net import state as st, validator
from game.net.handshake.identify import HandshakeIdentifyMessage
from game.net.handshake.new_user import HandshakeNewUserMessage
from game.net.handshake.prompt_new_user import HandshakePromptNewUserMessage
from game.net.handshake.upgrade import HandshakeUpgradeMessage
from game.net.handshake.user_info import HandshakeUserInfoMessage
from game.net.lobby.config import LobbyConfigMessage
from game.net.lobby.config_response import LobbyConfigResponseMessage
from game.net.lobby.join_response import LobbyJoinResponseMessage
from game.net.lobby.set_state import LobbySetStateMessage
from game.net.lobby.update_list import LobbyUpdateListMessage
from game.net.message import InboundMessage, OutboundMessage


class PlayerConnection:
    def __init__(self, host: GameHost, websocket: websockets.WebSocketServerProtocol, session_token: str):
        self.host = host
        self.websocket = websocket
        self.session_token = session_token
        self._state = st.HS_UNIDENTIFIED
        self._user_creation_transaction = None

        self.user_token: str = None
        self.user_name: str = None
        self.user_discrim: str = None

        self._handler_lobby_list = None
        self._current_lobby_id = None

    async def send(self, message: OutboundMessage):
        if self.websocket.closed:
            return

        build = message.build(self.session_token)
        output = json.dumps(build)
        await self.websocket.send(output)

    async def reject_authentication(self):
        self._user_creation_transaction = secrets.token_urlsafe(32)
        if self.state != st.HS_USER_PROMPTING:
            self.upgrade(st.HS_USER_PROMPTING)
        await self.send(
            HandshakePromptNewUserMessage(
                transaction_id=self._user_creation_transaction
            )
        )

    async def on_receive(self, message: InboundMessage):
        if self.state == st.HS_UNIDENTIFIED:
            if isinstance(message, HandshakeIdentifyMessage):
                message: HandshakeIdentifyMessage = message
                token = message.token
                redis = self.host.redis()

                if not token or not isinstance(token, str) or not redis.exists(namespaced(f"token:{token}")):
                    await self.reject_authentication()
                    return

                name_with_discrim = redis.get(namespaced(f"token:{token}")).decode("utf-8")
                if name_with_discrim.count("#") != 1:
                    await self.reject_authentication()
                    return

                self.user_name, self.user_discrim = name_with_discrim.split("#", maxsplit=1)
                self.user_token = token

                self.upgrade(st.HS_IDENTIFIED)
                await self.send(
                    HandshakeUserInfoMessage(
                        user_token=self.user_token,
                        user_name=self.name_with_discrim
                    )
                )
                self.upgrade(st.LOBBY_INIT)
                await self.send(
                    HandshakeUpgradeMessage()
                )
                return

        if self.state == st.HS_USER_PROMPTING:
            if isinstance(message, HandshakeNewUserMessage):
                message: HandshakeNewUserMessage = message
                if not self._user_creation_transaction or message.transaction_id != self._user_creation_transaction:
                    # unknown/unexpected transaction
                    print("Received an unknown user prompt transaction: ", self._user_creation_transaction,
                          message.transaction_id)
                    return
                self._user_creation_transaction = None

                username = message.user_name
                if not validator.username_valid(username):
                    await self.reject_authentication()
                    return

                redis = self.host.redis()
                # Generate discriminator (between 0001 and 9999, inclusive)
                while self.user_discrim is None:
                    discrim = str(random.randint(1, 9999)).zfill(4)
                    if not redis.exists(namespaced(f"user_name:{username}#{discrim}")):
                        self.user_discrim = discrim

                self.user_name = username
                self.user_token = secrets.token_urlsafe(64)

                redis.pipeline() \
                    .set(namespaced(f"user_name:{self.name_with_discrim}"), self.user_token) \
                    .set(namespaced(f"token:{self.user_token}"), self.name_with_discrim) \
                    .execute()

                self.upgrade(st.HS_IDENTIFIED)
                await self.send(
                    HandshakeUserInfoMessage(
                        user_token=self.user_token,
                        user_name=self.name_with_discrim
                    )
                )
                self.upgrade(st.LOBBY_INIT)
                await self.send(
                    HandshakeUpgradeMessage()
                )
                return

        if self.state == st.LOBBY_INIT:
            if isinstance(message, LobbySetStateMessage):
                message: LobbySetStateMessage = message
                if message.state == "list":
                    self.upgrade(st.LOBBY_LIST)
                    # get all open lobbies from redis
                    open_lobbies_ids = list(self.host.redis().smembers(namespaced("lobby_open_index")))
                    if len(open_lobbies_ids):
                        open_lobbies = self.host.redis().mget(
                            list(namespaced(f"lobby:{lid.decode('utf-8')}") for lid in open_lobbies_ids)
                        )
                    else:
                        open_lobbies = []

                    response_lobbies = [
                        LobbyState.deserialize(
                            json.loads(lobby_json_bstr.decode('utf-8'))
                        ).serialize()
                        for lobby_json_bstr in filter(lambda lb: lb is not None, open_lobbies)
                    ]

                    await self.send(LobbyUpdateListMessage(lobbies=response_lobbies))
                    return

        if self.state == st.LOBBY_LIST or self.state == st.LOBBY_INIT:
            if isinstance(message, LobbyConfigMessage):
                # Lobby CREATE request
                message: LobbyConfigMessage = message

                lobby_name = message.name
                if lobby_name is None:
                    return
                lobby_name = lobby_name.strip()
                if not validator.lobby_name_valid(lobby_name):
                    await self.send(
                        LobbyConfigResponseMessage(error="Invalid lobby name.")
                    )
                    return

                max_players = message.max_players
                if not isinstance(max_players, int) or max_players > 3 or max_players < 1:
                    await self.send(
                        LobbyConfigResponseMessage(error="Invalid player count, must be between 1 and 3 players.")
                    )
                    return

                lobby_id = str(uuid.uuid4())
                current_time_epoch_seconds = int(time.time())

                lobby_state = LobbyState(
                    lobby_id=lobby_id,
                    name=lobby_name,
                    created_time=current_time_epoch_seconds,
                    start_time=None,
                    max_players=max_players,
                    players=[
                        LobbyUser(name=self.name_with_discrim, ready=False)
                    ]
                )
                # Set in redis and notify the lobby list channel
                self._edit_and_publish_lobby_state(lobby_state)

                # Notify client that the lobby was created
                await self.send(
                    LobbyConfigResponseMessage(
                        lobby_id=lobby_id,
                        error=None
                    )
                )
                self._current_lobby_id = lobby_id
                self.upgrade(st.LOBBY_VIEW)
                return

            if isinstance(message, LobbySetStateMessage):
                # Lobby JOIN request
                message: LobbySetStateMessage = message
                if message.lobby_id is None:
                    return
                lobby_id = message.lobby_id
                lobby_state_json = self.host.redis().get(namespaced(f"lobby:{lobby_id}"))
                if lobby_state_json is None:
                    await self.send(
                        LobbyJoinResponseMessage(lobby_id=lobby_id, joined=False)
                    )
                    return

                # parse lobby
                lobby_state_json = lobby_state_json.decode("utf-8")
                lobby_state = LobbyState.deserialize(json.loads(lobby_state_json))
                if not lobby_state.is_open:
                    await self.send(
                        LobbyJoinResponseMessage(lobby_id=lobby_id, joined=False)
                    )
                    return

                # add player to list
                lobby_state.players.append(LobbyUser(name=self.name_with_discrim, ready=False))
                self._edit_and_publish_lobby_state(lobby_state)
                self.upgrade(st.LOBBY_VIEW)
                await self.send(
                    LobbyJoinResponseMessage(lobby_id=lobby_id, joined=True)
                )
                return

        print(f"Received a message unknown message or invalid state, state={self.state.state_id}, op={message.op}")

    def cleanup(self):
        # session death

        # remove pubsub handlers
        if self._handler_lobby_list is not None:
            self.host.redis_channel_unsub(self._handler_lobby_list)

        # remove self from current lobby
        if self._current_lobby_id is not None:
            self._leave_lobby(self._current_lobby_id)
            self._current_lobby_id = None

    def _leave_lobby(self, lobby_id: str):
        # Removes this player from a lobby in Redis. Does not notify the client specifically, but it may be notified
        # through the global "lobby list" update.

        lobby_json = self.host.redis().get(namespaced(f"lobby:{lobby_id}"))
        if lobby_json is not None:
            lobby_obj = json.loads(lobby_json.decode('utf-8'))
            lobby_state = LobbyState.deserialize(lobby_obj)
            # Remove player from list
            lobby_state.players = list(filter(
                lambda player: player.name != self.name_with_discrim,
                lobby_state.players
            ))
            # Send to redis and notify
            self._edit_and_publish_lobby_state(lobby_state)

    @property
    def state(self):
        return self._state

    @property
    def name_with_discrim(self):
        if not self.user_name or not self.user_discrim:
            return None
        return f"{self.user_name}#{self.user_discrim}"

    def upgrade(self, new_state: st.State):
        if not new_state.can_upgrade_from(self.state):
            print(f"Failed to upgrade a connection, state={self.state} cannot upgrade to state={new_state}")
            return
        old_state = self._state
        self._state = new_state
        self._handle_state_change(old_state, new_state)

    def downgrade(self, new_state: st.State):
        if not self.state.can_upgrade_from(new_state):
            print(f"Failed to downgrade a connection, state={self.state} cannot downgrade to state={new_state}")
            return
        old_state = self._state
        self._state = new_state
        self._handle_state_change(old_state, new_state)

    def _handle_state_change(self, old_state: st.State, new_state: st.State):
        if new_state == st.LOBBY_LIST or new_state == st.LOBBY_VIEW and self._handler_lobby_list is None:
            # Subscribe to lobby list updates
            self._handler_lobby_list = self.host.redis_channel_sub(
                channels.CHANNEL_LOBBY_LIST,
                handler=self._handle_lobby_list_update()
            )

    def _handle_lobby_list_update(self):
        def _handler(message):
            if message["type"] != "message":
                return

            lobby_json = message["data"].decode("utf-8")
            lobby_obj = json.loads(lobby_json)
            serialize_clean = LobbyState.deserialize(lobby_obj).serialize()
            asyncio.new_event_loop().run_until_complete(
                self.send(LobbyUpdateListMessage(lobbies=[serialize_clean]))
            )

        return _handler

    def _edit_and_publish_lobby_state(self, lobby: LobbyState):
        lobby_state_json = json.dumps(lobby.serialize())
        # Send to redis and notify
        self.host.redis().pipeline() \
            .set(namespaced(f"lobby:{lobby.lobby_id}"), lobby_state_json) \
            .publish(channels.CHANNEL_LOBBY_LIST, lobby_state_json) \
            .execute()
