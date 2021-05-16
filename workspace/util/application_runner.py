import signal
import sys

from fsui import Application
from fsui.qt import QFont, QFontDatabase
from workspace.ui import Font


class ApplicationRunner:
    def __init__(self, name):
        self._app = Application(name)

        stream = Font.stream("NotoSans-Regular.ttf")
        # noinspection PyArgumentList
        QFontDatabase.addApplicationFontFromData(stream.read())

        stream = Font.stream("Roboto-Regular.ttf")
        # noinspection PyArgumentList
        QFontDatabase.addApplicationFontFromData(stream.read())

        stream = Font.stream("RobotoMono-Regular.ttf")
        # noinspection PyArgumentList
        QFontDatabase.addApplicationFontFromData(stream.read())

        font = Font("Roboto", 14)
        font.qfont.setPointSizeF(10.5)
        font.qfont.setHintingPreference(QFont.PreferNoHinting)
        self._app.qapplication.setFont(font.qfont)

    def run(self, application):
        # FIXME: Find a nicer way to make PyQT cooperate with Ctrl+C?
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        args = sys.argv[1:]
        application.init(args)
        # if args:
        #     print(args)
        #     application.arguments(args)

        self._app.run()
