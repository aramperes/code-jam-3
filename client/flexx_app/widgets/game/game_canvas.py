from flexx import flx, ui


class GameCanvasWidget(ui.CanvasWidget):
    client = flx.Property()

    def init(self):
        super().init()
        self.apply_style({"width": "800px", "height": "600px"})
