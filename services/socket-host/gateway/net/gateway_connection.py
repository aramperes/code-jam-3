import asyncio
import json
import random
import secrets
import time
import uuid

import websockets
from common.namespace import namespaced
from common.net.connection import CommonSocketConnection
from common.net.message import InboundMessage
from gateway import GatewayHost, channels
from gateway.lobby import LobbyState, LobbyUser
from gateway.net import state as st, validator
from gateway.net.handshake.identify import HandshakeIdentifyMessage
from gateway.net.handshake.new_user import HandshakeNewUserMessage
from gateway.net.handshake.prompt_new_user import HandshakePromptNewUserMessage
from gateway.net.handshake.upgrade import HandshakeUpgradeMessage
from gateway.net.handshake.user_info import HandshakeUserInfoMessage
from gateway.net.lobby.chat import LobbyChatMessage
from gateway.net.lobby.chat_broadcast import LobbyChatBroadcastMessage
from gateway.net.lobby.config import LobbyConfigMessage
from gateway.net.lobby.config_response import LobbyConfigResponseMessage
from gateway.net.lobby.join_response import LobbyJoinResponseMessage
from gateway.net.lobby.quit import LobbyQuitMessage
from gateway.net.lobby.set_state import LobbySetStateMessage
from gateway.net.lobby.update_list import LobbyUpdateListMessage
from gateway.net.lobby.user_ready import LobbyUserReadyMessage


class GatewayConnection(CommonSocketConnection):
    def __init__(self, host: GatewayHost, websocket: websockets.WebSocketServerProtocol, session_token: str):
        super().__init__(host, websocket, session_token)

        self._user_creation_transaction = None
        self.user_token: str = None
        self.user_name: str = None
        self.user_discrim: str = None

        self.current_lobby_id = None
        self._handler_lobby_list = None
        self._handler_lobby_chat = None

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
                self._view_lobby(lobby_id)
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
                await self.send(
                    LobbyJoinResponseMessage(lobby_id=lobby_id, joined=True)
                )
                self._view_lobby(lobby_id)
                return

        if self.state == st.LOBBY_VIEW:
            if isinstance(message, LobbyChatMessage):
                message: LobbyChatMessage = message
                # todo: sanitize message (?)
                # send to redis channel for the current lobby
                channel = channels.lobby_chat(self.current_lobby_id)
                self.host.redis().publish(
                    channel,
                    json.dumps({
                        "user_name": self.name_with_discrim,
                        "message": message.message
                    })
                )
                return

            if isinstance(message, LobbyUserReadyMessage):
                message: LobbyUserReadyMessage = message
                lobby_state_json = self.host.redis().get(namespaced(f"lobby:{self.current_lobby_id}"))
                lobby_state_json = lobby_state_json.decode("utf-8")
                lobby_state = LobbyState.deserialize(json.loads(lobby_state_json))

                for player_obj in lobby_state.players:
                    if player_obj.name == self.name_with_discrim:
                        player_obj.ready = message.ready
                        break
                self._edit_and_publish_lobby_state(lobby_state)
                return

            if isinstance(message, LobbyQuitMessage):
                message: LobbyQuitMessage = message
                self._leave_lobby(self.current_lobby_id)
                self.downgrade(st.LOBBY_LIST)
                return

        print(f"Received a message unknown message or invalid state, state={self.state.state_id}, op={message.op}")

    def cleanup(self):
        # session death

        # remove pubsub handlers
        if self._handler_lobby_list is not None:
            self.host.redis_channel_unsub(self._handler_lobby_list)

        # remove self from current lobby
        if self.current_lobby_id is not None:
            self._leave_lobby(self.current_lobby_id)
            self.current_lobby_id = None

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
            # Unsubscribe from chat
            if self._handler_lobby_chat:
                self.host.redis_channel_unsub(self._handler_lobby_chat)

    def _view_lobby(self, lobby_id: str):
        self.upgrade(st.LOBBY_VIEW)
        self.current_lobby_id = lobby_id
        # Subscribe to chat
        self._handler_lobby_chat = self.host.redis_channel_sub(
            channels.lobby_chat(lobby_id),
            self._handle_lobby_chat()
        )

    @property
    def name_with_discrim(self):
        if not self.user_name or not self.user_discrim:
            return None
        return f"{self.user_name}#{self.user_discrim}"

    def handle_state_change(self, old_state: st.State, new_state: st.State):
        if (new_state == st.LOBBY_LIST or new_state == st.LOBBY_VIEW) and self._handler_lobby_list is None:
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

    def _handle_lobby_chat(self):
        def _handler(payload):
            if payload["type"] != "message":
                return
            chat_data_json = payload["data"].decode("utf-8")
            chat_data = json.loads(chat_data_json)
            broadcast_message = LobbyChatBroadcastMessage(
                user_name=chat_data.get("user_name"),
                message=chat_data.get("message", "")
            )
            asyncio.new_event_loop().run_until_complete(
                self.send(broadcast_message)
            )

        return _handler

    def _edit_and_publish_lobby_state(self, lobby: LobbyState):
        lobby_state_json = json.dumps(lobby.serialize())
        # Send to redis and notify
        self.host.redis().pipeline() \
            .set(namespaced(f"lobby:{lobby.lobby_id}"), lobby_state_json) \
            .publish(channels.CHANNEL_LOBBY_LIST, lobby_state_json) \
            .execute()
