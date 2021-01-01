from fsui.common.i18n import gettext
from fsui.common.layout import HorizontalLayout, VerticalLayout
from fsui.qt.button import Button
from fsui.qt.panel import Panel


class DialogButtons(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = HorizontalLayout(padding=20)
        self.layout.padding_top = 0
        self.added_spacer = False
        self.button_layout = HorizontalLayout()
        self.layout.add_spacer(0, expand=True)
        self.layout.add(self.button_layout, fill=True)

    @classmethod
    def create_with_layout(cls, parent, create_parent_layout=True):
        if create_parent_layout:
            parent.layout = VerticalLayout()
        buttons = DialogButtons(parent)
        layout = VerticalLayout(padding=20)
        parent.layout.add(layout, expand=True, fill=True)
        parent.layout.add(buttons, fill=True)
        return buttons, layout

    def add_spacer_if_needed(self):
        if self.added_spacer:
            return
        # self.layout.add_spacer(0, expand=True)
        self.added_spacer = True

    def add_button(self, button):
        self.add_spacer_if_needed()
        self.button_layout.add(button, margin_left=10, fill=True)
        return button

    def create_close_button(self):
        self.add_spacer_if_needed()
        button = Button(self, gettext("Close"))
        button.activated.connect(self.__close_activated)
        self.layout.add(button, margin_left=10, fill=True)
        return button

    def __close_activated(self):
        self.get_parent().close()
