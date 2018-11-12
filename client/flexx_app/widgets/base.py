from flexx import flx, event

from flexx_app.client import Client
from flexx_app.widgets.game.game_canvas import GameCanvasWidget
from flexx_app.widgets.loading_info import LoadingInfoWidget
from flexx_app.widgets.lobby.list_parent import LobbyListParentWidget
from flexx_app.widgets.username_prompt import UsernamePromptWidget


class BaseWidget(flx.Widget):
    ws_url = event.StringProp("", doc="Websocket URL")

    def init(self):
        self.apply_style({
            "width": "80%",
            "max-width": "800px",
            "padding-top": "50px",
            "margin-left": "auto",
            "margin-right": "auto"
        })

        self.game_title = flx.Label(text="- DeathWatch -", style={
            "text-align": "center",
            "width": "100%",
            "font-size": "16pt"
        })
        self.loading_info = LoadingInfoWidget(visible=True)

        self.client = Client(self.ws_url, self)
        self.canvas = None

    def set_loading_status(self, status):
        self.loading_info.set_status(status)
        self.loading_info.show()

    def hide_loading_status(self):
        self.loading_info.hide()

    def show_username_prompt(self):
        if not self.username_prompt:
            self.username_prompt = UsernamePromptWidget(parent=self, client=self.client)
        self.enable_username_prompt()
        self.clear_username_prompt()

    def disable_username_prompt(self):
        if self.username_prompt:
            self.username_prompt.disable()

    def enable_username_prompt(self):
        if self.username_prompt:
            self.username_prompt.enable()

    def remove_username_prompt(self):
        if self.username_prompt:
            self.username_prompt.dispose()

    def clear_username_prompt(self):
        if self.username_prompt:
            self.username_prompt.clear()

    def show_lobby_list(self):
        if not self.lobby_parent:
            self.lobby_parent = LobbyListParentWidget(parent=self, client=self.client)

    def lobby_config_show_error(self, error):
        if self.lobby_parent:
            self.lobby_parent.config_show_error(error)

    def lobby_config_success(self, lobby_id):
        if self.lobby_parent:
            self.lobby_parent.confirm_config_edit(lobby_id)

    def create_canvas(self):
        self.canvas = GameCanvasWidget(parent=self, client=self.client)
