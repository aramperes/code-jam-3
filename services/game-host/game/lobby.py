from typing import Dict, List, Union


class LobbyUser:
    def __init__(self, name: str, ready: bool):
        self.name = name
        self.ready = ready

    def serialize(self):
        return {
            "name": self.name,
            "ready": self.ready
        }

    @staticmethod
    def deserialize(obj: Dict):
        return LobbyUser(
            obj.get("name", ""),
            obj.get("ready", False)
        )


class LobbyState:
    def __init__(self, lobby_id: str, name: str, created_time: int, start_time: Union[int, None], max_players: int,
                 players: List[LobbyUser]):
        self.lobby_id = lobby_id
        self.name = name
        self.created_time = created_time
        self.start_time = start_time
        self.max_players = max_players
        self.players = players

    @property
    def is_open(self) -> bool:
        return len(self.players) < self.max_players

    def serialize(self):
        return {
            "id": self.lobby_id,
            "name": self.name,
            "created_time": self.created_time,
            "start_time": self.start_time,
            "max_players": self.max_players,
            "open": self.is_open,
            "players": [player.serialize() for player in self.players]
        }

    @staticmethod
    def deserialize(obj: Dict):
        return LobbyState(
            lobby_id=obj["id"],
            name=obj.get("name", "(Lobby)"),
            created_time=obj["created_time"],
            start_time=obj.get("start_time", None),
            max_players=obj["max_players"],
            players=[LobbyUser.deserialize(player_obj) for player_obj in obj.get("players", [])]
        )
