from typing import Dict, Type

from game.net.message import InboundMessage
from game.net.handshake.identify import HandshakeIdentifyMessage
from game.net.handshake.new_user import HandshakeNewUserMessage

INBOUND_REGISTRY: Dict[str, Type[InboundMessage]] = {
    "handshake:identify": HandshakeIdentifyMessage,
    "handshake:new_user": HandshakeNewUserMessage
}
