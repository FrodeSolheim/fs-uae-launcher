from fs_uae_launcher.ui.config.expand import expand_config, \
    AbstractExpandFunctions
from fs_uae_launcher.ui.config.model import ImplicitConfig, normalize, \
    create_model
from fs_uae_launcher.Config import Config
from fs_uae_launcher.Settings import Settings
from fsbc.util import unused
import fsui


class ConfigBrowser(fsui.VerticalItemView):

    def __init__(self, parent):
        fsui.VerticalItemView.__init__(self, parent)

        self.items = []
        self.game_icon = fsui.Image("fs_uae_launcher:res/16/controller.png")
        self.config_icon = fsui.Image(
            "fs_uae_launcher:res/fsuae_config_16.png")
        Config.add_listener(self)
        Settings.add_listener(self)
        # self.update_search()

        self.manual_download_icon = fsui.Image(
            "fs_uae_launcher:res/16/arrow_down_yellow.png")
        self.auto_download_icon = fsui.Image(
            "fs_uae_launcher:res/16/arrow_down_green.png")
        self.blank_icon = fsui.Image(
            "fs_uae_launcher:res/16/blank.png")
        self.missing_color = fsui.Color(0xa8, 0xa8, 0xa8)

        self.platform_icons = {}
        self._need_update = True
        self.update_items()

    def update_items(self):
        # FIXME: replace with a timer-scheduled function so this function does
        # not run needlessly often
        self._need_update = True
        fsui.call_after(self.do_update_items)

    def do_update_items(self):
        if not self._need_update:
            return
        print("do_update_items")
        implicit = ImplicitConfig(ConfigProxy(), SettingsProxy())
        expand_config(implicit, ExpandFunctions())
        model = create_model(implicit, show_all=False)
        # print_model(model)
        items = []

        def flatten(item_list, level):

            for model_item in item_list:
                if model_item.active:
                    text = "    " * level + str(model_item.text)
                    if model_item.extra:
                        text += " [" + model_item.extra + "]"
                    items.append(text)
                if model_item.children:
                    flatten(model_item.children, level + 1)

        flatten(model.items, 0)
        print(items)
        self.set_items(items)
        self._need_update = False

    def on_destroy(self):
        Config.remove_listener(self)
        Settings.remove_listener(self)

    def on_select_item(self, index):
        if index is None:
            return
        pass

    def on_activate_item(self, index):
        pass

    def on_config(self, key, value):
        unused(key)
        unused(value)
        self.update_items()

    def on_setting(self, key, value):
        unused(key)
        unused(value)
        self.update_items()

    def set_items(self, items):
        self.items = items
        self.update()

    def get_item_count(self):
        return len(self.items)

    def get_item_text(self, index):
        item = self.items[index]
        return item
        # return ""

    # def get_item_search_text(self, index):
    #     # return self.items[index][3]
    #     # FIXME: lower-case search string?
    #     return self.items[index][str("sort_key")]
    #
    # def get_item_text_color(self, index):
    #     have = self.items[index][str("have")]
    #     if not have:
    #         return self.missing_color

    def get_item_icon(self, index):
        # item = self.items[index]
        # platform_id = (item[str("platform")] or "").lower()
        # if item[str("have")] == 1:
        #     return self.manual_download_icon
        # elif item[str("have")] == 0:
        #     return self.blank_icon
        # elif item[str("have")] == 2:
        #     return self.auto_download_icon
        # elif item[str("have")] == 4:
        #     if platform_id not in self.platform_icons:
        #         try:
        #             icon = fsui.Image("fs_uae_launcher:res/16/{0}.png".format(
        #                 platform_id))
        #         except Exception:
        #             icon = self.game_icon
        #         self.platform_icons[platform_id] = icon
        #     return self.platform_icons[platform_id]
        # else:
        return self.config_icon

    # def on_get_item_tooltip(self, row, column):
    #     return ""


class SettingsProxy:

    def get(self, key):  # , default=""):
        return Settings.get(key)  # , default)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        Settings.set(key, value)


class ConfigProxy:

    def get(self, key):
        return Config.get(key)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        Config.set(key, value)


class ExpandFunctions(AbstractExpandFunctions):

    @staticmethod
    def matches(a, b):
        a = normalize(a)
        if isinstance(b, list):
            for b_item in b:
                if a == normalize(b_item):
                    return True
            return False
        return a == normalize(b)

    @staticmethod
    def fail(message):
        pass

    @staticmethod
    def warning(message):
        # warnings.append(message)
        pass

    @staticmethod
    def lower(s):
        return s.lower()
