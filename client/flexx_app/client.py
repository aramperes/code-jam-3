from pscript.stubs import JSON

from flexx_app import ws, storage


class Client:
    def __init__(self, ws_url, base):
        self.base = base
        # props
        self.session_token = None
        self._username_prompt_transaction = None

        self.socket = ws.create_websocket_connection(ws_url, self._ws_callback())

    def send(self, op, payload):
        print(" < " + op + " " + JSON.stringify(payload))
        self.socket.send(JSON.stringify({
            "op": op,
            "session": self.session_token,
            "payload": payload
        }))

    def _ws_callback(self):
        def call(msg):
            frame = JSON.parse(msg["data"])
            op = frame["op"]
            payload = frame["payload"]
            print(" > " + op + " " + JSON.stringify(payload))

            if op == "handshake:ready":
                token = None
                if storage.read_token() is not None:
                    token = str(storage.read_token())
                self.session_token = frame["session"]
                self.send("handshake:identify", {"token": token})
                self.base.set_loading_status("Authenticating...")
                return

            if op == "handshake:prompt_new_user":
                self.base.hide_loading_status()
                self._username_prompt_transaction = payload["transaction_id"]
                self.base.show_username_prompt()
                return

            if op == "handshake:user_info":
                self.username = payload["user"]["name"]
                self.token = payload["user"]["token"]

                storage.store_token(self.token)
                self.base.remove_username_prompt()
                self.base.hide_loading_status()
                return

            if op == "handshake:upgrade":
                # show lobby
                self.base.show_lobby_list()
                self.send("lobby:set_state", {
                    "state": "list"
                })

            if op == "lobby:update_list":
                # update lobby list
                lobbies = payload["lobbies"]
                self.base.update_lobby_list(lobbies)

            if op == "lobby:config_response":
                # if there is an error, show error
                # if no error, show lobby view
                error = payload["error"]
                lobby_id = payload["lobby_id"]
                if bool(error) or lobby_id is None:
                    self.base.lobby_config_show_error(error)
                else:
                    self.base.lobby_config_success(lobby_id)
        return call
