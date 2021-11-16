from fsgamesys.config.configevent import ConfigEvent
from fsui import Color, HorizontalLayout, Panel, TextField
from fswidgets.widget import Widget
from launcher.context import get_settings
from launcher.i18n import gettext
from launcher.ui2.configlistview import ConfigListView
from launcher.ui.newconfigbutton import NewConfigButton
from system.classes.configdispatch import ConfigDispatch


class SearchField(TextField):
    def __init__(self, parent: Widget) -> None:
        # FIXME: Should go via gscontext and not settings
        # or maybe via settings but with a window id/prefix
        text = get_settings(self).get("config_search")
        super().__init__(
            parent, text=text, clearbutton=True, placeholder=gettext("Search")
        )

    def on_changed(self) -> None:
        text = self.text()
        # FIXME: Should go via gscontext and not settings
        get_settings(self).set("config_search", text)


class SearchPanel(Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        horilayout = HorizontalLayout()
        self.layout.add(horilayout, fill=True, expand=True, margin=10)
        # self.set_background_color(Color(0xAEAEAE))
        self.set_background_color(Color(0xB8B8B8))
        horilayout.add(NewConfigButton(self), fill=True, margin_right=10)
        horilayout.add(SearchField(self), fill=True, expand=True)


class Launcher2LeftPanel(Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        # self.set_background_color(Color(0x999999))
        self.search_panel = SearchPanel(self)
        self.layout.add(self.search_panel, fill=True)
        self.config_listview = ConfigListView(self)
        self.layout.add(self.config_listview, fill=True, expand=True)
        ConfigDispatch(self, {"__running": self.__on_running_config})

        # panel = Panel(self)
        # panel.set_min_height(40)
        # # panel.set_background_color(Color(0x888888))
        # panel.set_background_color(Color(0xB8B8B8))
        # self.layout.add(panel, fill=True)

    def get_min_width(self) -> int:
        minWidth = super().get_min_width()
        print("Launcher2LeftPanel.get_min_width (size) =", minWidth)
        return minWidth

    def __on_running_config(self, event: ConfigEvent) -> None:
        isrunning = bool(event.value)
        if self.enabled() == isrunning:
            self.set_enabled(not isrunning)

    def on_resize(self) -> None:
        super().on_resize()
        print("Launcher2LeftPanel.on_resize, size is now", self.getSize())
