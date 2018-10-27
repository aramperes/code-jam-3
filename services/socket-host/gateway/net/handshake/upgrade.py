from common.net.message import OutboundMessage


class HandshakeUpgradeMessage(OutboundMessage):
    def __init__(self):
        super().__init__("handshake:upgrade")
