import asyncio
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
from common.namespace import namespaced
from common.net.message import InboundMessage
from common.net.registry import BaseInboundRegistry
from common.redis_handler import RedisChannelReceipt


class CommonServerHost:
    """
    WebSocket + redis server.
    """

    def __init__(self, host: str, port: int, redis_pool: redis.ConnectionPool, inbound_registry: BaseInboundRegistry):
        self._ws_host = host
        self._ws_port = port
        self._redis_pool = redis_pool
        self._inbound_registry = inbound_registry

        from common.net.connection import CommonSocketConnection
        self._ws_connections: Dict[str, CommonSocketConnection] = {}

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
                    message = self._inbound_registry.get(op_code)(data)

                    await connection.on_receive(message)
                except websockets.exceptions.ConnectionClosed:
                    print(f"Session died: {connection.session_token}")
                    connection.cleanup()
                    del self._ws_connections[connection.session_token]
                    break

        return loop

    async def _ws_init_connection(self, websocket: websockets.WebSocketServerProtocol):
        session_token = secrets.token_urlsafe(64)
        socket_connection = self.create_socket_connection_object(websocket, session_token)
        print(f"New connection! Session token: {session_token}")
        await self.post_handle_new_connection(socket_connection)
        return socket_connection

    async def post_handle_new_connection(self, connection):
        pass

    def create_socket_connection_object(self, websocket: websockets.WebSocketServerProtocol, session_token: str):
        raise NotImplementedError()

    def redis(self):
        return redis.Redis(connection_pool=self._redis_pool)

    def _init_redis_pubsub(self):
        thread = Thread(target=self._redis_pubsub_loop)
        thread.start()

    def handle_redis_init(self):
        pass

    def _redis_pubsub_loop(self):
        redis_connection = self.redis()
        self._redis_pubsub_connection = redis_connection.pubsub()
        self._redis_pubsub_connection.subscribe(namespaced("channel:dummy"))
        self.handle_redis_init()

        while self._redis_thread_kill_queue.empty():
            message = self._redis_pubsub_connection.get_message(timeout=0.05)
            if not message:
                continue
            channel = message["channel"].decode("utf-8")
            with threading.Lock():
                receipts_for = set(self._redis_channels[channel])
                for handler in receipts_for:
                    handler: RedisChannelReceipt = handler
                    handler.func.__call__(message)

    def redis_channel_sub(self, channel: str, handler) -> RedisChannelReceipt:
        receipt = RedisChannelReceipt(handler, channel)
        if len(self._redis_channels[channel]) == 0:
            self._redis_pubsub_connection.subscribe(channel)
        self._redis_channels[channel].add(receipt)
        return receipt

    def redis_channel_unsub(self, receipt: RedisChannelReceipt):
        channel = receipt.channel
        self._redis_channels[channel].remove(receipt)
        if len(self._redis_channels[channel]) == 0:
            self._redis_pubsub_connection.unsubscribe(channel)

    def _signal_handler(self):
        def handler(*args):
            self._redis_thread_kill_queue.put(0)
            sys.exit(0)

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
