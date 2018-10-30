import asyncio
import json
import random
from threading import Thread

import redis
import websockets
from common import channels
from common.host import CommonServerHost
from common.namespace import namespaced
from game.net import state
from game.net.delivery.ready import DeliveryReadyMessage
from game.net.delivery.upgrade import DeliveryUpgradeMessage
from game.net.registry import INBOUND_REGISTRY
from game.world import terrain
from game.world.world import World


class GameHost(CommonServerHost):

    def __init__(self, host: str, port: int, redis_pool: redis.ConnectionPool):
        super().__init__(host, port, redis_pool, INBOUND_REGISTRY)

        from game.net.game_connection import GameConnection
        self._GameConnectionType = GameConnection

        self.gateway_token_pending_map = {}  # track_token: session_token
        self.player_world_connection_count = {}  # world_id: count

    async def post_handle_new_connection(self, connection):
        await connection.send(
            DeliveryReadyMessage()
        )

    def create_socket_connection_object(self, websocket: websockets.WebSocketServerProtocol, session_token: str):
        return self._GameConnectionType(
            self,
            websocket,
            session_token
        )

    def get_world_by_id(self, world_id):
        world_data_json = self.redis().get(namespaced(f"world:{world_id}"))
        if world_data_json is None:
            # create world from id
            lobby_data_json = self.redis().get(namespaced(f"lobby:{world_id}"))
            if not lobby_data_json:
                return None
            lobby_data_json = lobby_data_json.decode("utf-8")
            lobby_data = json.loads(lobby_data_json)
            player_count = int(lobby_data["max_players"])
            terrain_seed = random.randrange(-10000, 10000)
            world = World(
                world_id, player_count, terrain_seed
            )
            self.redis().set(namespaced(f"world:{world_id}"), json.dumps(world.serialize()))
            return world

        world_data = json.loads(world_data_json.decode("utf-8"))
        return World.deserialize(world_data)

    def handle_redis_init(self):
        self.redis_channel_sub(
            channel=channels.CHANNEL_TRANSFER,
            handler=self._handle_transfer()
        )

    def _handle_transfer(self):
        def _handler(message):
            if message["type"] != "message":
                return
            transfer_json = message["data"].decode("utf-8")
            transfer_data = json.loads(transfer_json)
            transfer_gateway_token = transfer_data["track_token"]
            transfer_username = transfer_data["username"]
            transfer_lobby_id = transfer_data["lobby_id"]
            if transfer_gateway_token not in self.gateway_token_pending_map:
                return
            session_token = self.gateway_token_pending_map[transfer_gateway_token]
            del self.gateway_token_pending_map[transfer_gateway_token]
            connection = self._ws_connections.get(session_token)
            if not connection:
                return
            connection.username = transfer_username
            connection.world_id = transfer_lobby_id
            connection.init_redis_world_handlers()

            connection.upgrade(state.DELIVERY_IDENTIFIED)
            # send upgrade
            asyncio.new_event_loop().run_until_complete(
                connection.send(
                    DeliveryUpgradeMessage()
                )
            )
            self.check_world_init(transfer_lobby_id)

        return _handler

    def check_world_init(self, world_id):
        if world_id in self.player_world_connection_count:
            self.player_world_connection_count[world_id] += 1
        else:
            self.player_world_connection_count[world_id] = 1

        world = self.get_world_by_id(world_id)
        if world.player_count == self.player_world_connection_count[world_id]:
            # all players loaded, start init
            self._start_world_init(world)

    def _start_world_init(self, world):
        world_id = world.world_id
        self.redis().publish(channels.world_init(world_id), ".")

        # start thread to generate terrain
        thread = Thread(target=self.generate_terrain_handler(world))
        thread.start()

    def generate_terrain_handler(self, world: World):
        def _generate():
            for piece_x in range(World.WORLD_PIECES):
                for piece_y in range(World.WORLD_PIECES):
                    piece_terrain = []
                    piece_features = []
                    for piece_tile_x in range(World.WORLD_PIECE_SIZE):
                        for piece_tile_y in range(World.WORLD_PIECE_SIZE):
                            tile_x = piece_x * World.WORLD_PIECE_SIZE + piece_tile_x
                            tile_y = piece_y * World.WORLD_PIECE_SIZE + piece_tile_y
                            seed = world.terrain_seed
                            terrain_data, feature_data = terrain.tile_terrain(
                                tile_x,
                                tile_y,
                                seed,
                                World.WORLD_SIZE,
                                50
                            )
                            piece_terrain.append(terrain_data)
                            piece_features.append(feature_data)
                    piece_payload = {
                        "piece": {"x": piece_x, "y": piece_y},
                        "terrain": piece_terrain,
                        "features": piece_features
                    }
                    self.redis().publish(channels.world_terrain(world.world_id), json.dumps(piece_payload))

            self.redis().publish(channels.world_ready(world.world_id), "")

        return _generate
