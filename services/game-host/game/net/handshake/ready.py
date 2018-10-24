from game.net.message import OutboundMessage


class HandshakeReadyMessage(OutboundMessage):
    def __init__(self):
        super().__init__("handshake:ready")
