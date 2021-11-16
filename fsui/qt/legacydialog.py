import weakref
from typing import Callable, List, Optional

from fsui.common.layout import Layout
from fsui.qt.gui import QCloseEvent, QResizeEvent, QShowEvent
from fsui.qt.qparent import QParent
from fsui.qt.qt import QDialog
from fsui.qt.signal import Signal
from fsui.qt.toplevelwidget import TopLevelWidget
from fsui.qt.widgets import QWidget
from fswidgets.types import Size


class LegacyDialog(QDialog):
    closed = Signal()

    def __init__(
        self, parent: Optional[TopLevelWidget] = None, title: str = ""
    ):
        QDialog.__init__(self, QParent(parent))
        self._window = weakref.ref(self)

        # Overrides layout in QDialog, could be a problem but this class should
        # not be used anymore, so...
        self.layout: Optional[Layout] = None  # type: ignore

        self.setWindowTitle(title)

        # self.container = wx.Panel(self)
        # self.container.get_window = self.get_window
        # self.Bind(wx.EVT_SIZE, self.__resize_event)
        # self.Bind(wx.EVT_WINDOW_DESTROY, self.__destroy_event)
        # self.Bind(wx.EVT_CLOSE, self.__close_event)
        self.destroy_listeners: List[Callable[[], None]] = []
        self.close_listeners: List[Callable[[], None]] = []

    def get_parent(self) -> None:
        return None

    def closeEvent(self, a0: QCloseEvent) -> None:
        print("Dialog.closeEvent")
        self.closed.emit()
        self.on_close()
        for function in self.close_listeners:
            print(function)
            function()
        a0.accept()
        # remove close listeners so they will not keep the object alive
        self.close_listeners = []

    def add_close_listener(self, function: Callable[[], None]) -> None:
        self.close_listeners.append(function)

    def get_window(self) -> "LegacyDialog":
        return self

    def get_container(self) -> QWidget:
        return self

    # def show(self):
    #     self.Show()

    # def close(self):
    #     self.Close()

    def show_modal(self) -> int:
        # self.setModal(True)
        # return self.showModal()
        return self.exec_()

    def end_modal(self, value: int) -> None:
        # self.EndModal(value)
        self.done(value)

    def center_on_parent(self) -> None:
        real_parent = self.parent()
        if real_parent:
            pp = real_parent.x(), real_parent.y()
            ps = real_parent.width(), real_parent.height()
            ss = self.get_size()
            self.move(
                pp[0] + (ps[0] - ss[0]) // 2, pp[1] + (ps[1] - ss[1]) // 2
            )
        # elif self.default_center:
        #     x, y = self.default_center
        #     ss = self.get_size()
        #     self.move(x - ss[0] // 2, y - ss[1] // 2,)

    # def destroy(self):
    #     #self.Destroy()
    #     print("FIXME: Dialog.destroy does nothing")

    def set_title(self, title: str) -> None:
        self.setWindowTitle(title)

    def set_size(self, size: Size) -> None:
        # self.SetClientSize(size)
        # print("FIXME:\n\nDialog.set_size")
        self.resize(size[0], size[1])

    def on_create(self) -> None:
        pass

    def on_close(self) -> None:
        pass

    def onDestroy(self) -> None:
        pass

    # def __destroy_event(self, a0: DestroyEvent):
    #     self.onDestroy()

    # def __close_event(self, a0: QCloseEvent):
    #     print("__close_event")
    #     for function in self.close_listeners:
    #         function()
    #     self.on_close()
    #     self.Destroy()

    def showEvent(self, a0: QShowEvent) -> None:
        self.on_resize()

    def get_size(self) -> Size:
        return self.width(), self.height()

    def resizeEvent(self, a0: QResizeEvent) -> None:
        print("resized..")
        self.on_resize()

    def on_resize(self) -> None:
        if self.layout:
            self.layout.set_size(self.get_size())
            self.layout.update()

    def raise_and_activate(self) -> None:
        self.raise_()
        self.activateWindow()
