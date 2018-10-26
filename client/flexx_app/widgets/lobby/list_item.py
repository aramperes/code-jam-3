from flexx import flx

from flexx_app import timer


class LobbyListElementWidget(flx.Widget):
    list_parent = flx.Property()
    lobby = flx.Property()

    def init(self):
        self.client = self.list_parent.client
        self.apply_style({
            "border": "solid 1px gray",
            "padding": "10px"
        })

        self.lobby_name_field = flx.Label()
        self.lobby_players_field = flx.Label(style={
            "font-size": "10pt",
            "min-height": "0px"
        })

        self.update_lobby(self.lobby)

    def update_lobby(self, lobby):
        # creation time

        self.lobby_name_field.set_html(
            "<strong>" + lobby["name"] + "</strong> <i>(created <span class='timer-update'" +
            "timestamp='" + str(lobby["created_time"]) + "'>" + timer.get_human_delay(lobby["created_time"]) +
            "</span> ago, open)</i>"
        )

        self.lobby_players_field.set_html(
            "Players (" + str(len(lobby["players"])) + "/" + str(lobby["max_players"]) + "): " + ", ".join(
                [user.name for user in lobby["players"]])
        )
