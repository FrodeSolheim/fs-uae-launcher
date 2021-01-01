import weakref

from fsui.qt import Qt, QDialog
from fsui.qt.qparent import QParent
from fsui.qt.toplevelwidget import TopLevelWidget


# def hmm(*args, **kwargs):
#     print("---------------------------------------------------------")
#     print("(destroyed)")
#     print(args, kwargs)
#     print("---------------------------------------------------------")


class DialogWrapper(QDialog):
    def __init__(self, parent, *, border, fswidget, title):
        super().__init__(QParent(parent, window=True))
        self.setWindowTitle(title)
        self.setAttribute(Qt.WA_DeleteOnClose)

        flags = Qt.Dialog
        if not border:
            flags |= Qt.FramelessWindowHint
            # flags |= Qt.NoDropShadowWindowHint
        self.setWindowFlags(flags)

        # Maybe...
        self._fswidget_ref = weakref.ref(fswidget)

    # FIXME: Move to BaseWindow / eventFilter?
    def closeEvent(self, event):
        print(f"DialogWrapper.closeEvent self={self})")
        super().closeEvent(event)
        self._fswidget.on_close()

    @property
    def _fswidget(self):
        return self._fswidget_ref()

    def resizeEvent(self, event):
        self._fswidget.on_resize()

    def showEvent(self, _):
        # if self.owner().center_on_show:
        #     if not self._centered_on_initial_show:
        #         if self.parent():
        #             self.owner().center_on_parent()
        #         self._centered_on_initial_show = True
        #
        self._fswidget.set_initial_size_from_layout()
        self._fswidget.on_resize()


def check_refs(r):
    import fsui
    import gc

    gc.collect()
    obj = r()
    if obj:
        for i, referrer in enumerate(gc.get_referrers(obj)):
            print("")
            print("REF", i, referrer)
    fsui.call_later(1000, check_refs, r)


class Dialog(TopLevelWidget):
    def __init__(self, parent=None, title="", *, border=True):
        super().__init__(
            parent,
            DialogWrapper(parent, border=border, fswidget=self, title=title),
        )
        # print("---", self._qwidget)

        # import fsui
        # fsui.call_later(1000, check_refs, weakref.ref(self))

    # FIXME: Move to TopLevelWidget
    def active(self):
        return self._qwidget.isActiveWindow()

    def __del__(self):
        print("Dialog.__del__", self)

    def end_modal(self, value):
        self._qwidget.done(value)
        self.close()

    # FIXME
    def real_widget(self):
        return self._qwidget

    # FIXME: Correct?
    def real_window(self):
        return self._qwidget

    def show(self):
        self.center_on_initial_show()
        # FIXME: Qt.WindowModal?
        self._qwidget.setWindowModality(Qt.WindowModal)
        return self._qwidget.exec_()

    def show_modal(self):
        self.center_on_initial_show()
        # self.setWindowModality(Qt.WindowModal)
        return self._qwidget.exec_()

    # FIXME: Move to BaseWindow
    def window(self):
        return self._qwidget
