import fsui as fsui
from ..Skin import Skin


class ConfigScrollArea(fsui.VerticalScrollArea):

    def __init__(self, parent):
        fsui.VerticalScrollArea.__init__(self, parent)
        Skin.set_background_color(self)
