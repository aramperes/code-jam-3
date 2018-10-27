from typing import Any, Dict

from common.net.message import InboundMessage


class LobbyConfigMessage(InboundMessage):
    def __init__(self, raw_data: str):
        self.name: str = None
        self.max_players: int = None
        self.lobby_id: str = None
        super().__init__(raw_data)

    def parse_payload(self, payload: Dict[str, Any]):
        self.name = payload.get("name")
        self.max_players = payload.get("max_players")
        self.lobby_id = payload.get("lobby_id")
