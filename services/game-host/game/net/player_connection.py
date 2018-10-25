import json
import random
import re
import secrets

import websockets
from game import GameHost
from game.net import state as st
from game.net.handshake.identify import HandshakeIdentifyMessage
from game.net.handshake.new_user import HandshakeNewUserMessage
from game.net.handshake.prompt_new_user import HandshakePromptNewUserMessage
from game.net.handshake.upgrade import HandshakeUpgradeMessage
from game.net.handshake.user_info import HandshakeUserInfoMessage
from game.net.lobby.set_state import LobbySetStateMessage
from game.net.lobby.update_list import LobbyUpdateListMessage
from game.net.message import InboundMessage, OutboundMessage

_USERNAME_PATTERN = re.compile(r"^[\w]{2,15}$")


def username_valid(username: str) -> bool:
    return bool(_USERNAME_PATTERN.fullmatch(username))


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

                if not token or not isinstance(token, str) or not redis.exists(self.host.namespaced(f"token:{token}")):
                    await self.reject_authentication()
                    return

                name_with_discrim = redis.get(self.host.namespaced(f"token:{token}")).decode("utf-8")
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
                if not username_valid(username):
                    await self.reject_authentication()
                    return

                redis = self.host.redis()
                # Generate discriminator (between 0001 and 9999, inclusive)
                while self.user_discrim is None:
                    discrim = str(random.randint(1, 9999)).zfill(4)
                    if not redis.exists(self.host.namespaced(f"user_name:{username}#{discrim}")):
                        self.user_discrim = discrim

                self.user_name = username
                self.user_token = secrets.token_urlsafe(64)

                redis.pipeline() \
                    .set(self.host.namespaced(f"user_name:{self.name_with_discrim}"), self.user_token) \
                    .set(self.host.namespaced(f"token:{self.user_token}"), self.name_with_discrim) \
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
                    await self.send(LobbyUpdateListMessage(lobbies=[
                        {
                            "id": "1",
                            "name": "cool room",
                            "open": True,
                            "created_time": 0,
                            "start_time": None,
                            "max_players": 2,
                            "players": [
                                {
                                    "name": "notmomo#0001",
                                    "ready": True
                                }
                            ]
                        }
                    ]))
                    return

        print(f"Received a message unknown message or invalid state, state={self.state.state_id}, op={message.op}")

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
        self._state = new_state

    def downgrade(self, new_state: st.State):
        if not self.state.can_upgrade_from(new_state):
            print(f"Failed to downgrade a connection, state={self.state} cannot downgrade to state={new_state}")
            return
        self._state = new_state
