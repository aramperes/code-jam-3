from common.net.message import OutboundMessage


class WorldInitMessage(OutboundMessage):
    def __init__(self, pieces: int, piece_size: int):
        super().__init__("world:init")
        self.pieces = pieces
        self.piece_size = piece_size

    def payload(self):
        return {
            "terrain": {
                "pieces": self.pieces,
                "piece_size": self.piece_size
            }
        }
