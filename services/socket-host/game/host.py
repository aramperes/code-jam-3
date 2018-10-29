import redis
import websockets
from common.host import CommonServerHost
from game.net.registry import INBOUND_REGISTRY


class GameHost(CommonServerHost):

    def __init__(self, host: str, port: int, redis_pool: redis.ConnectionPool):
        super().__init__(host, port, redis_pool, INBOUND_REGISTRY)

    async def post_handle_new_connection(self, connection):
        # The game-host does not do anything on connection, it needs to wait for the
        # client to identify itself and for verification to be done.
        pass

    def create_socket_connection_object(self, websocket: websockets.WebSocketServerProtocol, session_token: str):
        # Since the game-host uses the client's old session token, the session_token param is temporary.
        # todo: GameConnection
        pass

    def handle_redis_init(self):
        # todo: handler for gateway-host identifications/transfers
        pass
