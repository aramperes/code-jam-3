from common.net.message import OutboundMessage


class DeliveryWaitingMessage(OutboundMessage):
    def __init__(self):
        super().__init__("delivery:waiting")
