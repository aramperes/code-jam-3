from flexx import flx

from flexx_app import timer


class LobbyListElementWidget(flx.Widget):
    list_parent = flx.Property()
    lobby = flx.Property()
    client = flx.Property()

    def init(self):
        self.apply_style({
            "display": "flex",
            "justify-content": "space-between"
        })

        with flx.Widget():
            self.apply_style({
                "border": "solid 1px gray",
                "padding": "10px"
            })

            self.lobby_name_field = flx.Label()
            self.lobby_players_field = flx.Label(style={
                "font-size": "10pt",
                "min-height": "0px"
            })

        self.join_button = flx.Button(text="Join")
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

    @flx.reaction("join_button.pointer_click")
    def _join_button_pointer_click(self, *events):
        self.join_button.set_text("Joining...")
        self.client.set_lobby_join_request(self.lobby["id"])
        self.client.send("lobby:set_state", {
            "state": "join",
            "lobby_id": self.lobby["id"]
        })

    @flx.reaction("client.lobby_join_request_update")
    def _handle_lobby_join_request_update(self, *events):
        event = events[-1]
        if not bool(event):
            return

        if event["new_lobby"] is None:
            # re-enable button
            self.join_button.set_text("Join")
            self.join_button.set_disabled(False)
            pass
        else:
            # disable button
            self.join_button.set_disabled(True)
            pass
