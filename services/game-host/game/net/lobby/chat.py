from typing import Dict

from game.net.message import InboundMessage


class LobbyChatMessage(InboundMessage):
    def __init__(self, raw_data: str):
        self.message: str = None
        super().__init__(raw_data)

    def parse_payload(self, payload: Dict):
        self.message = payload.get("message", "")
