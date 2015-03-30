from fs_uae_launcher.Options import Option
from fs_uae_launcher.ui.bottombar.RatingButton import RatingButton
from fs_uae_workspace.shell import shell_open
import fsui as fsui
from ..I18N import gettext
from ..Settings import Settings
from .ConfigurationsBrowser import ConfigurationsBrowser
from .GameListSelector import GameListSelector
from .IconButton import IconButton
from .Skin import Skin
from .VariantsBrowser import VariantsBrowser


class ConfigurationsPanel(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        Skin.set_background_color(self)
        self.layout = fsui.HorizontalLayout()

        # if Settings.get(Option.CONFIG_FEATURE) == "1":
        #     from fs_uae_launcher.ui.config.browser import ConfigBrowser
        #     config_browser = ConfigBrowser(self)
        #     config_browser.set_min_width(286)
        #     self.layout.add(config_browser, fill=True, margin=10)

        vert_layout = fsui.VerticalLayout()
        self.layout.add(vert_layout, fill=True, expand=True)

        hor_layout = fsui.HorizontalLayout()
        vert_layout.add(hor_layout, fill=True)

        label_stand_in = fsui.Panel(self)
        tw, th = label_stand_in.measure_text("Games")
        label_stand_in.set_min_height(th)
        hor_layout.add(label_stand_in, margin_top=10, margin_bottom=10)

        # label = fsui.HeadingLabel(self, _("Games and Configurations"))
        game_list_selector = GameListSelector(self)
        game_list_selector.set_min_width(250)
        game_list_selector.setMaximumWidth(250)
        hor_layout.add(game_list_selector, expand=False, margin_left=10)

        # hor_layout.add_spacer(10)

        gettext("Filters:")
        # self.filters_label = fsui.Label(self, _("Filters:"))
        # hor_layout.add(
        #     self.filters_label, margin=10, margin_top=0, margin_bottom=0)

        self.text_field = fsui.TextField(self, Settings.get("config_search"))
        self.text_field.on_change = self.on_search_change
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

        # self.favorite_button = IconButton(self, "favorite_button.png")
        # self.favorite_button.set_tooltip(
        #         _("Show Only Favorites (On/Off)"))
        # self.favorite_button.disable()
        # self.favorite_button.activated.connect(self.on_favorite_button)
        # hor_layout.add(self.favorite_button,
        #         margin=10, margin_top=0, margin_bottom=0)

        # self.verified_button = IconButton(self, "ok_button.png")
        # self.verified_button.set_tooltip(
        #         _("Show Only Verified Configurations (On/Off)"))
        # self.verified_button.disable()
        # self.verified_button.activated.connect(self.on_verified_button)
        # hor_layout.add(self.verified_button,
        #        margin=10, margin_top=0, margin_bottom=0)

        # if Settings.get("database_feature") == "1":
        if True:
            self.refresh_button = IconButton(self, "refresh_button.png")
            self.refresh_button.set_tooltip(
                gettext("Refresh Game Configurations from Online Database"))
            self.refresh_button.activated.connect(self.on_refresh_button)
            hor_layout.add(
                self.refresh_button, margin=10, margin_top=0, margin_bottom=0)

        self.configurations_browser = ConfigurationsBrowser(self)

        if VariantsBrowser.use_horizontal_layout():
            hori_layout = fsui.HorizontalLayout()
            vert_layout.add(hori_layout, fill=True, expand=True, margin=10)
            hori_layout.add(self.configurations_browser, fill=True, expand=2)
        else:
            hori_layout = None
            vert_layout.add(
                self.configurations_browser, fill=True, expand=3, margin=10)

        # if Settings.get("database_feature") == "1":
        if True:
            self.variants_browser = VariantsBrowser(self)
            if VariantsBrowser.use_horizontal_layout():
                hori_layout.add(
                    self.variants_browser, fill=True, expand=1, margin_left=18)
                # self.variants_browser.set_min_width(Constants.SCREEN_SIZE[0])
                # elf.variants_browser.set_min_width(72)
                self.variants_browser.set_min_width(100)
            else:
                hori_layout = fsui.HorizontalLayout()
                vert_layout.add(
                    hori_layout, fill=True, expand=False, margin=10,
                    margin_top=20)
                # Do not use fill=True with the default OS X theme at least,
                # if you do the item will be rendered with the old Aqua look
                hori_layout.add(
                    self.variants_browser, fill=False, expand=True)

                for rating in [1, 4, 5]:
                    button = RatingButton(self, rating)
                    hori_layout.add(button, margin_left=5, fill=True)

        else:
            self.variants_browser = None

        Settings.add_listener(self)
        self.on_setting("parent_uuid", Settings.get("parent_uuid"))

    def on_destroy(self):
        Settings.remove_listener(self)

    def on_setting(self, key, value):
        if key == "parent_uuid":
            if self.variants_browser is not None:
                if VariantsBrowser.use_horizontal_layout():
                    self.variants_browser.show_or_hide(bool(value))
                    self.layout.update()
                else:
                    # always show variants list
                    pass

    def on_verified_button(self):
        pass

    def on_favorite_button(self):
        pass

    def on_refresh_button(self):
        print("on_refresh_button")
        shell_open("Workspace:Tools/Refresh", parent=self.get_window())

    def on_search_change(self):
        text = self.text_field.get_text()
        Settings.set("config_search", text)
