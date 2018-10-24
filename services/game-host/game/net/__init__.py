from typing import Dict, Type

from game.net.message import InboundMessage
from game.net.handshake.identify import HandshakeIdentifyMessage
from game.net.handshake.new_user import HandshakeNewUserMessage
from game.net.lobby.config import LobbyConfigMessage
from game.net.lobby.set_state import LobbySetStateMessage

INBOUND_REGISTRY: Dict[str, Type[InboundMessage]] = {
    "handshake:identify": HandshakeIdentifyMessage,
    "handshake:new_user": HandshakeNewUserMessage,

    "lobby:set_state": LobbySetStateMessage,
    "lobby:config": LobbyConfigMessage,
}
