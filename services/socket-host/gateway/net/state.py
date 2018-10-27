from common.net.state import State

HS_UNIDENTIFIED = State(0)  # The user has not attempted to identify themselves
HS_USER_PROMPTING = State(1, HS_UNIDENTIFIED)  # The user does not exist, and is being created
HS_IDENTIFIED = State(2, HS_UNIDENTIFIED, HS_USER_PROMPTING)  # The client has identified the client

LOBBY_INIT = State(3, HS_IDENTIFIED)  # The server has upgraded the connection to lobby, and is waiting for action
LOBBY_LIST = State(4, LOBBY_INIT)  # The client is waiting for a list of lobbies
LOBBY_VIEW = State(5, LOBBY_INIT, LOBBY_LIST)  # The client is in a lobby

TRANSFERRED = State(6, LOBBY_VIEW)  # Final state, client has completed their contract
