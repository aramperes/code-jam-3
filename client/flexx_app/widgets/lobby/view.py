from flexx import flx


class LobbyViewWidget(flx.Widget):
    client = flx.AnyProp()
    lobby_id = flx.AnyProp()

    def init(self):
        flx.Label(text="<Lobby: " + self.lobby_id + ">")
