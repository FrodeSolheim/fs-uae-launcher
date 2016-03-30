from fsbc.util import unused
import fsui as fsui
from fsbc.application import app
from fsgs.Database import Database
from ..launcher_settings import LauncherSettings
from ..i18n import gettext


class GameListSelector(fsui.Choice):

    def __init__(self, parent):
        fsui.Choice.__init__(self, parent)
        self.game_lists = []
        self.populate_list()
        self.item_selected.connect(self.on_item_selected)

        LauncherSettings.add_listener(self)
        self.on_setting("game_list_uuid", app.settings["game_list_uuid"])

    def on_destroy(self):
        LauncherSettings.remove_listener(self)

    def on_setting(self, key, value):
        if key == "config_refresh":
            list_found = False
            with self.inhibit_signal("changed"):
                old_list_uuid = self.get_selected_list_uuid()
                print("- old list uuid", repr(old_list_uuid))
                print("- set choice index to None")
                self.populate_list()
                print("- game lists", self.game_lists)
                for i, item in enumerate(self.game_lists):
                    print("-", repr(item[0]))
                    if item[0] == old_list_uuid:
                        if self.get_index() != i:
                            print("- set choice index to", i)
                            self.set_index(i)
                        list_found = True
                        break
            if not list_found:
                # list uuid is no longer valid
                print("list uuid is no longer valid")
                self.set_index(0)
        elif key == "game_list_uuid":
            for i, item in enumerate(self.game_lists):
                if item[0] == value:
                    if self.get_index() != i:
                        self.set_index(i)
                    break
            else:
                self.set_index(0)

    def populate_list(self):
        database = Database.instance()
        self.game_lists = database.get_game_lists()
        if len(self.game_lists) > 0:
            self.game_lists.insert(0, ["", self.ITEM_SEPARATOR])
        self.game_lists.insert(
            0, [Database.GAME_LIST_GAMES, gettext("Games")])
        self.game_lists.insert(
            0, [Database.GAME_LIST_CONFIGS, gettext("Configs")])
        self.game_lists.insert(
            0, ["", gettext("Configs and Games")])

        currIndex = self.get_index()
        self.blockSignals(True)
        self.clear()
        for item in self.game_lists:
            list_name = item[1]
            if list_name == "Favorites":
                list_name = gettext("Favorites")
            self.add_item(list_name)
        self.blockSignals(False)
        self.set_index(currIndex)

    def get_selected_list_uuid(self):
        index = self.get_index()
        try:
            return self.game_lists[index][0]
        except IndexError:
            # should not really happen...
            return ""

    def on_item_selected(self, index):
        unused(index)
        list_uuid = self.get_selected_list_uuid()
        LauncherSettings.set("game_list_uuid", list_uuid)
