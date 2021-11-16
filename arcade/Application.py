import fsui
from fsgamesys.application import ApplicationMixin


class Application(ApplicationMixin, fsui.Application):
    instance = None
    name = None

    @classmethod
    def init(cls, name: str):
        cls.name = name

    def __init__(self):
        super().__init__(Application.name)
        self.set_icon(fsui.Icon("fs-uae-arcade", "pkg:launcher"))
