from typing import Dict, Union

from common.net.message import OutboundMessage


class HandshakeReadyMessage(OutboundMessage):
    def __init__(self, server_time: int):
        super().__init__("handshake:ready")
        self.server_time = server_time

    def payload(self) -> Union[None, Dict]:
        return {
            "server_time": self.server_time
        }
