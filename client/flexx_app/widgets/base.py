from flexx import flx, event

from flexx_app.client import Client
from flexx_app.widgets.loading_info import LoadingInfoWidget
from flexx_app.widgets.lobby.list_parent import LobbyListParentWidget
from flexx_app.widgets.username_prompt import UsernamePromptWidget


class BaseWidget(flx.Widget):
    ws_url = event.StringProp("", doc="Websocket URL")

    def init(self):
        self.client = Client(self.ws_url, self)
        # # UI
        # self.username_input = flx.LineEdit()
        # self.username_input.apply_style({"visibility": "hidden"})
        #
        # self.username_input_submit = flx.Button(text='Submit')
        # self.username_input_submit.apply_style({"visibility": "hidden"})

        # connect
        self.loading_info = LoadingInfoWidget(visible=True)

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
