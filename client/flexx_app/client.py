from flexx import flx
from pscript.stubs import JSON, RawJS

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

        self.socket = ws.create_websocket_connection(ws_url, self._ws_gateway_callback())
        self.track_token = None

        self._piece_count = 0
        self._expected_piece_count = None

        self._world_terrain = None
        self._world_features = None
        self._world_piece_count = None
        self._world_piece_size = None

    def send(self, op, payload):
        print(" < " + op + " " + JSON.stringify(payload))
        self.socket.send(JSON.stringify({
            "op": op,
            "session": self.session_token,
            "payload": payload
        }))

    def _ws_gateway_callback(self):
        def call(msg):
            print(" > " + msg["data"])
            frame = JSON.parse(msg["data"])
            op = frame["op"]
            payload = frame["payload"]

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
                return

            if op == "lobby:chat_broadcast":
                user_name = payload["user_name"]
                chat_message = payload["message"]
                self.on_lobby_chat(dict(user_name=user_name, chat_message=chat_message))
                return

            if op == "lobby:transfer":
                target_url = payload["target"]
                track_token = payload["track_token"]
                self.transfer_to(target_url, track_token)
                return

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

    def quit_lobby(self):
        if self.current_lobby_id:
            self.send("lobby:quit", {})
            self.__set_current_lobby_id(None)

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

    @flx.emitter
    def on_lobby_chat(self, message):
        return message

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

    def _ws_game_callback(self):
        def call(msg):
            frame = JSON.parse(msg["data"])
            op = frame["op"]
            payload = frame["payload"]
            print(" > " + op + " " + JSON.stringify(payload))

            if op == "delivery:ready":
                self.session_token = frame["session"]

                # send track token
                self.send("delivery:identify", {"track_token": self.track_token})
                return

            if op == "delivery:waiting":
                self.base.set_loading_status("Waiting for game host identification...")
                return

            if op == "delivery:upgrade":
                self.base.set_loading_status("Connected to game host, waiting for world...")
                return

            if op == "world:init":
                self._expected_piece_count = payload["terrain"]["pieces"] ** 2
                self._world_piece_count = payload["terrain"]["pieces"]
                self._world_piece_size = payload["terrain"]["piece_size"]

                self._world_terrain = []
                self._world_features = []
                world_dim = self._world_piece_count * self._world_piece_size

                for x in range(0, world_dim):
                    self._world_terrain.append([None] * world_dim)
                    self._world_features.append([None] * world_dim)

                self.base.set_loading_status("Loading terrain (0%)...")
                return

            if op == "world:terrain":
                piece_x = payload["piece"]["x"]
                piece_y = payload["piece"]["y"]
                base_tile_x = self._world_piece_size * piece_x
                base_tile_y = self._world_piece_size * piece_y

                payload_index = 0
                for tile_x_rel in range(0, self._world_piece_size):
                    for tile_y_rel in range(0, self._world_piece_size):
                        tile_x = tile_x_rel + base_tile_x
                        tile_y = tile_y_rel + base_tile_y

                        self._world_terrain[tile_x][tile_y] = payload["terrain"][payload_index]
                        self._world_features[tile_x][tile_y] = payload["features"][payload_index]
                        payload_index += 1

                self._piece_count += 1
                loading_percentage = self._piece_count / self._expected_piece_count * 100
                loading_percentage = RawJS("Math.round(loading_percentage);")
                self.base.set_loading_status("Loading terrain (" + str(loading_percentage) + "%)...")
                return

            if op == "world:ready":
                client_instance = self
                RawJS("window['client_instance'] = client_instance;")
                self.base.create_canvas()

                RawJS(
                    """
                    var script = document.createElement('script');script.src='/static/client.js';
                    
                    script.onload = function() {
                        let handle = setInterval(function() {
                            if (document.getElementsByTagName("canvas").length > 0) {
                                clearInterval(handle);
                                window["run_pixi_app"]();
                            }
                        }, 5);
                    }
                    
                    document.head.appendChild(script);
                    """
                )

        return call

    def transfer_to(self, url, track_token):
        self.track_token = track_token
        self.base.lobby_parent.dispose()
        self.base.lobby_parent = None

        self.base.set_loading_status("Transferring to game host...")

        self.socket.close()
        self.socket = ws.create_websocket_connection(url, self._ws_game_callback())
