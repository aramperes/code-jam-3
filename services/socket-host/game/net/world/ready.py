from common.net.message import OutboundMessage


class WorldReadyMessage(OutboundMessage):
    def __init__(self):
        super().__init__("world:ready")
