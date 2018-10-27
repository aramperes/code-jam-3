from typing import Any, Dict

from common.net.message import InboundMessage


class HandshakeNewUserMessage(InboundMessage):
    def __init__(self, raw_data: str):
        self.transaction_id = None
        self.user_name = None
        super().__init__(raw_data)

    def parse_payload(self, payload: Dict[str, Any]):
        if "transaction_id" in payload:
            self.transaction_id = str(payload["transaction_id"])

        if "name" in payload:
            self.user_name = str(payload["name"])
