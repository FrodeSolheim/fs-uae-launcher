from fsui import HorizontalLayout, Panel, TextField, Color
from launcher.context import get_settings
from launcher.i18n import gettext
from launcher.system.classes.configdispatch import ConfigDispatch
from launcher.ui.newconfigbutton import NewConfigButton
from launcher.ui2.configlistview import ConfigListView


class SearchField(TextField):
    def __init__(self, parent):
        # FIXME: Should go via gscontext and not settings
        # or maybe via settings but with a window id/prefix
        text = get_settings(self).get("config_search")
        super().__init__(
            parent, text=text, clearbutton=True, placeholder=gettext("Search")
        )

    def on_changed(self):
        text = self.text()
        # FIXME: Should go via gscontext and not settings
        get_settings(self).set("config_search", text)


class SearchPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        horilayout = HorizontalLayout()
        self.layout.add(horilayout, fill=True, expand=True, margin=10)
        # self.set_background_color(Color(0xAEAEAE))
        self.set_background_color(Color(0xB8B8B8))
        horilayout.add(NewConfigButton(self), fill=True, margin_right=10)
        horilayout.add(SearchField(self), fill=True, expand=True)


class Launcher2LeftPanel(Panel):
    def __init__(self, parent):
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

    def __on_running_config(self, event):
        isrunning = bool(event.value)
        if self.enabled() == isrunning:
            self.set_enabled(not isrunning)
