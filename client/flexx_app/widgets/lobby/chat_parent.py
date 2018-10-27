from flexx import flx


class ChatMessage(flx.Widget):
    user_name = flx.StringProp()
    chat_message = flx.StringProp()
    is_self = flx.BoolProp()

    def init(self):
        flx.Label(
            text=self._get_text(), style={"font-size": "10pt"}
        )

    def _get_text(self):
        text = self.user_name
        if self.is_self:
            text += " (You)"
        text += ": " + self.chat_message
        return text


class LobbyChatParentWidget(flx.Widget):
    client = flx.AnyProp()

    def init(self):
        self.apply_style({
            "display": "flex",
            "height": "100%",
            "flex-direction": "column"
        })

        self.history_container = flx.Widget(style={
            "flex-grow": "1",
            "margin-bottom": "10px",
            "overflow-y": "auto"
        })
        self.chat_field = flx.LineEdit(placeholder_text="Chat (Enter to submit)", style={
            "width": "99%"
        })

    @flx.reaction("client.on_lobby_chat")
    def _on_chat_receive(self, *events):
        for event in events:
            user_name = event["user_name"]
            chat_message = event["chat_message"]
            is_self = (user_name == self.client.username)
            print(chat_message, user_name, is_self)
            ChatMessage(
                parent=self.history_container,
                user_name=user_name,
                chat_message=chat_message,
                is_self=is_self
            )

    @flx.reaction("chat_field.submit")
    def _on_chat_submit(self, *events):
        chat_message = self.chat_field.text
        self.chat_field.set_text("")
        if len(chat_message.strip()) == 0:
            return
        self.client.send("lobby:chat", {
            "message": chat_message
        })
