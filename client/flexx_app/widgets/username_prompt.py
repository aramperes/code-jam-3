from flexx import flx


class UsernamePromptWidget(flx.Widget):
    client = flx.Property()

    def init(self):
        self.label = flx.Label(text="Please enter a new username: ")
        self.field = flx.LineEdit()
        self.submit = flx.Button(text="Submit")

    def enable(self):
        self.field.set_disabled(False)
        self.submit.set_disabled(False)

    def disable(self):
        self.field.set_disabled(True)
        self.submit.set_disabled(True)

    def clear(self):
        self.field.set_text("")

    @flx.reaction('submit.pointer_click')
    def _submitted(self, *events):
        self.disable()
        self.client.send("handshake:new_user", {
            "transaction_id": self.client._username_prompt_transaction,
            "name": self.field.text
        })
