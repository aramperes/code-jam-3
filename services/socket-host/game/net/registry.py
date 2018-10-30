from common.net.registry import BaseInboundRegistry
from game.net.delivery.identify import DeliveryIdentifyMessage

INBOUND_REGISTRY = BaseInboundRegistry()
INBOUND_REGISTRY.register("delivery:identify", DeliveryIdentifyMessage)
