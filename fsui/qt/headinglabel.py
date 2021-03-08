from fsui.qt.label import Label


class HeadingLabel(Label):
    def __init__(self, parent, label):
        Label.__init__(self, parent, label)
        font = self.font()
        # font.set_bold(True)
        font.set_weight(500)
        self.set_font(font)
