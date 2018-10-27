from typing import Any, Dict

from common.net.message import InboundMessage


class HandshakeIdentifyMessage(InboundMessage):
    def __init__(self, raw_data: str):
        self.token = None
        super().__init__(raw_data)

    def parse_payload(self, payload: Dict[str, Any]):
        if payload.get("token") is not None:
            self.token = str(payload["token"])
