from .label import Label


class HeadingLabel(Label):

    def __init__(self, parent, label):
        Label.__init__(self, parent, label)
        font = self.get_font()
        font.set_bold(True)
        self.set_font(font)
