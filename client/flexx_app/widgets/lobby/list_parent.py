from flexx import flx

from flexx_app.widgets.lobby.config_menu import LobbyConfigMenuWidget


class LobbyListParentWidget(flx.Widget):
    client = flx.Property()

    def init(self):
        self.lobby_cache = []

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

        self.menu_container = flx.Widget(style={
            "border": "solid 2px black",
            "border-top": "none",
            "padding": "10px"
        })

    def _open_create_menu(self):
        self.list_action_button_group.apply_style({"display": "none"})
        self.create_action_button_group.apply_style({"display": "block"})
        self.lobby_title.set_text("Create new lobby")
        self.title_username.apply_style({"display": "none"})

        self.create_menu = LobbyConfigMenuWidget(parent=self.menu_container, client=self.client)

    def _cancel_create_menu(self):
        self.list_action_button_group.apply_style({"display": "block"})
        self.create_action_button_group.apply_style({"display": "none"})
        self.lobby_title.set_text("Lobbies")
        self.title_username.apply_style({"display": "block"})

        self.create_menu.dispose()

    @flx.reaction("create_cancel_button.pointer_click")
    def _create_cancel_button_handler(self, *events):
        self._cancel_create_menu()

    @flx.reaction("create_button.pointer_click")
    def _list_create_button_handler(self, *events):
        self._open_create_menu()

    def update_list(self, lobbies):
        print(lobbies)
