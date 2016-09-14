import fsui
from .application import Application


class Menu(fsui.Menu):

    def __init__(self, parent):
        if isinstance(parent, Application):
            parent.add_menu(self)
        else:
            print("FIXME: adding menu to window", parent)
        super().__init__()
