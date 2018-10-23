import json

import websockets
from game.net.handshake.identify import HandshakeIdentifyMessage
from game.net.message import InboundMessage, OutboundMessage


class PlayerConnection:
    def __init__(self, websocket: websockets.WebSocketServerProtocol, session_token: str):
        self.websocket = websocket
        self.session_token = session_token

    async def send(self, message: OutboundMessage):
        if self.websocket.closed:
            return

        build = message.build(self.session_token)
        output = json.dumps(build)
        await self.websocket.send(output)

    def on_receive(self, message: InboundMessage):
        if isinstance(message, HandshakeIdentifyMessage):
            message: HandshakeIdentifyMessage = message
            print(f"Received identification: {message.token}")
