from typing import Any, Dict

from common.net.message import InboundMessage


class LobbyUserReadyMessage(InboundMessage):
    def __init__(self, raw_data: str):
        self.ready: bool = None
        super().__init__(raw_data)

    def parse_payload(self, payload: Dict[str, Any]):
        self.ready = bool(payload.get("ready", True))
