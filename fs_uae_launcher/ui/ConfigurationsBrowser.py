from fsgs.Database import Database
from fsgs.platform import PlatformHandler
from fsgs.util.gamenameutil import GameNameUtil
import fsui as fsui
from ..Config import Config
from ..Settings import Settings


class ConfigurationsBrowser(fsui.VerticalItemView):

    def __init__(self, parent):
        fsui.VerticalItemView.__init__(self, parent)
        self.items = []
        self.game_icon = fsui.Image("fs_uae_launcher:res/16/controller.png")
        self.config_icon = fsui.Image(
            "fs_uae_launcher:res/fsuae_config_16.png")
        Settings.add_listener(self)
        self.update_search()

        self.manual_download_icon = fsui.Image(
            "fs_uae_launcher:res/16/arrow_down_yellow.png")
        self.auto_download_icon = fsui.Image(
            "fs_uae_launcher:res/16/arrow_down_green.png")
        self.blank_icon = fsui.Image(
            "fs_uae_launcher:res/16/blank.png")
        self.missing_color = fsui.Color(0xa8, 0xa8, 0xa8)

        self.platform_icons = {}

    def on_destroy(self):
        Settings.remove_listener(self)

    def on_select_item(self, index):
        if index is None:
            return
        # self.load_configuration(self.items[index][str("uuid")])
        self.load_configuration(self.items[index])

    def on_activate_item(self, index):
        from ..FSUAELauncher import FSUAELauncher
        FSUAELauncher.start_game()

    def on_setting(self, key, _):
        if key in ["config_search", "game_list_uuid", "database_show_games",
                   "database_show_adult"]:
            # if key == "game_list_uuid":
            self.update_search()
            if len(self.items) > 0:
                self.select_item(None)
                self.select_item(0)
            else:
                # self.select_item(None)
                if Settings.get("parent_uuid"):
                    Settings.set("parent_uuid", "")
                    Config.load_default_config()
        elif key == "config_refresh":
            self.update_search()
            self.select_item(None)
            old_parent_uuid = Settings.get("parent_uuid")
            if old_parent_uuid:
                Settings.set("parent_uuid", "")
                Settings.set("parent_uuid", old_parent_uuid)

    def set_items(self, items):
        self.items = items
        self.update()

    def get_item_count(self):
        return len(self.items)

    def get_item_text(self, index):
        item = self.items[index]
        name = item[str("name")]
        platform = item[str("platform")] or ""
        if "[" in name:
            name, extra = name.split("[", 1)
            name = name.strip()
            extra = " \u00b7 " + extra.strip(" ]")
        else:
            extra = ""
        if fsui.toolkit == 'wx':
            sep = "\n"
        else:
            sep = " \u00b7 "
            name = name.replace("\n", " \u00b7 ")
        if platform == "Amiga":
            platform = ""
        elif platform:
            platform = sep + PlatformHandler.get_platform_name(platform)
            # if not extra:
            #     sep = ""
            # return "{0}{1}{2}{3}".format(name, sep, extra, "")
        # else:
        text = "{0}{1}{2}".format(name, extra, platform) or "Missing Name"
        return text

        # else:
        #     return "{0} \u00b7 {1}{2}".format(name, extra, platform)

    def get_item_search_text(self, index):
        # return self.items[index][3]
        # FIXME: lower-case search string?
        return self.items[index][str("sort_key")]

    def get_item_text_color(self, index):
        have = self.items[index][str("have")]
        if not have:
            return self.missing_color

    def get_item_icon(self, index):
        item = self.items[index]
        platform_id = (item[str("platform")] or "").lower()
        if item[str("have")] == 1:
            return self.manual_download_icon
        elif item[str("have")] == 0:
            return self.blank_icon
        elif item[str("have")] == 2:
            return self.auto_download_icon
        elif item[str("have")] == 4:
            if platform_id not in self.platform_icons:
                try:
                    icon = fsui.Image("fs_uae_launcher:res/16/{0}.png".format(
                        platform_id))
                except Exception:
                    icon = self.game_icon
                self.platform_icons[platform_id] = icon
            return self.platform_icons[platform_id]
        else:
            return self.config_icon

    # def on_get_item_tooltip(self, row, column):
    #     return self.items[row][1]
    #     #text = text.replace("\nAmiga \u00b7 ", "\n")

    def update_search(self):
        search = Settings.get("config_search").strip().lower()
        print("search for", search)
        words = []
        special = []
        for word in search.split(" "):
            word = word.strip()
            if not word:
                continue
            if ":" in word[1:-1]:
                special.append(word)
            else:
                words.append(word)
        terms = GameNameUtil.extract_search_terms(" ".join(words))
        terms.update(special)

        database = Database.get_instance()

        try:
            have = int(Settings.get("database_show_games"))
        except ValueError:
            # default is show all downloadable and locally available games
            have = 1
        items = database.find_games_new(
            " ".join(terms), have=have,
            list_uuid=Settings.get("game_list_uuid"))

        self.set_items(items)

    def load_configuration(self, item):
        if item[str("uuid")]:
            Settings.set("parent_uuid", item[str("uuid")])
        else:
            config_path = Database.get_instance().decode_path(
                item[str("path")])
            print("load config from", config_path)
            Config.load_file(config_path)
            Settings.set("parent_uuid", "")

        # database = Database.get_instance()
        # config_info = database.get_config(configuration_id)
        # if config_info["data"]:
        #     Config.load_data(config_info["data"])
        #     Settings.set("parent_uuid", "")
        # elif config_info["path"]:
        #     Config.load_file(config_info["path"])
        #     Settings.set("parent_uuid", "")
        # else:
        #     Settings.set("parent_uuid", config_info["uuid"])
