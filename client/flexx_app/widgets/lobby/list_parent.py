from flexx import flx

from flexx_app.widgets.lobby.config_menu import LobbyConfigMenuWidget
from flexx_app.widgets.lobby.list_item import LobbyListElementWidget


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
                self.join_directly_button = flx.Button(text="Join directly...")
                self.create_button = flx.Button(text="Create")

            with flx.Widget(style={"display": "none"}) as self.create_action_button_group:
                self.create_confirm_button = flx.Button(text="Create")
                self.create_cancel_button = flx.Button(text="Cancel")

        with flx.Widget(style={
            "border": "solid 2px black",
            "border-top": "none",
            "padding": "10px"
        }) as self.menu_container:
            with flx.Widget() as self.lobby_list_container:
                self.lobby_list_loading = flx.Label(text="Searching for lobbies...",
                                                    style={"text-align": "center",
                                                           "font-style": "italic",
                                                           "min-height": "0px",
                                                           "padding": "15px"})

    def _open_create_menu(self):
        self.list_action_button_group.apply_style({"display": "none"})
        self.create_action_button_group.apply_style({"display": "block"})
        self.lobby_title.set_text("Create new lobby")
        self.title_username.apply_style({"display": "none"})
        self.lobby_list_container.apply_style({"display": "none"})

        self.create_menu = LobbyConfigMenuWidget(parent=self.menu_container, client=self.client)

    def _cancel_create_menu(self):
        self.list_action_button_group.apply_style({"display": "block"})
        self.create_action_button_group.apply_style({"display": "none"})
        self.lobby_title.set_text("Lobbies")
        self.title_username.apply_style({"display": "block"})
        self.lobby_list_container.apply_style({"display": "block"})

        self.create_menu.dispose()

    def _populate_lobby_list(self):
        def _sort_key(lobby_obj):
            return lobby_obj["created_time"]

        cache = sorted(self.lobby_cache, key=_sort_key)
        print(cache)

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
                                                      lobby=lobby_obj)
                self.lobby_cache[lobby_obj["id"]]["_widget"] = lobby_widget
                if self.lobby_list_loading:
                    self.lobby_list_loading.dispose()
                    self.lobby_list_loading = None

    @flx.reaction("create_cancel_button.pointer_click")
    def _create_cancel_button_handler(self, *events):
        self._cancel_create_menu()

    @flx.reaction("create_button.pointer_click")
    def _list_create_button_handler(self, *events):
        self._open_create_menu()

    def update_list(self, lobbies):
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
