from common.net.message import OutboundMessage


class LobbyChatBroadcastMessage(OutboundMessage):
    def __init__(self, user_name: str, message: str):
        super().__init__("lobby:chat_broadcast")
        self.user_name = user_name
        self.message = message

    def payload(self):
        return {
            "user_name": self.user_name,
            "message": self.message
        }
