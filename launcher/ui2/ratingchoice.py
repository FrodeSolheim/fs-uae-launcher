from fsgamesys.Database import Database
from fsgamesys.ogd.client import OGDClient
from fsgamesys.options.constants2 import VARIANT_RATING__, VARIANT_UUID__
from fsui import Choice, Image
from launcher.context import get_config
from launcher.i18n import gettext

# from launcher.launcher_config import LauncherConfig
# from launcher.launcher_settings import LauncherSettings
# from system.exceptionhandler import exceptionhandler
# from launcher.ui.behaviors.configbehavior import ConfigBehavior
# from launcher.ui.behaviors.settingsbehavior import SettingsBehavior
from system.classes.configdispatch import ConfigDispatch


class RatingChoice(Choice):
    """
    Control allowing the user to set rating for a variant.

    The control disallows the use of cursor keys for directly changing
    the selected item, to avoid accidental ratings.
    """

    def __init__(self, parent):
        self.active_icon = 1
        super().__init__(parent, [], cursor_keys=False)
        with self.changed.inhibit:
            self.add_item(
                # gettext("Rate Variant"),
                # gettext("Rate"),
                "",
                Image("launcher:/data/16x16/bullet.png"),
            )
            self.add_item(
                # gettext("Best Variant"),
                gettext("Best"),
                Image("launcher:/data/16x16/rating_fav_2.png"),
            )
            self.add_item(
                # gettext("Good Variant"),
                gettext("Good"),
                Image("launcher:/data/16x16/thumb_up_2.png"),
            )
            self.add_item(
                # gettext("Bad Variant"),
                gettext("Bad"),
                Image("launcher:/data/16x16/thumb_down_2.png"),
            )
        self.set_tooltip(gettext("Rate variant"))
        # FIXME
        # ConfigBehavior(self, ["variant_uuid"])
        # SettingsBehavior(self, ["__variant_rating"])

        ConfigDispatch(
            self,
            {
                VARIANT_RATING__: self.on_variant_rating_config,
                VARIANT_UUID__: self.on_variant_uuid_config,
            },
        )

    def on_changed(self):
        variant_uuid = get_config(self).get(VARIANT_UUID__)
        if not variant_uuid:
            return
        rating = self.index_to_rating(self.index())
        self.set_rating_for_variant(variant_uuid, rating)

    def on_variant_rating_config(self, event):
        with self.changed.inhibit:
            try:
                rating = int(event.value)
            except ValueError:
                rating = 0
            self.set_index(self.rating_to_index(rating))

    def on_variant_uuid_config(self, event):
        self.set_enabled(bool(event.value))

    @staticmethod
    def index_to_rating(index):
        return [0, 5, 4, 1][index]

    @staticmethod
    def rating_to_index(rating):
        return [0, 3, 3, 2, 2, 1][rating]

    def set_rating_for_variant(self, variant_uuid, rating):
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
        # LauncherSettings.set("__variant_rating", str(like_rating))
        get_config(self).set(VARIANT_RATING__, str(like_rating))

    # @exceptionhandler
    # def on___variant_rating_setting(self, value):
    #     with self.changed.inhibit:
    #         try:
    #             rating = int(value)
    #         except ValueError:
    #             rating = 0
    #         self.set_index(self.rating_to_index(rating))

    # @exceptionhandler
    # def on_variant_uuid_config(self, value):
    #     self.set_enabled(value != "")
