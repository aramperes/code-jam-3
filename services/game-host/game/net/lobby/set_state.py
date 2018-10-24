from typing import Any, Dict

from game.net import InboundMessage


class LobbySetStateMessage(InboundMessage):
    def __init__(self, raw_data: str):
        self.state: str = None
        self.lobby_id: str = None

        super().__init__(raw_data)

    def parse_payload(self, payload: Dict[str, Any]):
        self.state = payload.get("state")
        self.lobby_id = payload.get("lobby_id")
