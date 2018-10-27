from flexx import flx


class PlayerItemWidget(flx.Widget):
    ready = flx.BoolProp()
    player_name = flx.StringProp()

    def init(self):
        self.apply_style({
            "border-bottom": "solid 1px black",
            "padding": "5px"
        })

        self.player_name_label = flx.Label(text=self.player_name, style={"font-size": "10pt"})
        self.ready_label = flx.Label(html=self._ready_label_html(), style={"font-size": "8pt", "min-height": "0px"})

    def _ready_label_html(self):
        if self.ready:
            return "<strong>Ready</strong>"
        else:
            return "Not ready"

    @flx.action
    def update_user(self, user_obj):
        self._mutate_ready(user_obj["ready"])
        self._mutate_player_name(user_obj["name"])

        self.player_name_label.set_text(self.player_name)
        self.ready_label.set_html(self._ready_label_html())


class LobbyPlayerListParentWidget(flx.Widget):
    client = flx.Property()
    cached_lobby_obj = flx.Property()

    def init(self):
        self.player_map = {}
        if self.cached_lobby_obj:
            self._update_lobby_view(self.cached_lobby_obj)

    def _update_lobby_view(self, lobby_obj):
        old_player_names = []
        for player_name in self.player_map:
            old_player_names.append(player_name)

        new_players = lobby_obj["players"]
        new_player_names = []
        for player_obj in new_players:
            player_name = player_obj["name"]
            new_player_names.append(player_name)
            player_ready = player_obj["ready"]

            if player_name in self.player_map:
                # widget already exists, update
                widget = self.player_map[player_name]
                widget.update_user(player_obj)
            else:
                # new user, create widget
                widget = PlayerItemWidget(parent=self, player_name=player_name, ready=player_ready)
                self.player_map[player_name] = widget

        # if a name is in the old player name, but not in the new players, delete the widget
        for old_name in old_player_names:
            if old_name not in new_player_names:
                old_widget = self.player_map[old_name]
                old_widget.dispose()
                self.player_map.pop(old_name)

    @flx.reaction("client.current_lobby_update")
    def _on_current_lobby_update(self, *events):
        event = events[-1]
        if not event:
            return
        lobby_obj = event["lobby_obj"]
        self._update_lobby_view(lobby_obj)
