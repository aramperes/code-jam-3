import asyncio
import json
import os
import secrets
from concurrent.futures import ProcessPoolExecutor
from threading import Thread

import redis
import responder
import websockets


class GameHost:
    def __init__(self, api: responder.API, redis_pool: redis.ConnectionPool):
        self.api = api
        self.redis_pool = redis_pool

        self.process_pool = ProcessPoolExecutor(2)
        self._init_routes()

        thread = Thread(target=self._init_websocket_server)
        thread.start()

    def _init_websocket_server(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            websockets.serve(
                self._ws_loop(),
                host=os.getenv('WS_HOST', 'localhost'),
                port=int(os.getenv('WS_HOST', 6789))
            )
        )
        loop.run_forever()

    def _ws_loop(self):
        async def loop(websocket: websockets.WebSocketServerProtocol, path):
            session_token = secrets.token_urlsafe(64)
            print(f"New connection! Session token: {session_token}")

            handshake_ready = self._build_message(session_token, "handshake:ready", None)
            await websocket.send(handshake_ready)

            while True:
                try:
                    data = await websocket.recv()
                    print(data)
                except websockets.exceptions.ConnectionClosed:
                    print(f"Session died: {session_token}")
                    break

        return loop

    def _build_message(self, session: str, op: str, payload: object) -> str:
        return json.dumps({
            "session": session,
            "op": op,
            "payload": payload
        })

    def _init_routes(self):
        @self.api.route("/")
        async def index(req, resp):
            resp.media = {
                "version": "0.0.1",
                "about": "This is the game host. It manages the multiplayer feature of the game.",
                "team": "Possible Jeans"
            }
