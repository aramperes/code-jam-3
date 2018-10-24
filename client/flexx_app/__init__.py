from flexx import flx
from pscript.stubs import JSON

from flexx_app import ws, storage

WS_URL = "ws://localhost:8080/game/"

class ExampleButtons(flx.Widget):
    def init(self):
        # props
        self.session_token = None
        self._username_prompt_transaction = None

        # UI
        self.status_label = flx.Label(text="Connecting to game server...")
        self.username_input = flx.LineEdit()
        self.username_input.apply_style({"visibility": "hidden"})

        self.username_input_submit = flx.Button(text='Submit')
        self.username_input_submit.apply_style({"visibility": "hidden"})

        # connect
        self.socket = ws.create_websocket_connection(WS_URL, self._ws_callback())
        # self.test_button = flx.Button(text='Click me!')

    @flx.reaction('username_input_submit.pointer_click')
    def username_input_submitted(self, *events):
        self.username_input_submit.set_disabled(True)
        self.username_input.set_disabled(True)
        self.send("handshake:new_user", {
            "transaction_id": self._username_prompt_transaction,
            "name": self.username_input.text
        })

    def send(self, op, payload):
        print(" < " + op)
        self.socket.send(JSON.stringify({
            "op": op,
            "session": self.session_token,
            "payload": payload
        }))

    def _ws_callback(self):
        def call(msg):
            frame = JSON.parse(msg["data"])
            op = frame["op"]
            print(" > " + op)
            payload = frame["payload"]

            if op == "handshake:ready":
                token = None
                if storage.read_token() is not None:
                    token = str(storage.read_token())
                self.session_token = frame["session"]
                self.send("handshake:identify", {"token": token})
                self.status_label.set_text("Authenticating...")
                return

            if op == "handshake:prompt_new_user":
                self._username_prompt_transaction = payload["transaction_id"]
                self.status_label.set_text("Please input a username:")
                self.username_input.set_text("")
                self.username_input.apply_style({"visibility": "visible"})
                self.username_input_submit.apply_style({"visibility": "visible"})
                return

            if op == "handshake:user_info":
                username = payload["user"]["name"]
                token = payload["user"]["token"]

                storage.store_token(token)

                self.username_input.apply_style({"visibility": "hidden"})
                self.username_input_submit.apply_style({"visibility": "hidden"})
                self.status_label.set_text("Welcome, " + username)
                return

        return call


app = flx.App(ExampleButtons)
