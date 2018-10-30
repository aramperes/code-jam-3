from common.net.message import OutboundMessage


class DeliveryUpgradeMessage(OutboundMessage):
    def __init__(self):
        super().__init__("delivery:upgrade")
