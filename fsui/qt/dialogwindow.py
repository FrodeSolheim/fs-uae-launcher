from fsui.qt.toplevelwidget import TopLevelWidget
from fsui.qt.window import Window


class DialogWindow(Window):
    def __init__(self, parent: TopLevelWidget, title: str):
        super().__init__(parent, title, maximizable=False, minimizable=False)

        # FIXME: Intercept escape key and make it close the dialog window
        # by default.
