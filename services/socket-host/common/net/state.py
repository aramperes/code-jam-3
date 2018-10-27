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
