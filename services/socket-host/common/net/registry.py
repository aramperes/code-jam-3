from typing import Dict, Type

from common.net.message import InboundMessage


class BaseInboundRegistry:
    def __init__(self):
        self._registry_map: Dict[str, Type[InboundMessage]] = {}

    def register(self, opcode: str, message_type: Type[InboundMessage]):
        self._registry_map[opcode] = message_type

    def get(self, opcode):
        return self._registry_map.get(opcode)
