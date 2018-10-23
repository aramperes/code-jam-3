from game.net.message import OutboundMessage


class HandshakePromptNewUserMessage(OutboundMessage):
    def __init__(self, transaction_id: str):
        super().__init__("handshake:prompt_new_user")
        self.transaction_id = transaction_id

    def payload(self):
        return {
            "transaction_id": self.transaction_id
        }
