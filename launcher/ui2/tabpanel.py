from fsbc.util import unused
from fsui import Panel, HorizontalLayout
from fsui.context import get_theme
from launcher.ui.skin import Skin


class TabPanel(Panel):
    def __init__(self, parent, spacing=10):
        unused(spacing)
        Panel.__init__(self, parent, paintable=True)
        Skin.set_background_color(self)
        self.layout = HorizontalLayout()
        self.layout.add_spacer(20)
        # self.layout.add_spacer(spacing)
        # self.layout.padding_left = 10
        # self.layout.padding_right = 10

        # self.set_background_color(Color(0xAEAEAE))
        # self.set_min_height(Constants.TAB_HEIGHT)

        self.bgcolor = get_theme(self).window_bgcolor()
        self.set_background_color(self.bgcolor)

    def select_tab(self, index):
        counter = 0
        for child in self.layout.children:
            child = child.element
            if hasattr(child, "type"):
                if child.type == child.TYPE_TAB:
                    if counter == index:
                        child.select()
                    counter += 1

    def set_selected_tab(self, tab):
        for child in self.layout.children:
            child = child.element
            if hasattr(child, "type"):
                if child.type == child.TYPE_TAB:
                    if child == tab:
                        child.state = child.STATE_SELECTED
                        child.refresh()
                    elif child.state == child.STATE_SELECTED:
                        if child.group_id == tab.group_id:
                            child.state = child.STATE_NORMAL
                            child.refresh()

    def add(self, button, expand=False):
        self.layout.add(button, expand=expand)

    def add_spacer(self, spacer=0, expand=False):
        self.layout.add_spacer(spacer, 0, expand=expand)
