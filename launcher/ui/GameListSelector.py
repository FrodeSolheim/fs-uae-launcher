import logging

import fsui
from fsbc.application import app
from fsgamesys.Database import Database
from fsgamesys.options.option import Option
from launcher.i18n import gettext
from launcher.ui.behaviors.settingsbehavior import SettingsBehavior


class GameListSelector(fsui.Choice):
    def __init__(self, parent):
        fsui.Choice.__init__(self, parent)
        self.game_lists = []
        self.populate_list()
        self.changed.connect(self.__on_changed_signal)
        SettingsBehavior(self, [Option.CONFIG_REFRESH, Option.GAME_LIST_UUID])

    def on_settings(self, key, value):
        if key == Option.CONFIG_REFRESH:
            list_found = False
            with self.changed.inhibit:
                logging.debug("GameListSelector on config_refresh")
                old_list_uuid = self.selected_list_uuid()
                logging.debug(
                    "GameListSelector old list uuid %s", repr(old_list_uuid)
                )
                logging.debug("GameListSelector Set choice index to None")
                self.set_index(None)
                self.populate_list()
                logging.debug(
                    "GameListSelector game lists: %s", repr(self.game_lists)
                )
                for i, item in enumerate(self.game_lists):
                    logging.debug("GameListSelector - %s", repr(item[0]))
                    if item[0] == old_list_uuid:
                        if self.index() != i:
                            logging.debug(
                                "GameListSelector Set choice index to %d", i
                            )
                            self.set_index(i)
                        list_found = True
                        break
            if not list_found:
                logging.debug("GameListSelector list uuid is no longer valid")
                self.set_index(0)
        elif key == Option.GAME_LIST_UUID:
            logging.debug("GameListSelector GAME LIST UUID %s", value)
            self.select_list_from_uuid(value)

    def select_list_from_uuid(self, uuid):
        for i, item in enumerate(self.game_lists):
            if item[0] == uuid:
                if self.index() != i:
                    with self.changed.inhibit:
                        logging.debug("GameListSelector = %d", i)
                        self.set_index(i)
                break
        else:
            self.set_index(0)

    def populate_list(self):
        database = Database.instance()
        self.game_lists = database.get_game_lists()
        if len(self.game_lists) > 0:
            self.game_lists.insert(0, ["", self.ITEM_SEPARATOR])
        self.game_lists.insert(0, [Database.GAME_LIST_GAMES, gettext("Games")])
        self.game_lists.insert(
            0, [Database.GAME_LIST_CONFIGS, gettext("Configs")]
        )
        self.game_lists.insert(0, ["", gettext("Configs and Games")])
        self.clear()
        for item in self.game_lists:
            list_name = item[1]
            if list_name == "Favorites":
                list_name = gettext("Favorites")
            self.add_item(list_name)

    def selected_list_uuid(self):
        index = self.index()
        try:
            return self.game_lists[index][0]
        except IndexError:
            # This should not really happen...
            return ""

    def __on_changed_signal(self):
        app.settings["game_list_uuid"] = self.selected_list_uuid()
