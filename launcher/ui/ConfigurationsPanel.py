import fsui
from fsgamesys.Database import Database
from fsgamesys.ogd.client import OGDClient
from fsui import Choice, Image
from launcher.context import get_config
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.ui.behaviors.configbehavior import ConfigBehavior
from launcher.ui.behaviors.settingsbehavior import SettingsBehavior
from launcher.ui.ConfigGroup import ConfigGroup
from launcher.ui.ConfigurationsBrowser import ConfigurationsBrowser
from launcher.ui.GameListSelector import GameListSelector
from launcher.ui.newconfigbutton import NewConfigButton
from launcher.ui.skin import Skin
from launcher.ui.VariantsBrowser import VariantsBrowser


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

        hor_layout.add(NewConfigButton(self), margin_left=10, margin_right=10)

        game_list_selector = GameListSelector(self)
        game_list_selector.set_min_width(250)
        # game_list_selector.setMaximumWidth(250)
        game_list_selector.changed.connect(self.on_game_list_changed)
        hor_layout.add(game_list_selector, expand=False, margin_left=10)

        self.text_field = fsui.TextField(
            self, LauncherSettings.get("config_search")
        )
        self.text_field.on_changed = self.on_search_changed

        if VariantsBrowser.use_horizontal_layout():
            # window is big enough to use fixed size
            # self.text_field.set_min_width(210)
            self.text_field.set_min_width(229)
            hor_layout.add(
                self.text_field,
                expand=False,
                margin=10,
                margin_top=0,
                margin_bottom=0,
            )
        else:
            hor_layout.add(
                self.text_field,
                expand=True,
                margin=10,
                margin_top=0,
                margin_bottom=0,
            )

        # self.refresh_button = IconButton(self, "refresh_button.png")
        # self.refresh_button.set_tooltip(
        #     gettext("Refresh Game Configurations from Online Database"))
        # self.refresh_button.activated.connect(self.on_refresh_button)
        # hor_layout.add(
        #     self.refresh_button, margin=10, margin_top=0, margin_bottom=0)

        self.configurations_browser = ConfigurationsBrowser(self)

        vert_layout.add(
            self.configurations_browser, fill=True, expand=3, margin=10
        )

        self.variants_panel = fsui.Panel(self)
        vert_layout.add(
            self.variants_panel,
            fill=True,
            expand=False,
            margin=10,
            margin_top=20,
        )

        self.variants_panel.layout = fsui.HorizontalLayout()
        self.variants_browser = VariantsBrowser(self.variants_panel)
        # Do not use fill=True with the default OS X theme at least,
        # if you do the item will be rendered with the old Aqua look
        self.variants_panel.layout.add(
            self.variants_browser, fill=False, expand=True
        )

        # for rating in [1, 4, 5]:
        #     button = RatingButton(self.variants_panel, rating)
        #     self.variants_panel.layout.add(button, margin_left=5, fill=True)

        self.variants_panel.layout.add(
            RatingChoice(self.variants_panel), margin_left=5, fill=True
        )

        self.config_panel = fsui.Panel(self)
        vert_layout.add(
            self.config_panel,
            fill=True,
            expand=False,
            margin_bottom=10,
            margin_top=20,
        )

        self.config_panel.layout = fsui.VerticalLayout()
        self.config_group = ConfigGroup(self.config_panel, new_button=False)
        self.config_panel.layout.add(self.config_group, fill=True, expand=True)

        LauncherSettings.add_listener(self)
        self.on_setting("parent_uuid", LauncherSettings.get("parent_uuid"))

    def onDestroy(self):
        LauncherSettings.remove_listener(self)
        super().onDestroy()

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


class RatingChoice(Choice):
    """Control allowing the user to set rating for a variant.

    The control disallows the use of cursor keys for directly changing
    the selected item, to avoid accidental ratings.
    """

    def __init__(self, parent):
        self.active_icon = 1
        super().__init__(parent, [], cursor_keys=False)
        with self.changed.inhibit:
            self.add_item(
                gettext("Rate Variant"),
                Image("launcher:/data/16x16/bullet.png"),
            )
            self.add_item(
                gettext("Best Variant"),
                Image("launcher:/data/16x16/rating_fav_2.png"),
            )
            self.add_item(
                gettext("Good Variant"),
                Image("launcher:/data/16x16/thumb_up_2.png"),
            )
            self.add_item(
                gettext("Bad Variant"),
                Image("launcher:/data/16x16/thumb_down_2.png"),
            )
        ConfigBehavior(self, ["variant_uuid"])
        SettingsBehavior(self, ["__variant_rating"])

    def on_changed(self):
        variant_uuid = get_config(self).get("variant_uuid")
        if not variant_uuid:
            return
        rating = self.index_to_rating(self.index())
        self.set_rating_for_variant(variant_uuid, rating)

    @staticmethod
    def index_to_rating(index):
        return [0, 5, 4, 1][index]

    @staticmethod
    def rating_to_index(rating):
        return [0, 3, 3, 2, 2, 1][rating]

    @staticmethod
    def set_rating_for_variant(variant_uuid, rating):
        # FIXME: Do asynchronously, add to queue
        client = OGDClient()
        result = client.rate_variant(variant_uuid, like=rating)
        like_rating = result.get("like", 0)
        work_rating = result.get("work", 0)
        database = Database.instance()
        cursor = database.cursor()
        cursor.execute(
            "DELETE FROM rating WHERE game_uuid = ?", (variant_uuid,)
        )
        cursor.execute(
            "INSERT INTO rating (game_uuid, work_rating, like_rating) "
            "VALUES (?, ?, ?)",
            (variant_uuid, work_rating, like_rating),
        )
        database.commit()
        LauncherSettings.set("__variant_rating", str(like_rating))

    def on___variant_rating_setting(self, value):
        with self.changed.inhibit:
            try:
                rating = int(value)
            except ValueError:
                rating = 0
            self.set_index(self.rating_to_index(rating))

    def on_variant_uuid_config(self, value):
        self.set_enabled(value != "")
