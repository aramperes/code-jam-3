from flexx import flx, event

from flexx_app.widgets import css_visible


class LoadingInfoWidget(flx.Widget):
    visible = event.BoolProp(True)

    def init(self):
        css_visible(self, self.visible)
        self.status_label = flx.Label(text="Connecting to game server...")

    def set_status(self, status: str):
        self.status_label.set_text(status)

    def hide(self):
        css_visible(self, False)

    def show(self):
        css_visible(self, True)
