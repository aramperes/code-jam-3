from flexx import flx

from flexx_app import http


class ExampleButtons(flx.Widget):
    def init(self):
        http.load_jquery()
        self.test_button = flx.Button(text='Click me!')

    @flx.reaction('test_button.pointer_click')
    def test_clicked(self, *events):
        http.call_http("GET", "/game/", self.handle_callback_game)

    def handle_callback_game(self, x):
        version = x["version"]
        print("Remote version: " + str(version))


app = flx.App(ExampleButtons)
