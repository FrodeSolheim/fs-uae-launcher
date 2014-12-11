from ..common.layout import HorizontalLayout, VerticalLayout
from ..common.i18n import gettext
from .Button import Button
from .Panel import Panel


class DialogButtons(Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.layout = HorizontalLayout(padding=20)
        self.layout.padding_top = 0
        self.layout.add_spacer(0, expand=True)

        self.button_layout = HorizontalLayout()
        self.layout.add(self.button_layout, fill=True)

    @classmethod
    def create_with_layout(cls, parent):
        parent.layout = VerticalLayout()
        buttons = DialogButtons(parent)
        layout = VerticalLayout(padding=20)
        parent.layout.add(layout, expand=True, fill=True)
        parent.layout.add(buttons, fill=True)
        return buttons, layout

    def add_button(self, button):
        self.button_layout.add(button, margin_left=10, fill=True)
        return button

    def on_close(self):
        self.get_parent().close()

    def create_close_button(self):
        button = Button(self, gettext("Close"))
        button.activated.connect(self.on_close)
        self.layout.add(button, margin_left=10, fill=True)
        return button
