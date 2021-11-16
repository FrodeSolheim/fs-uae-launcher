import weakref
from typing import Optional, cast

from fsui.qt.core import Qt
from fsui.qt.gui import QCloseEvent, QResizeEvent, QShowEvent
from fsui.qt.qparent import QOptionalParent
from fsui.qt.toplevelwidget import TopLevelWidget
from fsui.qt.widgets import QDialog, QWidget
from fswidgets.widget import Widget


class DialogWrapper(QDialog):
    def __init__(
        self,
        parent: Optional[TopLevelWidget],
        *,
        border: bool,
        fswidget: Widget,
        title: str,
    ):
        super().__init__(QOptionalParent(parent, window=True))
        self.setWindowTitle(title)
        self.setAttribute(Qt.WA_DeleteOnClose)

        flags: int = Qt.Dialog
        if not border:
            flags |= Qt.FramelessWindowHint
            # flags |= Qt.NoDropShadowWindowHint
        # FIXME: How to correctly type?
        self.setWindowFlags(cast(Qt.WindowFlags, flags))

        # Maybe...
        self._fswidget_ref = weakref.ref(fswidget)

    # FIXME: Move to BaseWindow / eventFilter?
    def closeEvent(self, a0: QCloseEvent) -> None:
        print(f"DialogWrapper.closeEvent self={self})")
        super().closeEvent(a0)
        self._fswidget.on_close()

    @property
    def _fswidget(self) -> Widget:
        w = self._fswidget_ref()
        assert w is not None
        return w

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self._fswidget.on_resize()

    def showEvent(self, a0: QShowEvent) -> None:
        # if self.owner().center_on_show:
        #     if not self._centered_on_initial_show:
        #         if self.parent():
        #             self.owner().center_on_parent()
        #         self._centered_on_initial_show = True
        #
        self._fswidget.set_initial_size_from_layout()
        self._fswidget.on_resize()


# def check_refs(r):
#     import gc

#     import fsui

#     gc.collect()
#     obj = r()
#     if obj:
#         for i, referrer in enumerate(gc.get_referrers(obj)):
#             print("")
#             print("REF", i, referrer)
#     fsui.call_later(1000, check_refs, r)


class Dialog(TopLevelWidget):
    def __init__(
        self,
        parent: Optional[TopLevelWidget] = None,
        title: str = "",
        *,
        border: bool = True,
    ) -> None:
        super().__init__(
            parent,
            DialogWrapper(parent, border=border, fswidget=self, title=title),
        )
        # print("---", self._qwidget)

        # import fsui
        # fsui.call_later(1000, check_refs, weakref.ref(self))

    # FIXME: Move to TopLevelWidget
    def active(self) -> bool:
        return self.qDialog.isActiveWindow()

    def __del__(self) -> None:
        print("Dialog.__del__", self)

    def end_modal(self, value: int) -> None:
        self.qDialog.done(value)
        self.close()

    # FIXME
    def real_widget(self) -> QWidget:
        return self.qWidget

    # FIXME: Correct?
    def real_window(self) -> QDialog:
        return self.qDialog

    @property
    def qDialog(self) -> QDialog:
        return cast(QDialog, self.qWidget)

    def show(self) -> None:
        self.center_on_initial_show()
        # FIXME: Qt.WindowModal?
        self.qDialog.setWindowModality(Qt.WindowModal)
        self.qDialog.exec_()

    def show_modal(self) -> int:
        self.center_on_initial_show()
        # self.setWindowModality(Qt.WindowModal)
        return self.qDialog.exec_()

    # FIXME: Move to BaseWindow
    @property
    def window(self) -> TopLevelWidget:
        return self
