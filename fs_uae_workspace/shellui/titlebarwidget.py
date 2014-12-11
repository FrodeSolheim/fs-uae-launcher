from fsui.qt import Qt, QWidget, QLabel, QHBoxLayout


class TitleBarWidget(QWidget):

    def __init__(self, parent, window_handler):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.window_handler = window_handler

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)

        self.caption = Caption(self)
        self.caption.setFixedHeight(self.height())
        # self.caption.setText("FS-UAE Workspace")
        self.caption.setText("Workspace")

        self.caption.setStyleSheet("font-family: \"Open Sans\"; font-size: 10pt; font-weight: bold;")

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addSpacing(10)
        self.layout.addWidget(self.caption)

        self.active_window = None
        self.window_handler.window_activated.connect(self.__window_activated)
        self.window_handler.window_changed.connect(self.__window_changed)

    def __window_activated(self, window):
        print("__window_activated", window)
        self.active_window = window
        if self.active_window:
            if self.active_window.is_desktop():
                self.set_caption("Workspace")
            else:
                self.set_caption(self.active_window.name)
        else:
            self.set_caption("")

    def __window_changed(self, window):
        print("__window_changed", window, window.changed)
        if window != self.active_window:
            return
        if window.changed == "name":
            self.set_caption(window.name)

    def set_caption(self, name):
        #self.caption.setText("Applications    Places    System    " + name)
        self.caption.setText(name)


class Caption(QLabel):

    def __init__(self, parent):
        super().__init__(parent)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # self.setAutoFillBackground(True)
        # palette = self.palette()
        # palette.setColor(self.backgroundRole(), Qt.red)
        # self.setPalette(palette)
