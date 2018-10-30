import asyncio
import json

import websockets
from common import channels
from common.namespace import namespaced
from common.net.connection import CommonSocketConnection
from common.net.message import InboundMessage
from game import GameHost
from game.net import state as st
from game.net.delivery.identify import DeliveryIdentifyMessage
from game.net.delivery.upgrade import DeliveryUpgradeMessage
from game.net.delivery.waiting import DeliveryWaitingMessage
from game.net.world.init import WorldInitMessage
from game.net.world.ready import WorldReadyMessage
from game.net.world.terrain import WorldTerrainMessage
from game.world.world import World


class GameConnection(CommonSocketConnection):

    def __init__(self, host: GameHost, websocket: websockets.WebSocketServerProtocol, session_token: str):
        super().__init__(host, websocket, session_token)
        self.host: GameHost = self.host
        self.username = None
        self.world_id = None

        self._handler_world_init = None
        self._handler_world_terrain = None
        self._handler_world_ready = None

    async def on_receive(self, message: InboundMessage):
        if self.state == st.DELIVERY_INIT:
            if message.op == "delivery:identify":
                await self.send(DeliveryWaitingMessage())
                message: DeliveryIdentifyMessage = message
                if message.track_token is None:
                    return
                if message.track_token in self.host.gateway_token_pending_map:
                    return

                # check in redis if it's already there
                transfer_json = self.host.redis().get(namespaced(f"transfer:{message.track_token}"))
                if transfer_json:
                    transfer_data = json.loads(transfer_json.decode("utf-8"))
                    transfer_username = transfer_data["username"]
                    transfer_lobby_id = transfer_data["lobby_id"]
                    self.username = transfer_username
                    self.upgrade(st.DELIVERY_IDENTIFIED)
                    self.init_redis_world_handlers(transfer_lobby_id)
                    await self.send(DeliveryUpgradeMessage())

                    self.host.check_world_init(transfer_lobby_id)
                    return
                else:
                    self.host.gateway_token_pending_map[message.track_token] = self.session_token
                    return

    def cleanup(self):
        if self._handler_world_init:
            self.host.redis_channel_unsub(self._handler_world_init)
        if self._handler_world_terrain:
            self.host.redis_channel_unsub(self._handler_world_terrain)
        if self._handler_world_ready:
            self.host.redis_channel_unsub(self._handler_world_ready)

    def _handle_world_init(self):
        def _handler(message):
            if message["type"] != "message":
                return

            asyncio.new_event_loop().run_until_complete(
                self.send(
                    WorldInitMessage(pieces=World.WORLD_PIECES, piece_size=World.WORLD_PIECE_SIZE)
                )
            )

        return _handler

    def _handle_world_terrain(self):
        def _handler(message):
            if message["type"] != "message":
                return
            asyncio.new_event_loop().run_until_complete(
                self.send(
                    WorldTerrainMessage(
                        data=json.loads(
                            message["data"].decode("utf-8")
                        )
                    )
                )
            )

        return _handler

    def _handle_world_ready(self):
        def _handler(message):
            if message["type"] != "message":
                return
            asyncio.new_event_loop().run_until_complete(
                self.send(
                    WorldReadyMessage()
                )
            )

        return _handler

    def init_redis_world_handlers(self, world_id):
        self._handler_world_init = self.host.redis_channel_sub(
            channels.world_init(world_id),
            handler=self._handle_world_init()
        )
        self._handler_world_terrain = self.host.redis_channel_sub(
            channels.world_terrain(world_id),
            handler=self._handle_world_terrain()
        )
        self._handler_world_ready = self.host.redis_channel_sub(
            channels.world_ready(world_id),
            handler=self._handle_world_ready()
        )
