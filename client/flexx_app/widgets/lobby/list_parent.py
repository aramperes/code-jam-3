from flexx import flx

from flexx_app.widgets.lobby.config_menu import LobbyConfigMenuWidget
from flexx_app.widgets.lobby.list_item import LobbyListElementWidget
from flexx_app.widgets.lobby.view import LobbyViewWidget


class LobbyListParentWidget(flx.Widget):
    client = flx.Property()

    def init(self):
        self.lobby_cache = {}

        with flx.Widget(style={
            "width": "100%",
            "padding": "10px",
            "border": "solid 2px black",
            "display": "flex",
            "align-items": "center",
            "justify-content": "space-between"
        }):
            with flx.Widget():
                self.lobby_title = flx.Label(text="Lobbies",
                                             style={"font-size": "14pt"})
                self.title_username = flx.Label(html="Welcome, <strong>" + self.client.username + "</strong>",
                                                style={"font-size": "10pt", "min-height": "0px"})
            with flx.Widget() as self.list_action_button_group:
                # self.join_directly_button = flx.Button(text="Join directly...")
                self.create_button = flx.Button(text="Create")

            with flx.Widget(style={"display": "none"}) as self.create_action_button_group:
                self.create_confirm_button = flx.Button(text="Create")
                self.create_cancel_button = flx.Button(text="Cancel")

        with flx.Widget(style={
            "border": "solid 2px black",
            "border-top": "none",
            "padding": "10px"
        }) as self.menu_container:
            with flx.Widget(style={
                "display": "grid",
                "grid-gap": "10px",
                "max-height": "400px",
                "overflow-y": 'auto'
            }) as self.lobby_list_container:
                self.lobby_list_loading = flx.Label(text="Searching for lobbies...",
                                                    style={"text-align": "center",
                                                           "font-style": "italic",
                                                           "min-height": "0px",
                                                           "padding": "15px"})

    def _open_create_menu(self):
        self.create_action_button_group.apply_style({"display": "block"})
        self.lobby_title.set_text("Create new lobby")

        self.create_menu = LobbyConfigMenuWidget(parent=self.menu_container, client=self.client)

    def _cancel_create_menu(self):
        if not self.create_menu:
            return
        self.create_action_button_group.apply_style({"display": "none"})
        self.create_menu.dispose()
        self.create_menu = None

    def _show_list_ui(self):
        self.list_action_button_group.apply_style({"display": "block"})
        self.lobby_title.set_text("Lobbies")
        self.title_username.apply_style({"display": "block"})
        self.lobby_list_container.apply_style({"display": "grid"})

    def _hide_list_ui(self):
        self.list_action_button_group.apply_style({"display": "none"})
        self.title_username.apply_style({"display": "none"})
        self.lobby_list_container.apply_style({"display": "none"})

    def _show_view_ui(self, lobby_id):
        lobby_obj = self.lobby_cache.get(lobby_id)
        self.lobby_view = LobbyViewWidget(client=self.client, lobby_id=lobby_id, parent=self.menu_container,
                                          cached_lobby_obj=lobby_obj)
        self._update_view_lobby_title()

    def _close_view_ui(self):
        if not self.lobby_view:
            return
        self.lobby_view.dispose()
        self.lobby_view = None

    def _populate_lobby_list(self):
        def _sort_key(lobby_obj):
            return lobby_obj["created_time"]

        cache = sorted(self.lobby_cache, key=_sort_key)

        for lobby_id in cache:
            lobby_obj = self.lobby_cache[lobby_id]
            if lobby_obj["_widget"] == None and lobby_obj["open"] == False:
                # if no widget and not open, we don't care
                continue
            if lobby_obj["_widget"] != None:
                # lobby that was already painted
                lobby_widget = lobby_obj["_widget"]
                if lobby_obj["open"] == False:
                    # lobby is no longer open, delete
                    lobby_widget.dispose()
                    continue
                else:
                    # update existing widget
                    lobby_widget.update_lobby(lobby_obj)
                    continue
            else:
                # new lobby! make a widget
                lobby_widget = LobbyListElementWidget(parent=self.lobby_list_container, list_parent=self,
                                                      lobby=lobby_obj, client=self.client)
                self.lobby_cache[lobby_obj["id"]]["_widget"] = lobby_widget
                if self.lobby_list_loading:
                    self.lobby_list_loading.dispose()
                    self.lobby_list_loading = None

    @flx.reaction("create_cancel_button.pointer_click")
    def _create_cancel_button_handler(self, *events):
        self._cancel_create_menu()
        self._show_list_ui()

    @flx.reaction("create_confirm_button.pointer_click")
    def _create_confirm_button_handler(self, *events):
        self._create_buttons_disabled(True)
        self.client.send("lobby:config", {
            "name": self.create_menu.name_field.text,
            "max_players": int(self.create_menu.playercount_field.text),
            "lobby_id": None
        })

    @flx.reaction("create_button.pointer_click")
    def _list_create_button_handler(self, *events):
        self._hide_list_ui()
        self._open_create_menu()

    def config_show_error(self, error):
        if error:
            self.create_menu.error_label.set_text("Error: " + str(error))
        else:
            self.create_menu.error_label.set_text("Error: could not create lobby.")

        self.create_menu.error_label.apply_style({"color": "red"})
        self._create_buttons_disabled(False)

    def confirm_config_edit(self, lobby_id):
        self._cancel_create_menu()

    def _create_buttons_disabled(self, disabled):
        self.create_confirm_button.set_disabled(disabled)
        self.create_cancel_button.set_disabled(disabled)
        self.create_menu.set_disabled_all(disabled)

    def _update_view_lobby_title(self):
        if not self.lobby_view:
            return

        if self.lobby_cache.get(self.client.current_lobby_id):
            self.lobby_title.set_text("\"" + self.lobby_cache.get(self.client.current_lobby_id)["name"] + "\"")

    @flx.reaction("client.lobby_list_update")
    def _on_update_list(self, *events):
        event = events[-1]
        if event is None:
            return
        lobbies = event["lobbies"]
        if len(lobbies) == 0:
            return

        for lobby_obj_remote in lobbies:
            if "id" in lobby_obj_remote:
                lobby_widget = None
                if lobby_obj_remote["id"] in self.lobby_cache:
                    lobby_widget = self.lobby_cache[lobby_obj_remote["id"]]["_widget"]
                lobby_obj_remote["_widget"] = lobby_widget
                self.lobby_cache[lobby_obj_remote["id"]] = lobby_obj_remote

        self._populate_lobby_list()
        self._update_view_lobby_title()

    @flx.reaction("client.on_lobby_join")
    def _on_lobby_join(self, *events):
        event = events[-1]
        if event is None:
            return
        lobby_id = event["lobby_id"]
        self._cancel_create_menu()
        self._hide_list_ui()
        self._show_view_ui(lobby_id)

    @flx.reaction("client.on_lobby_leave")
    def _on_lobby_leave(self, *events):
        # todo
        print("Going back to lobby list")
