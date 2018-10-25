from typing import Dict, List

from game.net.message import OutboundMessage


class LobbyUpdateListMessage(OutboundMessage):
    def __init__(self, lobbies: List[Dict]):
        super().__init__("lobby:update_list")
        self.lobbies = lobbies

    def payload(self):
        return {
            "lobbies": self.lobbies
        }
