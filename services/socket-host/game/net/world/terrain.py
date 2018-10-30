from typing import Dict

from common.net.message import OutboundMessage


class WorldTerrainMessage(OutboundMessage):
    def __init__(self, data: Dict):
        super().__init__("world:terrain")
        self.data = data

    def payload(self):
        return self.data
