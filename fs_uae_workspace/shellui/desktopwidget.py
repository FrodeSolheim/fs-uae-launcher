from fsui.qt import Qt, QWidget


class DesktopWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setMinimumSize(640, 400)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(palette)

        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
