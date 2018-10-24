from game.net.message import OutboundMessage


class LobbyUpdateListMessage(OutboundMessage):
    def __init__(self):
        super().__init__("lobby:update_list")

    def payload(self):
        return {
            "lobbies": [
                # todo: encode lobby object
            ]
        }
