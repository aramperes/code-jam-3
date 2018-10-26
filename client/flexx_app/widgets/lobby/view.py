from flexx import flx

from flexx_app.widgets.lobby.player_list_parent import LobbyPlayerListParentWidget


class LobbyViewWidget(flx.Widget):
    client = flx.AnyProp()
    lobby_id = flx.AnyProp()
    cached_lobby_obj = flx.AnyProp()

    def init(self):
        self.apply_style({
            "height": "400px"
        })

        with flx.Widget(style={
            "height": "100%",
            "width": "250px",
            "border": "solid 1px black"
        }):
            self.player_list_parent = LobbyPlayerListParentWidget(client=self.client,
                                                                  cached_lobby_obj=self.cached_lobby_obj)

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
