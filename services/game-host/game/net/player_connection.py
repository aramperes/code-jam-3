import json
import secrets

import websockets

from game.net import state
from game.net.handshake.identify import HandshakeIdentifyMessage
from game.net.handshake.new_user import HandshakeNewUserMessage
from game.net.handshake.prompt_new_user import HandshakePromptNewUserMessage
from game.net.handshake.upgrade import HandshakeUpgradeMessage
from game.net.handshake.user_info import HandshakeUserInfoMessage
from game.net.message import InboundMessage, OutboundMessage
from game.net.state import State


class PlayerConnection:
    def __init__(self, websocket: websockets.WebSocketServerProtocol, session_token: str):
        self.websocket = websocket
        self.session_token = session_token
        self._state = state.HS_UNIDENTIFIED
        self._user_creation_transaction = None

    async def send(self, message: OutboundMessage):
        if self.websocket.closed:
            return

        build = message.build(self.session_token)
        output = json.dumps(build)
        await self.websocket.send(output)

    async def on_receive(self, message: InboundMessage):
        if self.state == state.HS_UNIDENTIFIED:
            if isinstance(message, HandshakeIdentifyMessage):
                message: HandshakeIdentifyMessage = message

                # todo: check if identification is valid. simply reject for now
                self._user_creation_transaction = secrets.token_urlsafe(32)
                self.upgrade(state.HS_USER_PROMPTING)
                await self.send(
                    HandshakePromptNewUserMessage(
                        transaction_id=self._user_creation_transaction
                    )
                )
                return
        if self.state is state.HS_USER_PROMPTING:
            if isinstance(message, HandshakeNewUserMessage):
                message: HandshakeNewUserMessage = message
                if not self._user_creation_transaction or message.transaction_id != self._user_creation_transaction:
                    # unknown/unexpected transaction
                    return

                self._user_creation_transaction = None
                # todo: check if the username is allowed. simply allow for now
                self.upgrade(state.HS_IDENTIFIED)
                await self.send(
                    HandshakeUserInfoMessage(
                        user_id="abc",
                        user_name="test"
                    )
                )
                self.upgrade(state.LOBBY_INIT)
                await self.send(
                    HandshakeUpgradeMessage()
                )

    @property
    def state(self):
        return self._state

    def upgrade(self, new_state: State):
        if not new_state.can_upgrade_from(self.state):
            print(f"Failed to upgrade a connection, state={self.state} cannot upgrade to state={new_state}")
            return
        self._state = new_state
