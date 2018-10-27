from common.net.message import OutboundMessage


class LobbyJoinResponseMessage(OutboundMessage):
    def __init__(self, lobby_id: str, joined: bool):
        super().__init__("lobby:join_response")
        self.lobby_id = lobby_id
        self.joined = joined

    def payload(self):
        return {
            "lobby_id": self.lobby_id,
            "joined": self.joined
        }
