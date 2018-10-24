import asyncio
import secrets
from typing import Dict

import redis
import websockets
from game.net import INBOUND_REGISTRY
from game.net.handshake.ready import HandshakeReadyMessage
from game.net.message import InboundMessage
from game.net.player_connection import PlayerConnection


class GameHost:
    def __init__(self, host: str, port: int, redis_pool: redis.ConnectionPool):
        self._ws_host = host
        self._ws_port = port
        self.redis_pool = redis_pool
        self._ws_connections: Dict[str, PlayerConnection] = {}

        self._init_websocket_server()

    def _init_websocket_server(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            websockets.serve(
                self._ws_loop(),
                host=self._ws_host,
                port=self._ws_port
            )
        )
        loop.run_forever()

    def _ws_loop(self):
        async def loop(websocket: websockets.WebSocketServerProtocol, path):
            connection = await self._ws_init_connection(websocket)
            self._ws_connections[connection.session_token] = connection

            while True:
                try:
                    data = await websocket.recv()
                    message = InboundMessage(data)
                    op_code = message.op
                    message = INBOUND_REGISTRY[op_code](data)

                    await connection.on_receive(message)
                except websockets.exceptions.ConnectionClosed:
                    print(f"Session died: {connection.session_token}")
                    del self._ws_connections[connection.session_token]
                    break

        return loop

    async def _ws_init_connection(self, websocket: websockets.WebSocketServerProtocol) -> PlayerConnection:
        session_token = secrets.token_urlsafe(64)
        player_connection = PlayerConnection(
            websocket=websocket,
            session_token=session_token
        )
        print(f"New connection! Session token: {session_token}")
        await player_connection.send(HandshakeReadyMessage())
        return player_connection
