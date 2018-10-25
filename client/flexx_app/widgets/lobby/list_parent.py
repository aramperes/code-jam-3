from flexx import flx


class LobbyListParentWidget(flx.Widget):
    client = flx.Property()

    def init(self):
        with flx.Widget(style={
            "width": "100%",
            "padding": "10px",
            "border": "solid 2px black",
            "display": "flex",
            "align-items": "center",
            "justify-content": "space-between"
        }):
            with flx.Widget():
                self.title_lobbies = flx.Label(text="Lobbies",
                                               style={"font-size": "14pt"})
                self.title_username = flx.Label(html="Welcome, <strong>" + self.client.username + "</strong>",
                                                style={"font-size": "10pt", "min-height": "0px"})
            with flx.Widget():
                self.join_directly_button = flx.Button(text="Join directly...")
                self.create_button = flx.Button(text="Create")

    def update_list(self, lobbies):
        print(lobbies)
