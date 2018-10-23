from game.net.message import OutboundMessage


class HandshakeUserInfoMessage(OutboundMessage):
    def __init__(self, user_id: str, user_name: str):
        super().__init__("handshake:user_info")
        self.user_id = user_id
        self.user_name = user_name

    def payload(self):
        return {
            "user": {
                "id": self.user_id,
                "name": self.user_name
            }
        }
