from common.net.registry import BaseInboundRegistry
from gateway.net.handshake.identify import HandshakeIdentifyMessage
from gateway.net.handshake.new_user import HandshakeNewUserMessage
from gateway.net.lobby.chat import LobbyChatMessage
from gateway.net.lobby.config import LobbyConfigMessage
from gateway.net.lobby.quit import LobbyQuitMessage
from gateway.net.lobby.set_state import LobbySetStateMessage
from gateway.net.lobby.user_ready import LobbyUserReadyMessage

INBOUND_REGISTRY = BaseInboundRegistry()
INBOUND_REGISTRY.register("handshake:identify", HandshakeIdentifyMessage)
INBOUND_REGISTRY.register("handshake:new_user", HandshakeNewUserMessage)

INBOUND_REGISTRY.register("lobby:set_state", LobbySetStateMessage)
INBOUND_REGISTRY.register("lobby:config", LobbyConfigMessage)
INBOUND_REGISTRY.register("lobby:chat", LobbyChatMessage)
INBOUND_REGISTRY.register("lobby:user_ready", LobbyUserReadyMessage)
INBOUND_REGISTRY.register("lobby:quit", LobbyQuitMessage)
