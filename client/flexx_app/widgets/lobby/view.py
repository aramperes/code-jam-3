from flexx import flx

from flexx_app.widgets.lobby.chat_parent import LobbyChatParentWidget
from flexx_app.widgets.lobby.player_list_parent import LobbyPlayerListParentWidget


class LobbyViewWidget(flx.Widget):
    client = flx.AnyProp()
    lobby_id = flx.AnyProp()
    cached_lobby_obj = flx.AnyProp()
    is_ready = flx.BoolProp(False)

    def init(self):
        self.apply_style({
            "height": "400px",
            "display": "flex"
        })

        with flx.Widget(style={
            "display": "flex",
            "height": "100%",
            "flex-direction": "column"
        }):
            with flx.Widget(style={
                "height": "100%",
                "width": "250px",
                "border": "solid 1px black",
                "flex-grow": "1",
                "margin-bottom": "10px",
            }):
                self.player_list_parent = LobbyPlayerListParentWidget(client=self.client,
                                                                      cached_lobby_obj=self.cached_lobby_obj)
            with flx.Widget(style={
                "display": "flex",
                "flex-direction": "row",
                "padding-bottom": "2px"
            }):
                self.ready_button = flx.Button(text="Ready", style={"font-weight": "bold"})
                self.quit_button = flx.Button(text="Quit")

        with flx.Widget(style={
            "height": "100%",
            "flex-grow": "1",
            "margin-left": "10px"
        }):
            LobbyChatParentWidget(client=self.client)
        if self.cached_lobby_obj:
            self._update_lobby_view(self.cached_lobby_obj)

    def _update_lobby_view(self, lobby_obj):
        # self.lobby_id_label.set_text("ID: " + lobby_obj["id"])
        pass

    @flx.reaction("client.current_lobby_update")
    def _on_current_lobby_update(self, *events):
        event = events[-1]
        if not event:
            return
        lobby_obj = event["lobby_obj"]
        self._update_lobby_view(lobby_obj)

    @flx.action
    def set_ready(self, ready):
        self._mutate_is_ready(ready)
        # Announce it to the world!
        self.client.send("lobby:user_ready", {
            "ready": ready
        })
        if ready:
            self.ready_button.set_text("Un-Ready")
        else:
            self.ready_button.set_text("Ready")

    @flx.reaction("ready_button.pointer_click")
    def _on_ready_button_toggle(self, *events):
        if self.is_ready == True:
            self.set_ready(False)
        else:
            self.set_ready(True)

    @flx.reaction("quit_button.pointer_click")
    def _on_quit_button_click(self, *events):
        self.client.quit_lobby()
