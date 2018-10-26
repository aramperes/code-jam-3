from flexx import flx


class LobbyChatParentWidget(flx.Widget):
    client = flx.AnyProp()
    cached_lobby_obj = flx.AnyProp()

    def init(self):
        pass
