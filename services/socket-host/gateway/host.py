import asyncio
import json
import threading
import time

import redis
import websockets
from common.host import CommonServerHost
from common.namespace import namespaced
from common.net.connection import CommonSocketConnection
from gateway import channels
from gateway.net import state
from gateway.net.handshake.ready import HandshakeReadyMessage
from gateway.net.lobby.transfer import LobbyTransferMessage
from gateway.net.registry import INBOUND_REGISTRY


class GatewayHost(CommonServerHost):

    def __init__(self, host: str, port: int, redis_pool: redis.ConnectionPool, transfer_url: str):
        super().__init__(host, port, redis_pool, INBOUND_REGISTRY)
        self._transfer_url = transfer_url

        from gateway.net.player_connection import PlayerConnection
        self._PlayerConnectionType = PlayerConnection

    async def post_handle_new_connection(self, connection):
        await connection.send(
            HandshakeReadyMessage(server_time=int(time.time()))
        )

    def create_socket_connection_object(self, websocket: websockets.WebSocketServerProtocol, session_token: str):
        return self._PlayerConnectionType(
            host=self,
            websocket=websocket,
            session_token=session_token
        )

    def handle_redis_init(self):
        self._redis_pubsub_connection.subscribe(namespaced("channel:dummy"))
        self._init_lobby_cleanup_job()

    def _init_lobby_cleanup_job(self):
        open_index = namespaced("lobby_open_index")

        # Pubsub handler that updates the "open" lobby list for faster indexing,
        # as well as cleaning up empty lobbies
        def handle_lobby_update(message):
            if message["type"] != "message":
                return
            lobby_json = message["data"].decode("utf-8")
            lobby_obj = json.loads(lobby_json)
            lobby_is_open = bool(lobby_obj["open"])
            lobby_id = lobby_obj["id"]

            # check if lobby state in redis
            redis_lobby_state = bool(self.redis().sismember(
                open_index,
                lobby_id
            ))
            if lobby_is_open != redis_lobby_state:
                # something changed
                if lobby_is_open:
                    # add to set
                    self.redis().sadd(open_index, lobby_id)  # sadd :(
                else:
                    # remove from set
                    self.redis().srem(open_index, lobby_id)

            # check if lobby is empty
            if len(lobby_obj["players"]) == 0:
                self.redis().delete(namespaced(f"lobby:{lobby_id}"))
                return

            # check if all players are ready
            if len(lobby_obj["players"]) == lobby_obj["max_players"]:
                all_ready = all([player["ready"] for player in lobby_obj["players"]])
                if all_ready:
                    # transfer all players to game host
                    with threading.Lock():
                        player_connections = set()
                        for player_conn in self._ws_connections.values():
                            if player_conn.current_lobby_id == lobby_id:
                                player_connections.add(player_conn)
                    for player_conn in player_connections:
                        self.transfer_to_game_host(player_conn)
                        print("Transferring", player_conn.name_with_discrim)

        self.redis_channel_sub(
            channels.CHANNEL_LOBBY_LIST,
            handler=handle_lobby_update
        )

    def transfer_to_game_host(self, connection: CommonSocketConnection):
        async def send_goodbye():
            # todo: make target URL configurable
            connection.upgrade(state.TRANSFERRED)
            await connection.send(LobbyTransferMessage(target=self._transfer_url, track_token="todo"))
            # At this point, the client cannot do anything except disconnect.

        asyncio.new_event_loop().run_until_complete(
            send_goodbye()
        )
