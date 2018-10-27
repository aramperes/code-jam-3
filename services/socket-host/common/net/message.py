import json
from typing import Any, Dict, Union


class Message:
    def __init__(self, op: str, payload: Union[None, Dict]):
        self._op = op
        self._payload = payload

    @property
    def payload(self) -> Union[None, Dict]:
        return self._payload

    @property
    def op(self) -> str:
        return self._op


class OutboundMessage(Message):
    def __init__(self, op: str):
        super().__init__(op, None)

    def payload(self) -> Union[None, Dict]:
        return None

    def build(self, session_token: str) -> Dict[str, Any]:
        return {
            "op": self._op,
            "session": session_token,
            "payload": self.payload()
        }


class InboundMessage(Message):
    def __init__(self, raw_data: str):
        self._raw_data = raw_data

        frame = self._parse_frame()
        super().__init__(frame["op"], self._payload)

    def _parse_frame(self) -> Dict[str, Any]:
        frame = json.loads(self._raw_data)
        if frame["payload"] is not None:
            self._payload = self.parse_payload(frame["payload"])
        return frame

    def parse_payload(self, payload: Dict[str, Any]):
        pass
