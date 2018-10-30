import websockets
from common.namespace import namespaced
from common.net.connection import CommonSocketConnection
from common.net.message import InboundMessage
from game import GameHost
from game.net import state as st
from game.net.delivery.identify import DeliveryIdentifyMessage
from game.net.delivery.upgrade import DeliveryUpgradeMessage
from game.net.delivery.waiting import DeliveryWaitingMessage


class GameConnection(CommonSocketConnection):

    def __init__(self, host: GameHost, websocket: websockets.WebSocketServerProtocol, session_token: str):
        super().__init__(host, websocket, session_token)
        self.username = None

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
                user_name_tentative = self.host.redis().get(namespaced(f"transfer:{message.track_token}"))
                if user_name_tentative:
                    self.username = user_name_tentative.decode("utf-8")
                    self.upgrade(st.DELIVERY_IDENTIFIED)
                    await self.send(DeliveryUpgradeMessage())
                    return
                else:
                    self.host.gateway_token_pending_map[message.track_token] = self.session_token
                    return
