from fsui import Font, Label, TextArea
from launcher.system.classes.window import Window
from launcher.system.classes.windowresizehandle import WindowResizeHandle
from launcher.ws.shell import shell_hostpath, shell_realcase


class ChecksumWindow(Window):
    def __init__(self, parent, path):
        super().__init__(parent, title="Checksum")

        self.layout.add(
            Label(self, "MultiView cannot be opened directly yet"), margin=20
        )

        WindowResizeHandle(self)


class Checksum:
    @classmethod
    def wsopen(self, *, path, **kwargs):
        print("Checksum.wsopen, path=", path)
        window = ChecksumWindow(None, path)
        window.show()
