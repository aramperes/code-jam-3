from typing import Dict, Union

from common.net.message import OutboundMessage


class LobbyTransferMessage(OutboundMessage):
    def __init__(self, target: str, track_token: str):
        super().__init__("lobby:transfer")
        self.target = target
        self.track_token = track_token

    def payload(self) -> Union[None, Dict]:
        return {
            "target": self.target,
            "track_token": self.track_token
        }
