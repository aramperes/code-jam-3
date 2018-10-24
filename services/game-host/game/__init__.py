import os

import redis

from game.host import GameHost

redis_pool = redis.ConnectionPool(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    max_connections=10
)

game_host = GameHost(
    redis_pool=redis_pool,
    host=os.getenv("GAME_HOST", None),
    port=int(os.getenv("GAME_PORT", 5000))
)


def run():
    game_host.run()
