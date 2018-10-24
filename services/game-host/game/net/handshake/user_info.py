from game.net.message import OutboundMessage


class HandshakeUserInfoMessage(OutboundMessage):
    def __init__(self, user_token: str, user_name: str):
        super().__init__("handshake:user_info")
        self.user_token = user_token
        self.user_name = user_name

    def payload(self):
        return {
            "user": {
                "token": self.user_token,
                "name": self.user_name
            }
        }
