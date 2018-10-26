from flexx import flx


class LobbyViewWidget(flx.Widget):
    client = flx.AnyProp()
    lobby_id = flx.AnyProp()
    cached_lobby_obj = flx.AnyProp()

    def init(self):
        self.lobby_id_label = flx.Label()

        if self.cached_lobby_obj:
            self._update_lobby_view(self.cached_lobby_obj)

    @flx.reaction("client.lobby_list_update")
    def _lobby_list_update(self, *events):
        # Check if current lobby was updated
        event = events[-1]
        if event is None:
            return
        lobbies = event["lobbies"]
        for lobby in lobbies:
            if lobby["id"] == self.lobby_id:
                self._update_lobby_view(lobby)
                return

    def _update_lobby_view(self, lobby_obj):
        self.lobby_id_label.set_text("ID: " + lobby_obj["id"])
