import asyncio
import json
import secrets
import signal
import sys
import threading
from collections import defaultdict
from queue import Queue
from threading import Thread
from typing import Dict

import redis
import websockets
from game import channels
from game.namespace import namespaced
from game.net import INBOUND_REGISTRY
from game.net.handshake.ready import HandshakeReadyMessage
from game.net.message import InboundMessage
from game.redis_handler import RedisChannelReceipt


class GameHost:

    def __init__(self, host: str, port: int, redis_pool: redis.ConnectionPool):
        self._ws_host = host
        self._ws_port = port
        self._redis_pool = redis_pool

        from game.net.player_connection import PlayerConnection
        self._PlayerConnectionType = PlayerConnection
        self._ws_connections: Dict[str, PlayerConnection] = {}

        self._redis_async_loop = None
        self._ws_async_loop = None

        self._redis_thread_kill_queue = Queue()
        self._signal_handler()

        self._redis_channels = defaultdict(set)
        self._redis_pubsub_connection = None

    def run(self):
        self._init_redis_pubsub()
        self._init_websocket_server()

    def _init_websocket_server(self):
        self._ws_async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._ws_async_loop)
        self._ws_async_loop.run_until_complete(
            websockets.serve(
                self._ws_loop(),
                host=self._ws_host,
                port=self._ws_port
            )
        )
        self._ws_async_loop.run_forever()

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
                    connection.cleanup()
                    del self._ws_connections[connection.session_token]
                    break

        return loop

    async def _ws_init_connection(self, websocket: websockets.WebSocketServerProtocol):
        session_token = secrets.token_urlsafe(64)
        player_connection = self._PlayerConnectionType(
            host=self,
            websocket=websocket,
            session_token=session_token
        )
        print(f"New connection! Session token: {session_token}")
        await player_connection.send(HandshakeReadyMessage())
        return player_connection

    def _init_redis_pubsub(self):
        thread = Thread(target=self._redis_pubsub_loop)
        thread.start()

    def _redis_pubsub_loop(self):
        redis_connection = self.redis()
        self._redis_pubsub_connection = redis_connection.pubsub()
        self._redis_pubsub_connection.subscribe(namespaced("channel:dummy"))
        self._init_lobby_cleanup_job()

        while self._redis_thread_kill_queue.empty():
            message = self._redis_pubsub_connection.get_message(timeout=0.05)
            if not message:
                continue
            channel = message["channel"].decode("utf-8")
            with threading.Lock():
                for handler in self._redis_channels[channel]:
                    handler: RedisChannelReceipt = handler
                    handler.func.__call__(message)

    def redis_channel_sub(self, channel: str, handler) -> RedisChannelReceipt:
        receipt = RedisChannelReceipt(handler, channel)
        self._redis_pubsub_connection.subscribe(channel)
        self._redis_channels[channel].add(receipt)
        return receipt

    def redis_channel_unsub(self, receipt: RedisChannelReceipt):
        channel = receipt.channel
        self._redis_channels[channel].remove(receipt)
        self._redis_pubsub_connection.unsubscribe(channel)

    def _signal_handler(self):
        def handler(*args):
            self._redis_thread_kill_queue.put(0)
            sys.exit(0)

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def redis(self):
        return redis.Redis(connection_pool=self._redis_pool)

    def _init_lobby_cleanup_job(self):
        open_index = namespaced("lobby_open_index")

        # Pubsub handler that updates the "open" lobby list for faster indexing
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

        self.redis_channel_sub(
            channels.CHANNEL_LOBBY_LIST,
            handler=handle_lobby_update
        )
