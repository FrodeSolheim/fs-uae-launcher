from typing import List, Optional

from fsgamesys.config.configevent import ConfigEvent
from fsgamesys.config.configloader import ConfigLoader
from fsgamesys.context import fsgs
from fsgamesys.Database import Database
from fsgamesys.options.constants2 import (
    PARENT_UUID,
    VARIANT_RATING__,
    VARIANT_UUID__,
)
from fsui import Color, Image, ItemChoice
from fswidgets.widget import Widget
from launcher.context import get_config
from launcher.ui.newconfigbutton import NewConfigButton
from system.classes.configdispatch import ConfigDispatch

# class LastVariants(object):
#     def __init__(self):
#         self.cache = {}
#         LauncherSignal.add_listener("quit", self)

#     def on_quit_signal(self):
#         database = Database.get_instance()
#         for key, value in self.cache.items():
#             database.set_last_game_variant(key, value)
#         database.commit()


class VariantChoice(ItemChoice):
    @staticmethod
    def use_horizontal_layout():
        # return get_screen_size()[0] > 1024
        return False

    def __init__(self, parent: Widget) -> None:
        ItemChoice.__init__(self, parent)

        self.parent_uuid = ""
        self.items = []  # type: list [dict]
        # self.last_variants = LastVariants()

        self.missing_color = Color(0xA8, 0xA8, 0xA8)
        self.icon = Image("launcher:/data/fsuae_config_16.png")
        self.adf_icon = Image("launcher:/data/adf_game_16.png")
        self.ipf_icon = Image("launcher:/data/ipf_game_16.png")
        self.cd_icon = Image("launcher:/data/cd_game_16.png")
        self.hd_icon = Image("launcher:/data/hd_game_16.png")
        # self.missing_icon = Image(
        #     "launcher:/data/missing_game_16.png")
        self.missing_icon = Image("launcher:/data/16x16/delete_grey.png")
        self.blank_icon = Image("launcher:/data/16x16/blank.png")
        self.bullet_icon = Image("launcher:/data/16x16/bullet.png")
        self.manual_download_icon = Image(
            "launcher:/data/16x16/arrow_down_yellow.png"
        )
        self.auto_download_icon = Image(
            "launcher:/data/16x16/arrow_down_green.png"
        )
        self.up_icon = Image("launcher:/data/16x16/thumb_up_mod.png")
        self.down_icon = Image("launcher:/data/16x16/thumb_down_mod.png")
        self.fav_icon = Image("launcher:/data/rating_fav_16.png")

        # LauncherSettings.add_listener(self)
        # self.on_setting("parent_uuid", LauncherSettings.get("parent_uuid"))

        ConfigDispatch(
            self,
            {
                PARENT_UUID: self.__on_parent_uuid_config,
                VARIANT_RATING__: self.on_variant_rating_config,
            },
        )

    # def onDestroy(self):
    #     LauncherSettings.remove_listener(self)
    #     # Signal.remove_listener("quit", self)

    def __on_parent_uuid_config(self, event: ConfigEvent) -> None:
        print("-" * 79)
        print("PARENT_UUID IS NOW", event.value)
        print("-" * 79)
        self.parent_uuid = event.value
        if event.value:
            self.update_list(event.value)
        else:
            # LauncherSettings.set("game_uuid", "")
            # self.set_items([gettext("Configuration")])
            self.set_items([])
            self.set_enabled(False)

    def on_select_item(self, index: Optional[int]) -> None:
        if index is None:
            return
        self.load_variant(self.items[index])
        # self.last_variants.cache[self.parent_uuid] = variant_uuid

    def on_variant_rating_config(self, event: ConfigEvent) -> None:
        variant_uuid = get_config(self).get(VARIANT_UUID__)
        for item in self.items:
            if item["uuid"] == variant_uuid:
                item["personal_rating"] = int(event.value or 0)
                self.update()
                break

    def set_items(self, items) -> None:
        self.items = items
        self.update()
        # self.set_enabled(len(items) > 0)

    def get_item_count(self) -> int:
        return len(self.items)

    def get_item_text(self, index: int) -> str:
        name = self.items[index]["name"]
        name = name.replace(", ", " \u00b7 ")
        return name

    def get_item_text_color(self, index: int) -> Optional[Color]:
        have = self.items[index]["have"]
        if not have:
            return self.missing_color
        return None

    NOT_AVAILABLE = 0
    MANUAL_AVAILABLE = 1
    AUTO_AVAILABLE = 2
    AVAILABLE = 3

    def get_item_icon(self, index: int) -> Image:
        have = self.items[index]["have"]
        if have == self.NOT_AVAILABLE:
            # return self.missing_icon
            return self.blank_icon
        if have == self.MANUAL_AVAILABLE:
            return self.manual_download_icon
        if have == self.AUTO_AVAILABLE:
            return self.auto_download_icon
        return self.get_item_extra_icons(index)[0] or self.bullet_icon
        # name = self.items[index]["name"]
        # have = self.items[index]["have"]
        # if not have:
        #     return self.missing_icon
        # if have == 1:
        #     return self.manual_download_icon
        # if have == 2:
        #     return self.auto_download_icon
        #
        # if "IPF" in name:
        #     return self.ipf_icon
        # if "ADF" in name:
        #     return self.adf_icon
        # if "WHDLoad" in name:
        #     return self.hd_icon
        # if "CD32" in name:
        #     return self.cd_icon
        # if "CDTV" in name:
        #     return self.cd_icon
        # return self.icon

    def get_item_extra_icons(self, index: int) -> List[Optional[Image]]:
        personal_rating = self.items[index]["personal_rating"]
        if personal_rating == 5:
            return [self.fav_icon]
        elif personal_rating == 4:
            return [self.up_icon]
        elif personal_rating == 3:
            return [self.up_icon]
        elif personal_rating == 2:
            return [self.down_icon]
        elif personal_rating == 1:
            return [self.down_icon]
        return [None]

    def update_list(self, game_uuid: str) -> None:
        print("VariantsBrowser.update_list, game_uuid=", game_uuid)
        database = Database.get_instance()
        items = database.find_game_variants_new(game_uuid, have=0)

        # items = database.search_configurations(self.search)
        # FIXME: Merge code with
        # FSGameSystemContext.py:get_ordered_game_variants
        sortable_items = []
        for i, variant in enumerate(items):
            name = variant["name"]
            # assert "\n" not in name
            # only show variant name (without game name)
            # name = name.split("\n", 1)[-1]

            game_database = fsgs.game_database(variant["database"])
            (
                variant["like_rating"],
                variant["work_rating"],
            ) = game_database.get_ratings_for_game(variant["uuid"])
            (
                variant["personal_rating"],
                _,
            ) = database.get_ratings_for_game(variant["uuid"])

            if variant["published"] == 0:
                primary_sort = 1
                variant["name"] = "[UNPUBLISHED] " + variant["name"]
            else:
                primary_sort = 0
            sort_key = (
                primary_sort,
                1000000 - variant["like_rating"],
                1000000 - variant["work_rating"],
                name,
            )
            sortable_items.append((sort_key, i, variant))
        # print(sortable_items)
        self.items = [x[2] for x in sorted(sortable_items)]
        self.update()
        # self.set_items(self.items)
        # self.set_item_count(len(self.items))

        self.select_item(None, signal=False)

        select_index = None

        # FIXME: Temporarily disabled
        list_variant_uuid = None
        # list_uuid = LauncherSettings.get("game_list_uuid")
        # if list_uuid:
        #     list_variant_uuid = database.get_variant_for_list_and_game(
        #         list_uuid, game_uuid
        #     )
        #     print(
        #         "game list", list_uuid, "override variant", list_variant_uuid
        #     )
        # else:
        #     list_variant_uuid = None

        if list_variant_uuid:
            # override variant selection from list if possible
            for i, variant in enumerate(self.items):
                print(variant["uuid"], variant["name"], list_variant_uuid)
                if variant["uuid"] == list_variant_uuid:
                    select_index = i
                    print("override select index", select_index)
                    break
        if select_index is None:
            # default index selection
            for i, variant in enumerate(self.items):
                if variant["personal_rating"] == 5:
                    if variant["have"] >= 3:
                        select_index = i
                        break
                    else:
                        # FIXME: Add warning here that the favorite variant
                        # could not be selected.
                        pass
            else:
                for i, variant in enumerate(self.items):
                    if variant["have"] >= 3:
                        select_index = i
                        break
                else:
                    for i, variant in enumerate(self.items):
                        if variant["have"] >= 1:
                            select_index = i
                            break
                    else:
                        if len(self.items) > 0:
                            select_index = 0

        # self.clear()
        # for i, variant in enumerate(self.items):
        #     self.add_item(variant["name"], icon=self.get_item_icon(i))

        self.set_enabled(len(self.items) > 0)
        if select_index is not None:
            print("selecting variant index", select_index)
            self.select_item(select_index)
        else:
            NewConfigButton.new_config(get_config(self))

        # try:
        #     variant_uuid = self.last_variants.cache[game_uuid]
        # except KeyError:
        #     variant_uuid = database.get_last_game_variant(game_uuid)
        # if len(self.items) > 0:
        #     for i, variant in enumerate(self.items):
        #         if variant[3] == variant_uuid:
        #             self.select_item(i)
        #             break
        #     else:
        #         self.select_item(0)

    def load_variant(self, item) -> None:
        self._load_variant(item)
        # try:
        #     self._load_variant(item)
        # except Exception:
        #     traceback.print_exc()
        #     LauncherConfig.load_default_config()
        #     LauncherConfig.load({"__error": "Error Loading Configuration"})
        #     self.select_item(None)

    # @exceptionhandler
    def _load_variant(self, item) -> None:
        print("_load_variant", item)
        variant_uuid = item["uuid"]
        database_name = item["database"]
        personal_rating = item["personal_rating"]
        have = item["have"]
        self._load_variant_2(
            variant_uuid, database_name, personal_rating, have
        )

    def _load_variant_2(
        self,
        variant_uuid: str,
        database_name: str,
        personal_rating: int,
        have: int,
    ) -> None:
        if get_config(self).get(VARIANT_UUID__) == variant_uuid:
            print("Variant {} is already loaded".format(variant_uuid))
        game_database = fsgs.game_database(database_name)

        # game_database_client = GameDatabaseClient(game_database)
        # try:
        #     variant_id = game_database_client.get_game_id(variant_uuid)
        # except Exception:
        #     # game not found:
        #     print("could not find game", repr(variant_uuid))
        #     Config.load_default_config()
        #     return
        # values = game_database_client.get_final_game_values(variant_id)

        values = game_database.get_game_values_for_uuid(variant_uuid)

        # try:
        #     values = game_database.get_game_values_for_uuid(variant_uuid)
        # except Exception:
        #     # game not found:
        #     traceback.print_exc()
        #     print("could not find game", repr(variant_uuid))
        #     LauncherConfig.load_default_config()
        #     return

        # values["variant_uuid"] = variant_uuid
        # values["variant_rating"] = str(item["personal_rating"])

        # LauncherConfig.load_values(values, uuid=variant_uuid)

        game_uuid = values["game_uuid"]
        assert game_uuid
        ConfigLoader(get_config(self)).load_database_values(
            values,
            game_uuid=game_uuid,
            variant_uuid=variant_uuid,
            database_name=database_name,
        )

        # variant_rating = 0
        # if item["work_rating"] is not None:
        #     variant_rating = item["work_rating"] - 2
        # if item["like_rating"]:
        #     variant_rating = item["like_rating"]
        # Config.set("__variant_rating", str(variant_rating))

        # LauncherConfig.set("variant_uuid", variant_uuid)
        # LauncherConfig.set("__changed", "0")
        # LauncherConfig.set("__database", database_name)

        # FIXME
        # LauncherSettings.set("__variant_rating", str(personal_rating))
        get_config(self).set("__variant_rating", str(personal_rating))

        if int(have) < self.AVAILABLE:
            print(" -- some files are missing --")
            # LauncherConfig.set("x_missing_files", "1")
            get_config(self).set("x_missing_files", "1")

    def get_min_width(self) -> int:
        return 0
