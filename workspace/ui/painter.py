import fsui


class Painter(fsui.DrawingContext):

    def __init__(self, parent):
        super().__init__(parent._painter)
