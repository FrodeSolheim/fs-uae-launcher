import weakref
from fsui.qt import QMenu, QCursor, QPoint


class AutoCloseMenu(QMenu):

    def mousePressEvent(self, event):
        parent = self._parent()
        # noinspection PyArgumentList
        c = QCursor.pos()
        p = parent.mapToGlobal(QPoint(0, 0))
        s = parent.get_size()
        if p.x() <= c.x() < p.x() + s[0] and p.y() <= c.y() < p.y() + s[1]:
            # We want to close the menu (and not re-open it) if we click
            # on the widget used to open the menu.
            parent._ignore_next_left_down_event = True
        super().mousePressEvent(event)


class Menu:

    def __init__(self, implementation=QMenu):
        self.qmenu = implementation()
        # self._menu = wx.Menu()
        # self._ids = []
        # #self._functions = []
        pass

    def is_open(self):
        return self.qmenu.isVisible()

    def close(self):
        self.qmenu.close()

    def add_item(self, text, function=None, item_id=-1):
        text = text.replace("&", "&&")

        action = self.qmenu.addAction(text)
        if function is not None:
            action.triggered.connect(function)

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

    def add_about_item(self, text, function):
        self.add_item(text, function)

    def add_preferences_item(self, text, function):
        self.add_item(text, function)

    def add_separator(self):
        self.qmenu.addSeparator()

    def set_parent(self, parent):
        self._parent = weakref.ref(parent)
        self.qmenu._parent = weakref.ref(parent)


class PopupMenu(Menu):

    def __init__(self):
        super().__init__(implementation=AutoCloseMenu)
