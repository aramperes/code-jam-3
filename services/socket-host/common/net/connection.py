import json

import websockets
from common.host import CommonServerHost
from common.net.message import InboundMessage, OutboundMessage
from common.net.state import State


class CommonSocketConnection:
    def __init__(self, host: CommonServerHost, websocket: websockets.WebSocketServerProtocol, session_token: str):
        self.host = host
        self.websocket = websocket
        self.session_token = session_token
        self._state = State(0)

    # NETWORK LIFECYCLE #

    async def send(self, message: OutboundMessage):
        if self.websocket.closed:
            return

        build = message.build(self.session_token)
        output = json.dumps(build)
        await self.websocket.send(output)

    async def on_receive(self, message: InboundMessage):
        raise NotImplementedError()

    def cleanup(self):
        pass

    # STATE MANAGEMENT #

    @property
    def state(self):
        return self._state

    def upgrade(self, new_state: State):
        if not new_state.can_upgrade_from(self.state):
            print(f"Failed to upgrade a connection, state={self.state} cannot upgrade to state={new_state}")
            return
        old_state = self._state
        self._state = new_state
        self.handle_state_change(old_state, new_state)

    def downgrade(self, new_state: State):
        if not self.state.can_upgrade_from(new_state):
            print(f"Failed to downgrade a connection, state={self.state} cannot downgrade to state={new_state}")
            return
        old_state = self._state
        self._state = new_state
        self.handle_state_change(old_state, new_state)

    def handle_state_change(self, old_state: State, new_state: State):
        pass
