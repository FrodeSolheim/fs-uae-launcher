from typing import List

from fsgamesys.config.configevent import ConfigEvent
from fsui import Choice, Color, HorizontalLayout, Label, Panel
from fsui.context import get_window
from fswidgets.widget import Widget
from launcher.ui2.frontcoverpanel import FrontCoverPanel
from launcher.ui2.launcher2colors import Launcher2Colors
from launcher.ui.book import Book
from launcher.ui.IconButton import IconButton
from system.classes.configdispatch import ConfigDispatch


class Launcher2SidePanel(Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        self.set_background_color(Color(Launcher2Colors.SIDE_PANEL_COLOR))
        # self.set_min_width(300)
        self.set_min_width(252 + 20 * 2)

        hori_layout = HorizontalLayout()
        self.layout.add(
            hori_layout,
            fill=True,
            margin_top=10,
            margin_right=20,
            margin_left=20,
            margin_bottom=0,
        )

        self.choice = Choice(
            self,
            [
                "Game front cover",
            ],
        )
        hori_layout.add(self.choice, expand=True)
        self.choice.disable()  # Currently not implemented

        # FIXME: Only enable button if screen is big enough for expanded
        # window?
        self.add_button = IconButton(self, "add_button.png")
        hori_layout.add(self.add_button, margin_left=10)
        self.add_button.disable()  # Currently not implemented

        self.book = Book(self)
        self.layout.add(self.book, expand=True, fill=True)
        self.pages: List[Widget] = []
        self.pages.append(GameFrontCoverPanel(self.book))
        for page in self.pages:
            self.book.add_page(page)
        self.book.set_page(self.pages[0])


class GameFrontCoverPanel(Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        # self.set_background_color(Color(0xFF0000))
        imageLoader = get_window(self).imageLoader
        self.front_panel = FrontCoverPanel(self, imageLoader)
        self.layout.add(
            self.front_panel,
            margin_top=20,
            margin_right=20,
            margin_bottom=20,
            margin_left=20,
        )

        hori_layout = HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        self.year_label = Label(self)
        font = self.year_label.font()
        font.set_bold()
        self.year_label.set_font(font)
        self.year_label.set_min_width(40)
        hori_layout.add(self.year_label, margin_left=20)

        self.publisher_label = Label(self)
        hori_layout.add(self.publisher_label, expand=True, margin_left=10)

        self._publisher = ""
        self._year = ""
        ConfigDispatch(
            self,
            {
                "publisher": self.__on_publisher_config,
                "year": self.__on_year_config,
            },
        )

    def __on_publisher_config(self, event: ConfigEvent) -> None:
        if event.value != self._publisher:
            self._publisher = event.value
            self._update()

    def __on_year_config(self, event: ConfigEvent) -> None:
        if event.value != self._year:
            self._year = event.value
            self._update()

    def _update(self) -> None:
        self.publisher_label.set_text(self._publisher)
        if self._publisher and not self._year:
            year = "????"
        else:
            year = self._year
        self.year_label.set_text(year)
