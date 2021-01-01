from fsui import Label, Font, TextArea
from launcher.system.classes.window import Window
from launcher.system.classes.windowresizehandle import WindowResizeHandle
from launcher.ws.shell import shell_hostpath, shell_realcase


class MultiViewWindow(Window):
    def __init__(self, parent):
        super().__init__(parent, title="MultiView")

        self.layout.add(
            Label(self, "MultiView cannot be opened directly yet"), margin=20
        )

        WindowResizeHandle(self)


class MultiViewTextWindow(Window):
    def __init__(self, parent, path):
        # FIXME: Show path in title?
        title = shell_realcase(path)
        # title = "MultiView"
        super().__init__(parent, title=title)

        hostpath = shell_hostpath(path)
        with open(hostpath, "r", encoding="ISO-8859-1") as f:
            text = f.read()
        print(text)

        # FIXME: Use fixed-width font
        # FIXME: Would be fun to use ANSI-symbols compatible with Amiga?

        self.textarea = TextArea(self, text)
        font = Font.from_description("Roboto Mono 15")
        self.textarea.set_font(font)
        self.textarea.set_min_size((800, 700))
        self.textarea.scroll_to_start()
        self.layout.add(self.textarea, fill=True, expand=True)


class MultiView:
    @classmethod
    def wsopen(self, *, path, **kwargs):
        print("MultiView.wsopen, path=", path)
        window = MultiViewTextWindow(None, path)
        window.show()
