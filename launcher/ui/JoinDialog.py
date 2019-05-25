import fsui


class JoinDialog(fsui.LegacyDialog):
    def __init__(self):
        fsui.LegacyDialog.__init__(self, None, "Create/Join Game")
        self.layout = fsui.VerticalLayout()

        self.layout.add_spacer(20)

        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, fill=True)

        hor_layout.add_spacer(20)
        self.text = fsui.TextField(self)
        self.text.activated.connect(self.on_ok_button)
        hor_layout.add(self.text, expand=True)
        hor_layout.add_spacer(20)

        self.layout.add_spacer(20)

        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, fill=True)

        hor_layout.add_spacer(20, expand=True)
        self.cancel_button = fsui.Button(self, "    Cancel    ")
        self.cancel_button.activated.connect(self.on_cancel_button)
        hor_layout.add(self.cancel_button)
        hor_layout.add_spacer(10)
        self.ok_button = fsui.Button(self, "    Create/Join    ")
        self.ok_button.activated.connect(self.on_ok_button)
        hor_layout.add(self.ok_button)
        hor_layout.add_spacer(20)

        self.layout.add_spacer(20)
        self.set_size(self.layout.get_min_size())

        self.text.focus()

    def get_game_name(self):
        return "&" + self.text.get_text()

    def on_ok_button(self):
        self.end_modal(True)

    def on_cancel_button(self):
        self.end_modal(False)
