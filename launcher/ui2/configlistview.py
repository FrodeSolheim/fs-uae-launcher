from fsgamesys import openretro
from fsgamesys.config.configloader import ConfigLoader
from fsgamesys.Database import Database
from fsgamesys.options.constants2 import PARENT_UUID
from fsgamesys.platforms.platform import PlatformHandler
from fsgamesys.product import Product
from fsgamesys.util.gamenameutil import GameNameUtil
from fsui import Color, Font, Image, VerticalItemView, get_window
from launcher.context import get_config, get_gscontext
from launcher.launcher_config import LauncherConfig
from launcher.launcher_settings import LauncherSettings
from launcher.system.exceptionhandler import exceptionhandler
from launcher.ui2.startbutton import StartButton


class ConfigListView(VerticalItemView):
    def __init__(self, parent):
        VerticalItemView.__init__(self, parent, border=False)
        self.items = []
        self.game_icon = Image("launcher:res/16x16/controller.png")
        self.config_icon = Image("launcher:res/fsuae_config_16.png")
        LauncherSettings.add_listener(self)
        self.update_search()

        self.manual_download_icon = Image(
            "launcher:res/16x16/arrow_down_yellow.png"
        )
        self.auto_download_icon = Image(
            "launcher:res/16x16/arrow_down_green.png"
        )
        self.blank_icon = Image("launcher:res/16x16/blank.png")
        self.missing_color = Color(0xA8, 0xA8, 0xA8)
        self.unpublished_color = Color(0xCC, 0x00, 0x00)

        self.platform_icons = {}

        self.set_background_color(Color(0x999999))
        self.set_font(Font("Saira Condensed", 17, weight=500))

        self.set_row_height(32)
        get_window(self).activated.connect(self.__on_activated)
        get_window(self).deactivated.connect(self.__on_deactivated)

        self._qwidget.verticalScrollBar().setStyleSheet(
            f"""
            QScrollBar:vertical {{
                border: 0px;
                /*
                background: #32CC99;
                */
                /*
                background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 #888888, stop: 1 #909090);
                */
                /*
                background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 #848484, stop: 0.0625 #8A8A8A stop: 1 #909090);
                */
                background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 #858585, stop: {1 / (16 - 1)} #8A8A8A stop: 1 #909090);
                width: 16px;
                margin: 0 0 0 0;
            }}
            QScrollBar::handle:vertical {{
                /*
                background: #9d9d9d;
                */
                background: #999999;
                background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 #AAAAAA stop: 1 #999999);
                min-height: 60px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: #AAAAAA;   
                background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 #B2B2B2 stop: 1 #A0A0A0);
            }}

            QScrollBar::handle:vertical:pressed {{
                background: #777777;
            }}

            QScrollBar::add-line:vertical {{
                border: none;
                background: none;
                width: 0;
                height: 0;
            }}

            QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                width: 0;
                height: 0;
            }}
            """
        )

    @exceptionhandler
    def __on_activated(self):
        self.update_stylesheet()

    @exceptionhandler
    def __on_deactivated(self):
        self.update_stylesheet()

    def update_stylesheet(self):
        # FIXME: From theme
        row_bg = "#3B5275"
        if not get_window(self).window_focus():
            row_bg = "#505050"
        self._qwidget.setStyleSheet(
            """
        QListView {{
            background-color: {base};
            /*
            background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 #999999, stop: 1 #909090);
            */
            /*
            background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 #A0A0A0, stop: 1 #909090);
            */
            outline: none;
        }}
        QListView::item {{
            padding-left: 10px;
            border: 0;

        }}
        QListView::item:selected {{
            background-color: {row_bg};
            color: {row_fg};
        }}

        """.format(
                row_fg="#ffffff",
                row_bg=row_bg,
                base="#999999",
            )
        )

    def on_destroy(self):
        LauncherSettings.remove_listener(self)
        super().on_destroy()

    @exceptionhandler
    def on_select_item(self, index):
        if index is None:
            return
        # self.load_configuration(self.items[index][str("uuid")])
        self.load_configuration(self.items[index])

    @exceptionhandler
    def on_activate_item(self, index):
        StartButton.start(self, gscontext=get_gscontext(self))

    @exceptionhandler
    def on_setting(self, key, _):
        if key in [
            "config_search",
            "game_list_uuid",
            "database_show_games",
            "database_show_adult",
            "database_show_unpublished",
        ]:
            # if key == "game_list_uuid":
            self.update_search()
            if len(self.items) > 0:
                self.select_item(None)
                self.select_item(0)
            else:
                # self.select_item(None)
                if LauncherSettings.get(PARENT_UUID):
                    LauncherSettings.set(PARENT_UUID, "")
                    LauncherConfig.load_default_config()
        elif key == "__config_refresh":
            self.update_search()
            self.select_item(None)
            old_parent_uuid = LauncherSettings.get(PARENT_UUID)
            if old_parent_uuid:
                LauncherSettings.set(PARENT_UUID, "")
                LauncherSettings.set(PARENT_UUID, old_parent_uuid)
        elif key == PARENT_UUID or key == "config_path":
            if not (
                LauncherSettings.get(PARENT_UUID)
                or LauncherSettings.get("config_path")
            ):
                self.select_item(None)

    def set_items(self, items):
        self.items = items
        self.update()

    def get_item_count(self):
        return len(self.items)

    def get_item_text(self, index):
        item = self.items[index]
        name = item[str("name")]
        platform_id = item[str("platform")] or ""
        if "[" in name:
            name, extra = name.split("[", 1)
            name = name.strip()
            extra = " \u00b7 " + extra.strip(" ]")
        else:
            extra = ""
        sep = " \u00b7 "
        name = name.replace("\n", " \u00b7 ")
        if platform_id == Product.default_platform_id:
            platform = ""
        elif platform_id == "Amiga" and not openretro:
            platform = ""
        elif platform_id:
            platform = sep + PlatformHandler.get_platform_name(platform_id)
        else:
            platform = ""
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
        published = self.items[index]["published"]
        if not published:
            return self.unpublished_color

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
                    icon = Image(
                        "launcher:res/16x16/{0}.png".format(platform_id)
                    )
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
        search = LauncherSettings.get("config_search").strip().lower()
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
            have = int(LauncherSettings.get("database_show_games"))
        except ValueError:
            # default is show all downloadable and locally available games
            have = 1
        items = database.find_games_new(
            " ".join(terms),
            have=have,
            list_uuid=LauncherSettings.get("game_list_uuid"),
        )

        self.set_items(items)

    # noinspection PyMethodMayBeStatic
    def load_configuration(self, item):
        if item[str("uuid")]:
            # This triggers the variant browser to load variants for the game.
            # FIXME: This needs to be moved to config, somehow.
            get_config(self).set(PARENT_UUID, item["uuid"])

            # FIXME: REMOVE
            # LauncherSettings.set(PARENT_UUID, item["uuid"])

        else:
            config_path = Database.get_instance().decode_path(
                item[str("path")]
            )
            print("load config from", config_path)
            ConfigLoader(get_config(self)).load_config_file(config_path)
            # LauncherConfig.load_file(config_path)

            # FIXME: REMOVE
            # LauncherSettings.set(PARENT_UUID, "")
