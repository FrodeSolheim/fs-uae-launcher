from fsui import Image, Panel
from fsgamesys.product import Product
from launcher.i18n import gettext
from launcher.panels.additionalconfigpanel import AdditionalConfigPanel
from launcher.panels.cdpanel import CDPanel
from launcher.panels.expansionspanel import ExpansionsPanel
from launcher.panels.floppiespanel import FloppiesPanel
from launcher.panels.harddrivespanel import HardDrivesPanel
from launcher.panels.inputpanel import InputPanel
from launcher.panels.mainpanel import MainPanel
from launcher.panels.romrampanel import RomRamPanel
from launcher.ui.Constants import Constants
from launcher.ui.book import Book
from launcher.ui.config.configscrollarea import ConfigScrollArea
from launcher.ui2.tabbutton import TabButton
from launcher.ui2.tabpanel import TabPanel


class ConfigPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        column = 0

        self.toolbar = None
        self.tab_panel = TabPanel(self)
        # if Skin.fws():
        #     self.title_bar = TitleBar(self)
        #     self.layout.add(self.title_bar, fill=True)
        # if self.tab_panel:
        self.layout.add(self.tab_panel, fill=True)
        self.current_tab_group_id = 0
        self.tab_groups = [[]]

        self.book = Book(self)
        self.layout.add(self.book, fill=True, expand=True, margin=10)
        self.books = [self.book]

        self.add_page(
            column,
            MainPanel,
            "32x32/go-home",
            gettext("Config"),
            gettext("Main configuration options"),
        )
        if not Product.is_fs_fuse():
            self.add_page(
                column,
                FloppiesPanel,
                "32x32/media-floppy",
                gettext("Floppies"),
                gettext("Floppy drives"),
            )
        if not Product.is_fs_fuse():
            self.add_page(
                column,
                CDPanel,
                "32x32/media-optical",
                gettext("CD-ROMs"),
                gettext("CD-ROM drives"),
            )
        if not Product.is_fs_fuse():
            # noinspection SpellCheckingInspection
            self.add_page(
                column,
                HardDrivesPanel,
                "32x32/drive-harddisk",
                gettext("Hard drives"),
            )
        if not Product.is_fs_fuse():
            self.add_page(
                column,
                InputPanel,
                "32x32/applications-games",
                gettext("Input"),
                gettext("Input options"),
            )
        if not Product.is_fs_fuse():
            # self.add_scroll_page(
            self.add_page(
                column,
                RomRamPanel,
                "32x32/application-x-firmware",
                gettext("Hardware"),
                gettext("CPU, ROM & RAM"),
            )
        if not Product.is_fs_fuse():
            # self.add_scroll_page(
            self.add_page(
                column,
                ExpansionsPanel,
                "32x32/audio-card",
                gettext("Expansions"),
                gettext("Expansions"),
            )
        if not Product.is_fs_fuse():
            # self.add_scroll_page(
            self.add_page(
                column,
                AdditionalConfigPanel,
                "32x32/system-shutdown",
                gettext("Additional Configuration"),
                gettext("Additional configuration"),
            )

        self.select_tab(0, 0)

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

    def add_tab_button(
        self,
        function,
        icon,
        title="",
        tooltip="",
        menu_function=None,
        left_padding=0,
        right_padding=0,
    ):
        if not tooltip:
            tooltip = title
        button = TabButton(
            self.tab_panel,
            icon,
            button_type=TabButton.TYPE_BUTTON,
            left_padding=left_padding,
            right_padding=right_padding,
        )
        button.set_tooltip(tooltip)
        button.group_id = self.current_tab_group_id
        menu_data = [None]
        if function:
            button.activated.connect(function)
        elif menu_function:

            def menu_wrapper():
                print("menu button click")
                print(menu_data[0] is not None and menu_data[0].is_open())
                if menu_data[0] is not None and menu_data[0].is_open():
                    menu_data[0].close()
                else:
                    menu_data[0] = menu_function()
                    button.check_hover()

            # def on_left_up():
            #     print("on left up")
            #     # menu_data[0].close()

            button.on_left_down = menu_wrapper
            button.on_left_dclick = menu_wrapper
            # button.on_left_up = on_left_up
        self.tab_panel.add(button)
        # noinspection PyTypeChecker
        self.tab_groups[self.current_tab_group_id].append(button)
        return button

    def add_tab_panel(self, class_, min_width=0, expand=1000000):
        # panel = class_(self.tab_panel, padding_bottom=2)
        panel = class_(self.tab_panel)
        panel.expandable = True
        panel.set_min_height(Constants.TAB_HEIGHT)
        if self.toolbar:
            panel.SetSize((min_width, 46))
            self.toolbar.AddControl(panel)
        else:
            self.tab_panel.add(panel, expand=expand)
        return panel

    def add_tab_separator(self):
        if self.toolbar:
            self.toolbar.AddSeparator()

    def add_tab_spacer(self, spacer=0, expand=False):
        self.tab_panel.add_spacer(spacer, expand=expand)

    def _add_page(self, book, instance, icon_name, title, tooltip):
        book.add_page(instance)
        if icon_name:
            icon = Image("launcher:res/{0}.png".format(icon_name))
        else:
            icon = None

        def function():
            book.set_page(instance)

        if icon:
            self.add_tab(function, icon, title, tooltip)
        return instance

    def add_page(self, column, content_class, icon_name, title, tooltip=""):
        book = self.books[column]
        instance = content_class(book)
        if content_class == MainPanel:
            self.main_panel = instance
        return self._add_page(book, instance, icon_name, title, tooltip)

    def add_scroll_page(
        self, column, content_class, icon_name, title, tooltip=""
    ):
        book = self.books[column]
        instance = ConfigScrollArea(book)
        content_instance = content_class(instance)
        instance.set_widget(content_instance)
        if content_class == MainPanel:
            self.main_panel = instance
        return self._add_page(book, instance, icon_name, title, tooltip)
