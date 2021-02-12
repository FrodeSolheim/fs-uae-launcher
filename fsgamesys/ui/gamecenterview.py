import os
import sys

from PyQt5.QtQuick import QQuickView

# to make sure cxFreeze includes it
from fsbc.application import app
from fsui.qt import QUrl


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

        #     "qml/ScaledUserInterface.qml")))
        # self.setSource(QUrl.fromLocalFile(
        # self.setSource(QUrl.fromLocalFile(
        #     os.path.expanduser("~/git/fs-uae/fs-uae-launcher/qml/ScaledUserInterface.qml")))
        # self.setSource(QUrl.fromLocalFile(
        #     os.path.expanduser("~/git/fs-uae/fs-uae-launcher/qml/ScaledUserInterface.qml")))
        # print(QLibraryInfo.location(QLibraryInfo.Qml2ImportsPath))
