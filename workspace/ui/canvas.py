import fsui


class Canvas(fsui.Panel):

    def __init__(self, parent):
        super().__init__(parent, paintable=True)
