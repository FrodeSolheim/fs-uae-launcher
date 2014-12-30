import fsui as fsui
from .TabPanel import TabPanel
from .TabButton import TabButton
from .Constants import Constants
from .Skin import Skin


class WindowWithTabs(fsui.Window):

    def __init__(self, parent, title):
        fsui.Window.__init__(self, parent, title)
        Skin.set_background_color(self)
        self.toolbar = None
        self.tab_panel = TabPanel(self)
        self.layout = fsui.VerticalLayout()
        if self.tab_panel:
            self.layout.add(self.tab_panel, fill=True)
        self.current_tab_group_id = 0
        self.tab_groups = [[]]

    # def __size_event(self, event):
    #     size = event.GetSize()
    #     print("WindowWithTabs size event, size =", size)
    #     event.Skip()

    def realize_tabs(self):
        if self.toolbar:
            self.toolbar.Realize()

    def new_tab_group(self):
        self.current_tab_group_id += 1
        self.tab_groups.append([])

    def set_content(self, content):
        self.layout.add(content, expand=True, fill=True)

    def select_tab(self, index, group):
        if self.toolbar:
            pass
        else:
            print("\n\n\nselect tab", index, group)
            # noinspection PyUnresolvedReferences
            self.tab_groups[group][index].select()
            # self.tab_groups[group].select_tab(index)

    def add_tab(self, function, icon, title="", tooltip=""):
        if not tooltip:
            tooltip = title
        button = TabButton(self.tab_panel, icon)
        button.set_tooltip(tooltip)
        button.group_id = self.current_tab_group_id
        button.on_select = function
        self.tab_panel.add(button)
        # noinspection PyTypeChecker
        self.tab_groups[self.current_tab_group_id].append(button)

    def add_tab_button(self, function, icon, title="", tooltip="",
                       menu_function=None, left_padding=0, right_padding=0):
        if not tooltip:
            tooltip = title
        button = TabButton(
            self.tab_panel, icon, type=TabButton.TYPE_BUTTON,
            left_padding=left_padding, right_padding=right_padding)
        button.set_tooltip(tooltip)
        button.group_id = self.current_tab_group_id
        if function:
            button.activated.connect(function)
        elif menu_function:
            def menu_wrapper():
                menu_function()
                button.check_hover()
            button.on_left_down = menu_wrapper
        self.tab_panel.add(button)
        # noinspection PyTypeChecker
        self.tab_groups[self.current_tab_group_id].append(button)
        return button

    def add_tab_panel(self, class_, min_width=0):
        # panel = class_(self.tab_panel, padding_bottom=2)
        panel = class_(self.tab_panel)
        panel.expandable = True
        panel.set_min_height(Constants.TAB_HEIGHT)
        if self.toolbar:
            panel.SetSize((min_width, 46))
            self.toolbar.AddControl(panel)
        else:
            self.tab_panel.add(panel, expand=1000000)

    def add_tab_separator(self):
        if self.toolbar:
            self.toolbar.AddSeparator()

    def add_tab_spacer(self, spacer=0, expand=False):
        self.tab_panel.add_spacer(spacer, expand=expand)
