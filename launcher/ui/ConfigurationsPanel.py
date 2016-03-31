from launcher.ui.ConfigGroup import ConfigGroup
from launcher.ui.bottombar.RatingButton import RatingButton
from launcher.ui.newbutton import NewButton
import fsui as fsui
from ..launcher_settings import LauncherSettings
from .ConfigurationsBrowser import ConfigurationsBrowser
from .GameListSelector import GameListSelector
from .Skin import Skin
from .VariantsBrowser import VariantsBrowser


class ConfigurationsPanel(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        Skin.set_background_color(self)
        self.layout = fsui.HorizontalLayout()

        vert_layout = fsui.VerticalLayout()
        self.layout.add(vert_layout, fill=True, expand=True)

        hor_layout = fsui.HorizontalLayout()
        vert_layout.add(hor_layout, fill=True)

        label_stand_in = fsui.Panel(self)
        tw, th = label_stand_in.measure_text("Games")
        label_stand_in.set_min_height(th)
        hor_layout.add(label_stand_in, margin_top=10, margin_bottom=10)

        hor_layout.add(NewButton(self), margin_left=10, margin_right=10)

        game_list_selector = GameListSelector(self)
        game_list_selector.set_min_width(250)
        game_list_selector.setMaximumWidth(250)
        game_list_selector.changed.connect(self.on_game_list_changed)
        hor_layout.add(game_list_selector, expand=False, margin_left=10)

        self.text_field = fsui.TextField(
            self, LauncherSettings.get("config_search"))
        self.text_field.on_changed = self.on_search_changed
        if VariantsBrowser.use_horizontal_layout():
            # window is big enough to use fixed size
            # self.text_field.set_min_width(210)
            self.text_field.set_min_width(229)
            hor_layout.add(
                self.text_field, expand=False, margin=10, margin_top=0,
                margin_bottom=0)
        else:
            hor_layout.add(
                self.text_field, expand=True, margin=10, margin_top=0,
                margin_bottom=0)

        # self.refresh_button = IconButton(self, "refresh_button.png")
        # self.refresh_button.set_tooltip(
        #     gettext("Refresh Game Configurations from Online Database"))
        # self.refresh_button.activated.connect(self.on_refresh_button)
        # hor_layout.add(
        #     self.refresh_button, margin=10, margin_top=0, margin_bottom=0)

        self.configurations_browser = ConfigurationsBrowser(self)

        vert_layout.add(
            self.configurations_browser, fill=True, expand=3, margin=10)

        self.variants_panel = fsui.Panel(self)
        vert_layout.add(self.variants_panel, fill=True, expand=False,
                        margin=10, margin_top=20)

        self.variants_panel.layout = fsui.HorizontalLayout()
        self.variants_browser = VariantsBrowser(self.variants_panel)
        # Do not use fill=True with the default OS X theme at least,
        # if you do the item will be rendered with the old Aqua look
        self.variants_panel.layout.add(
            self.variants_browser, fill=False, expand=True)

        for rating in [1, 4, 5]:
            button = RatingButton(self.variants_panel, rating)
            self.variants_panel.layout.add(button, margin_left=5, fill=True)

        self.config_panel = fsui.Panel(self)
        vert_layout.add(self.config_panel, fill=True, expand=False,
                        margin_bottom=10, margin_top=20)

        self.config_panel.layout = fsui.VerticalLayout()
        self.config_group = ConfigGroup(self.config_panel, new_button=False)
        self.config_panel.layout.add(self.config_group, fill=True, expand=True)

        LauncherSettings.add_listener(self)
        self.on_setting("parent_uuid", LauncherSettings.get("parent_uuid"))

    def on_destroy(self):
        LauncherSettings.remove_listener(self)

    def on_setting(self, key, value):
        if key == "parent_uuid":
            self.variants_panel.show_or_hide(bool(value))
            self.config_panel.show_or_hide(not bool(value))
            self.layout.update()

    def on_verified_button(self):
        pass

    def on_favorite_button(self):
        pass

    def on_search_changed(self):
        text = self.text_field.get_text()
        LauncherSettings.set("config_search", text)

    def on_game_list_changed(self):
        print("ConfigurationsPanel.on_game_list_changed!")
        self.text_field.set_text("")
