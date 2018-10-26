from flexx import flx


class LobbyConfigMenuWidget(flx.Widget):
    client = flx.Property()

    def init(self):
        with flx.Widget(style={
            "text-align": "center",
            "margin-bottom": "20px"
        }):
            flx.Label(text="Presets:")
            with flx.Widget():
                self.preset_button_1 = flx.Button(text="Singleplayer")
                self.preset_button_2 = flx.Button(text="2-player co-op")
                self.preset_button_3 = flx.Button(text="3-player co-op")

        with flx.Widget(style={
            "display": "flex",
            "justify-content": "space-evenly"
        }):
            with flx.Widget():
                flx.Label(text="Lobby name:")
                self.name_field = flx.LineEdit()

            with flx.Widget():
                flx.Label(text="Players (1-3):")
                self.playercount_field = flx.LineEdit()

        with flx.Widget(style={
            "text-align": "center",
            "margin-top": "20px",
            "font-style": "italic"
        }):
            self.error_label = flx.Label(text="Lobby name must be between 2 and 35 characters.")

    @flx.reaction("preset_button_1.pointer_click")
    def _preset_button_1_handler(self, *events):
        self.load_preset(self.client.username + "'s solo game", "1")

    @flx.reaction("preset_button_2.pointer_click")
    def _preset_button_3_handler(self, *events):
        self.load_preset(self.client.username + "'s co-op game", "2")

    @flx.reaction("preset_button_3.pointer_click")
    def _preset_button_2_handler(self, *events):
        self.load_preset(self.client.username + "'s co-op game", "3")

    def load_preset(self, name, players):
        self.name_field.set_text(name)
        self.playercount_field.set_text(players)

    def set_disabled_all(self, disabled):
        self.name_field.set_disabled(disabled)
        self.playercount_field.set_disabled(disabled)
        self.preset_button_1.set_disabled(disabled)
        self.preset_button_2.set_disabled(disabled)
        self.preset_button_3.set_disabled(disabled)
