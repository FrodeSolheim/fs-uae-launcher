from fsui.qt import QMainWindow, QWidget
from .gamecenterview import GameCenterView


class FSGSMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.game_center_view = GameCenterView()
        self.game_center_view.engine().quit.connect(self.on_quit)

        self.game_center_widget = QWidget.createWindowContainer(
            self.game_center_view, parent=self
        )
        self.resize(960, 540)
        self.game_center_widget.resize(960, 540)
        # self.game_center_widget.setFocus()
        # self.game_center_widget.setFocusPolicy(Qt.TabFocus)

        self.game_center_view.requestActivate()
        self.setFocus()

    def on_quit(self):
        self.close()
