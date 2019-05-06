import os, sys
from fsui.qt import QUrl, QLibraryInfo
from fsui.qt import QMainWindow, QWidget, Qt
from PyQt5.QtQuick import QQuickView

# to make sure cxFreeze includes it
import PyQt5.QtNetwork
import PyQt5.QtQml
from fsbc.application import app


class GameCenterView(QQuickView):
    def __init__(self, parent=None):
        QQuickView.__init__(self, parent)

        if getattr(sys, "frozen", ""):
            qml_path = os.path.join(app.executable_dir(), "qml")
        else:
            qml_path = os.path.expanduser("~/git/fs-uae/fs-uae-launcher/qml")

        engine = self.engine()
        print(engine.importPathList())
        print(engine.pluginPathList())
        # engine.setPluginPathList([qml_path, "."])

        # engine.addPluginPath(qml_path)
        # engine.addImportPath(qml_path)

        # engine.setPluginPathList([qml_path, "."])
        # engine.setImportPathList([qml_path])

        # engine.addPluginPath(qml_path)
        # print("setImportPathList", [QUrl.fromLocalFile(qml_path)])
        self.setSource(
            QUrl.fromLocalFile(
                os.path.join(qml_path, "ScaledUserInterface.qml")
            )
        )

        # self.game_center_view = GameCenterView()

        self.engine().quit.connect(self.on_quit)
        self.resize(960, 540)

        # self.game_center_widget = QWidget.createWindowContainer(
        #     self.game_center_view, parent=self)
        # self.resize(960, 540)

        # self.game_center_widget.setFocus()
        # self.game_center_widget.setFocusPolicy(Qt.TabFocus)

        # self.game_center_view.requestActivate()
        # self.setFocus()

    def on_quit(self):
        self.close()
