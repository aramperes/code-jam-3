from typing import Any, Dict

from common.net.message import InboundMessage


class DeliveryIdentifyMessage(InboundMessage):
    def __init__(self, raw_data: str):
        self.track_token: str = None
        super().__init__(raw_data)

    def parse_payload(self, payload: Dict[str, Any]):
        self.track_token = payload.get("track_token")
