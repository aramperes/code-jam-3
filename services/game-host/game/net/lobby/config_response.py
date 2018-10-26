from game.net.message import OutboundMessage


class LobbyConfigResponseMessage(OutboundMessage):
    def __init__(self, lobby_id: str = None, error: str = None):
        super().__init__("lobby:config_response")
        self.lobby_id = lobby_id
        self.error = error

    def payload(self):
        payload = {
            "lobby_id": self.lobby_id
        }
        if self.error is not None:
            payload["error"] = self.error

        return payload
