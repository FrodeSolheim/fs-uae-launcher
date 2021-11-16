from typing import Callable, List, Optional, Type

from fsgamesys.product import Product
from fsui import Image, Panel
from fsui.qt.menu import Menu
from fsui.qt.scrollarea import ScrollArea
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.panels.additionalconfigpanel import AdditionalConfigPanel
from launcher.panels.cdpanel import CDPanel
from launcher.panels.expansionspanel import ExpansionsPanel
from launcher.panels.floppiespanel import FloppiesPanel
from launcher.panels.harddrivespanel import HardDrivesPanel
from launcher.panels.inputpanel import InputPanel
from launcher.panels.mainpanel import MainPanel
from launcher.panels.romrampanel import RomRamPanel
from launcher.ui2.tabbutton import TabButton
from launcher.ui2.tabpanel import TabPanel
from launcher.ui.book import Book
from launcher.ui.config.configscrollarea import ConfigScrollArea


class ConfigPanel(Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        column = 0

        self.tab_panel = TabPanel(self)
        # if Skin.fws():
        #     self.title_bar = TitleBar(self)
        #     self.layout.add(self.title_bar, fill=True)
        # if self.tab_panel:
        self.layout.add(self.tab_panel, fill=True)
        self.current_tab_group_id = 0
        self.tab_groups: List[List[TabButton]] = [[]]

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

    def new_tab_group(self) -> None:
        self.current_tab_group_id += 1
        self.tab_groups.append([])

    def set_content(self, content: Widget) -> None:
        self.layout.add(content, expand=True, fill=True)

    def select_tab(self, index: int, group: int) -> None:
        print("\n\n\nselect tab", index, group)
        # noinspection PyUnresolvedReferences
        self.tab_groups[group][index].select()
        # self.tab_groups[group].select_tab(index)

    def add_tab(
        self,
        function: Callable[[], None],
        icon: Image,
        title: str = "",
        tooltip: str = "",
    ) -> None:
        if not tooltip:
            tooltip = title
        button = TabButton(self.tab_panel, icon)
        button.set_tooltip(tooltip)
        button.group_id = self.current_tab_group_id
        button.on_select = function  # type: ignore # FIXME
        self.tab_panel.add(button)
        # noinspection PyTypeChecker
        self.tab_groups[self.current_tab_group_id].append(button)

    def add_tab_button(
        self,
        function: Callable[[], None],
        icon: Image,
        title: str = "",
        tooltip: str = "",
        menu_function: Optional[Callable[[], Menu]] = None,
        left_padding: int = 0,
        right_padding: int = 0,
    ) -> TabButton:
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
        # menu_data: List[Optional[Menu]] = [None]
        menu: Optional[Menu] = None
        if function:
            button.activated.connect(function)
        elif menu_function is not None:

            def menu_wrapper():
                nonlocal menu
                print("menu button click")
                # print(menu_data[0] is not None and menu_data[0].is_open())
                # if menu_data[0] is not None and menu_data[0].is_open():
                #     menu_data[0].close()
                # else:
                #     menu_data[0] = menu_function()
                print(menu is not None and menu.is_open())
                if menu is not None and menu.is_open():
                    menu.close()
                else:
                    menu = menu_function()
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

    def _add_page(
        self,
        book: Book,
        instance: Widget,
        icon_name: str,
        title: str,
        tooltip: str,
    ):
        book.add_page(instance)
        icon: Optional[Image]
        if icon_name:
            icon = Image("launcher:/data/{0}.png".format(icon_name))
        else:
            icon = None

        def function() -> None:
            book.set_page(instance)

        if icon:
            self.add_tab(function, icon, title, tooltip)

    def add_page(
        self,
        column: int,
        content_class: Type[Panel],
        icon_name: str,
        title: str,
        tooltip: str = "",
    ):
        book = self.books[column]
        instance = content_class(book)
        # if content_class == MainPanel:
        #     self.main_panel = instance
        self._add_page(book, instance, icon_name, title, tooltip)

    def add_scroll_page(
        self,
        column: int,
        content_class: Type[ScrollArea],
        icon_name: str,
        title: str,
        tooltip: str = "",
    ):
        book = self.books[column]
        instance = ConfigScrollArea(book)
        content_instance = content_class(instance)
        instance.set_widget(content_instance)
        # if content_class == MainPanel:  # type: ignore
        #     self.main_panel = instance
        self._add_page(book, instance, icon_name, title, tooltip)
