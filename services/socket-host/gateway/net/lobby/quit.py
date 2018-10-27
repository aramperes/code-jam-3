from common.net.message import InboundMessage


class LobbyQuitMessage(InboundMessage):
    def __init__(self, raw_data: str):
        super().__init__(raw_data)
