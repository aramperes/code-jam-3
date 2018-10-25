class State:
    def __init__(self, state_id: int, *parents: 'State'):
        self.state_id = state_id
        self.parents = [state.state_id for state in parents]

    def can_upgrade_from(self, state) -> bool:
        return state.state_id in self.parents

    def __eq__(self, other):
        if isinstance(other, State):
            return self.state_id == other.state_id
        return False


# States

HS_UNIDENTIFIED = State(0)  # The user has not attempted to identify themselves
HS_USER_PROMPTING = State(1, HS_UNIDENTIFIED)  # The user does not exist, and is being created
HS_IDENTIFIED = State(2, HS_UNIDENTIFIED, HS_USER_PROMPTING)  # The client has identified the client

LOBBY_INIT = State(3, HS_IDENTIFIED)  # The server has upgraded the connection to lobby, and is waiting for action
LOBBY_LIST = State(4, LOBBY_INIT)  # The client is waiting for a list of lobbies
