from fsbc.util import unused
import fsui as fsui
from fsbc.Application import app
from fsgs.Database import Database
from ..Settings import Settings
from ..I18N import gettext


class GameListSelector(fsui.Choice):

    def __init__(self, parent):
        fsui.Choice.__init__(self, parent)
        self.game_lists = []
        self.populate_list()
        self.item_selected.connect(self.on_item_selected)

        Settings.add_listener(self)
        self.on_setting("game_list_uuid", app.settings["game_list_uuid"])

    def on_destroy(self):
        Settings.remove_listener(self)

    def on_setting(self, key, value):
        if key == "config_refresh":
            old_list_uuid = self.get_selected_list_uuid()
            print("- old list uuid", old_list_uuid)
            print("- set choice index to None")
            self.set_index(None)
            self.populate_list()
            print("- game lists", self.game_lists)
            for i, item in enumerate(self.game_lists):
                print("-", item[0])
                if item[0] == old_list_uuid:
                    if self.get_index() != i:
                        print("- set choice index to", i)
                        self.set_index(i, signal=True)
                    break
            else:
                # list uuid is no longer valid
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
        self.game_lists.insert(
            0, ["", gettext("All Games and Configs")])

        self.clear()
        for item in self.game_lists:
            self.add_item(item[1])

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
        app.settings["game_list_uuid"] = list_uuid
