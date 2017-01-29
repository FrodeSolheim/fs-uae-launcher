import fsui
from launcher.i18n import gettext


class PrevButton(fsui.Button):
    def __init__(self, parent):
        super().__init__(parent, gettext("Prev"))


class NextButton(fsui.Button):
    def __init__(self, parent):
        super().__init__(parent, gettext("Next"))


class CloseButton(fsui.Button):
    def __init__(self, parent):
        super().__init__(parent, gettext("Close"))

    def on_activate(self):
        print(repr(self.window))
        self.window.close()

    @classmethod
    def add_to_layout(cls, parent, layout, margin=0, margin_top=None):
        if parent.window.theme.has_close_buttons:
            button_layout = fsui.HorizontalLayout()
            assert isinstance(layout, fsui.Layout)
            layout.add(button_layout, fill=True, margin=margin,
                       margin_top=margin_top)
            button_layout.add_spacer(expand=True)
            close_button = CloseButton(parent)
            button_layout.add(close_button, fill=True)
            return close_button
        else:
            return None
