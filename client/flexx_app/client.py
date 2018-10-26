from flexx import flx
from pscript.stubs import JSON

from flexx_app import ws, storage, timer


class Client(flx.Component):
    lobby_join_request = flx.AnyProp()
    current_lobby_id = flx.AnyProp()

    def __init__(self, ws_url, base, *init_args, **property_values):
        super().__init__(*init_args, **property_values)
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

                # get time
                server_time = int(payload["server_time"])
                timer.DESYNC = timer.calculate_desync(server_time)
                timer.start_task_update_timers()

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
                return

            if op == "lobby:update_list":
                # update lobby list
                lobbies = payload["lobbies"]
                self.lobby_list_update(lobbies)
                return

            if op == "lobby:config_response":
                # if there is an error, show error
                # if no error, show lobby view
                error = payload["error"]
                lobby_id = payload["lobby_id"]
                if bool(error) or lobby_id is None:
                    self.base.lobby_config_show_error(error)
                else:
                    is_new_lobby = self.current_lobby_id is None
                    self.base.lobby_config_success(lobby_id)
                    if is_new_lobby:
                        self.__set_current_lobby_id(lobby_id)
                return

            if op == "lobby:join_response":
                joined = payload["joined"]
                lobby_id = payload["lobby_id"]

                if self.lobby_join_request != lobby_id:
                    # Different request
                    return

                if joined:
                    self.__set_current_lobby_id(lobby_id)

                # Clear the request
                self.set_lobby_join_request(None)

        return call

    @flx.action
    def set_lobby_join_request(self, lobby_id):
        self._mutate_lobby_join_request(lobby_id)
        self.lobby_join_request_update(lobby_id)

    @flx.emitter
    def lobby_join_request_update(self, new_lobby):
        return dict(new_lobby=new_lobby)

    @flx.emitter
    def lobby_list_update(self, lobbies):
        return dict(lobbies=lobbies)

    @flx.emitter
    def current_lobby_update(self, lobby_obj):
        return dict(lobby_obj=lobby_obj)

    @flx.action
    def __set_current_lobby_id(self, lobby_id):
        self._mutate_current_lobby_id(lobby_id)
        if lobby_id is not None:
            self.on_lobby_join(lobby_id)
        else:
            self.on_lobby_leave(lobby_id)

    @flx.emitter
    def on_lobby_join(self, lobby_id):
        return dict(lobby_id=lobby_id)

    @flx.emitter
    def on_lobby_leave(self):
        return dict()

    @flx.reaction("lobby_list_update")
    def __on_lobby_list_update_current(self, *events):
        event = events[-1]
        if not event:
            return
        lobbies = event["lobbies"]
        if lobbies and self.current_lobby_id:
            for lobby_obj in lobbies:
                if lobby_obj["id"] == self.current_lobby_id:
                    self.current_lobby_update(lobby_obj)
                    break
