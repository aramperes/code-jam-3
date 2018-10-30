from typing import Dict


class World:
    WORLD_PIECES = 25  # amount of pieces per dimension (width or height)
    WORLD_PIECE_SIZE = 10  # amount of tiles per piece per dimension
    WORLD_SIZE = WORLD_PIECES * WORLD_PIECE_SIZE  # amount of tiles per dimension

    def __init__(self, world_id: str, player_count: int, terrain_seed: int):
        self.world_id = world_id
        self.player_count = player_count
        self.terrain_seed = terrain_seed

    def serialize(self):
        return {
            "id": self.world_id,
            "player_count": self.player_count,
            "terrain_seed": self.terrain_seed
        }

    @staticmethod
    def deserialize(obj: Dict):
        return World(
            world_id=obj["id"],
            player_count=obj["player_count"],
            terrain_seed=obj["terrain_seed"]
        )
