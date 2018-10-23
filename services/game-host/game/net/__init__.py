from typing import Dict, Type

from game.net.handshake.identify import HandshakeIdentifyMessage
from game.net.message import InboundMessage

INBOUND_REGISTRY: Dict[str, Type[InboundMessage]] = {
    "handshake:identify": HandshakeIdentifyMessage
}
