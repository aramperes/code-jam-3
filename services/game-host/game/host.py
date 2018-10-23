import redis
import responder


class GameHost:
    def __init__(self, api: responder.API, redis_pool: redis.ConnectionPool):
        self.api = api
        self.redis_pool = redis_pool

        self._init_routes()

    def _init_routes(self):
        @self.api.route("/")
        async def index(req, resp):
            resp.media = {
                "version": "0.0.1",
                "about": "This is the game host. It manages the multiplayer feature of the game.",
                "team": "Possible Jeans"
            }
