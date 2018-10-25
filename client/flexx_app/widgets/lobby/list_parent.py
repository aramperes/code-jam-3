from flexx import flx


class LobbyListParentWidget(flx.Widget):
    client = flx.Property()

    def init(self):
        self.title_username = flx.Label(text="Welcome, " + self.client.username)
