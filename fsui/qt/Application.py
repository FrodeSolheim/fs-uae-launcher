from typing import Any, Callable

from fsbc.application import Application as FSBCApplication
from fsui.qt.icon import Icon
from fsui.qt.qt import init_qt


class Application(FSBCApplication):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.qapplication = init_qt()
        self.on_create()

    def on_create(self) -> None:
        pass

    def run(self) -> None:
        self.qapplication.exec_()
        self.stop()

    def set_icon(self, icon: Icon) -> None:
        self.qapplication.setWindowIcon(icon.qicon())

    def run_in_main(
        self, function: Callable[..., None], *args: Any, **kwargs: Any
    ) -> None:
        from fsui.qt import call_after

        call_after(function, *args, **kwargs)
