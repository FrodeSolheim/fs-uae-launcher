from typing import Optional, cast

from fscore.deprecated import deprecated
from fsui.qt.qparent import QParent
from fsui.qt.qt import QCheckBox
from fsui.qt.signal import Signal, SignalWrapper
from fswidgets.parentstack import ParentStack
from fswidgets.widget import Widget


class CheckBox(Widget):
    changed_signal = Signal()

    def __init__(
        self,
        parent: Optional[Widget] = None,
        text: str = "",
        checked: bool = False,
        check: Optional[bool] = False,  # FParameter name check -> checked
    ):
        parent = parent or ParentStack.top()
        super().__init__(parent, QCheckBox(text, QParent(parent)))

        self.changed = SignalWrapper(self, "changed")

        # Legacy parameter
        if check is not None:
            checked = check

        if checked:
            self.setChecked(True)
        self.qwidget.stateChanged.connect(self.__state_changed)  # type: ignore

    def check(self):
        self.setChecked(True)

    def isChecked(self):
        return self.qwidget.isChecked()

    @property
    def qwidget(self) -> QCheckBox:
        return cast(QCheckBox, self.getQWidget())

    def setChecked(self, checked: bool):
        self.qwidget.setChecked(checked)

    def uncheck(self):
        self.setChecked(False)

    # -------------------------------------------------------------------------

    # FIXME: Rename: onChange?
    def on_changed(self):
        self.changed.emit()

    def __state_changed(self):
        if not self.changed.inhibit:
            self.on_changed()

    # -------------------------------------------------------------------------

    @deprecated
    def checked(self):
        return self.isChecked()

    @deprecated
    def set_checked(self, checked: bool):
        self.qwidget.setChecked(checked)
