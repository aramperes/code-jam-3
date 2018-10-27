import os

import redis
from gateway.host import GatewayHost

redis_pool = redis.ConnectionPool(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    max_connections=10
)

gateway_host = GatewayHost(
    redis_pool=redis_pool,
    host=os.getenv("GATEWAY_HOST", None),
    port=int(os.getenv("GATEWAY_PORT", 5000)),
    transfer_url=os.getenv("GATEWAY_TRANSFER_TARGET", "ws://localhost:8080/game/")
)


def run():
    gateway_host.run()
