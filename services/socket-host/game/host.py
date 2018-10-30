import asyncio
import json

import redis
import websockets
from common import channels
from common.host import CommonServerHost
from game.net import state
from game.net.delivery.ready import DeliveryReadyMessage
from game.net.delivery.upgrade import DeliveryUpgradeMessage
from game.net.registry import INBOUND_REGISTRY


class GameHost(CommonServerHost):

    def __init__(self, host: str, port: int, redis_pool: redis.ConnectionPool):
        super().__init__(host, port, redis_pool, INBOUND_REGISTRY)

        from game.net.game_connection import GameConnection
        self._GameConnectionType = GameConnection

        self.gateway_token_pending_map = {}

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
            if transfer_gateway_token in self.gateway_token_pending_map:
                session_token = self.gateway_token_pending_map[transfer_gateway_token]
                del self.gateway_token_pending_map[transfer_gateway_token]
                connection = self._ws_connections.get(session_token)
                if not connection:
                    return
                connection.username = transfer_username
                connection.upgrade(state.DELIVERY_IDENTIFIED)
                # send upgrade
                asyncio.new_event_loop().run_until_complete(
                    connection.send(
                        DeliveryUpgradeMessage()
                    )
                )

        return _handler
