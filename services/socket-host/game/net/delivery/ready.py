from common.net.message import OutboundMessage


class DeliveryReadyMessage(OutboundMessage):
    def __init__(self):
        super().__init__("delivery:ready")
