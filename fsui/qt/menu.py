import weakref
from typing import Any, Optional, Type

from fscore.types import SimpleCallable
from fscore.deprecated import deprecated
from fsui.qt.qt import QCursor, QMenu, QPoint


class AutoCloseMenu(QMenu):
    def mousePressEvent(self, event):
        parent = self._parent()
        # noinspection PyArgumentList
        c = QCursor.pos()
        p = parent.widget().mapToGlobal(QPoint(0, 0))
        s = parent.get_size()
        if p.x() <= c.x() < p.x() + s[0] and p.y() <= c.y() < p.y() + s[1]:
            # We want to close the menu (and not re-open it) if we click
            # on the widget used to open the menu.
            # parent._ignore_next_left_down_event = True
            pass
        super().mousePressEvent(event)


class Menu:
    def __init__(self, implementation: Type[QMenu] = QMenu):
        self.qmenu: QMenu = implementation()
        # self._menu = wx.Menu()
        # self._ids = []
        # #self._functions = []
        pass

    def is_open(self):
        return self.qmenu.isVisible()

    def close(self):
        self.qmenu.close()

    def add_item(
        self,
        text: str,
        function: Optional[SimpleCallable] = None,
        item_id: int = -1,
    ):
        text = text.replace("&", "&&")

        action = self.qmenu.addAction(text)
        if function is not None:
            # Will this case references problems?
            # (Closure holding a reference to the function)
            def triggered_wrapper(checked):
                if function is not None:
                    function()

            action.triggered.connect(triggered_wrapper)  # type: ignore

        # if item_id == -1:
        #     item_id = wx.NewId()
        # self._ids.append(item_id)
        # #self._functions.append(function)
        # self._menu.Append(item_id, text)
        # def function_wrapper(event):
        #     # the reason we use CallAfter here is so control will return
        #     # to the application after having popped up a menu, so the
        #     # button opening a menu can draw its correct state when the
        #     # menu is closed, before for example a modal dialog is opened.
        #     wx.CallAfter(function)
        # self._menu.Bind(wx.EVT_MENU, function_wrapper, id=item_id)

    def add_about_item(self, text: str, function: SimpleCallable):
        self.add_item(text, function)

    def add_preferences_item(self, text: str, function: SimpleCallable):
        self.add_item(text, function)

    def add_separator(self):
        self.qmenu.addSeparator()

    # FIXME: Using Any here to avoid circular import dependency on Widget
    # FIXME: Maybe remove Widget.popup_menu and invert the coupling
    def setParent(self, parent: Any):
        self._parent = weakref.ref(parent)
        self.qmenu._parent = weakref.ref(parent)

    @deprecated
    def set_parent(self, parent: Any):
        self.setParent(parent)


class PopupMenu(Menu):
    def __init__(self):
        super().__init__(implementation=AutoCloseMenu)
