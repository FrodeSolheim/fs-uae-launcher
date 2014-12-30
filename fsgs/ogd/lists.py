from .base import SynchronizerBase
from ..Database import Database
from fsgs.res import gettext


class ListsSynchronizer(SynchronizerBase):

    def __init__(self, *args, **kwargs):
        SynchronizerBase.__init__(self, *args, **kwargs)

    def synchronize_list(self, database, list_uuid, list_info):
        self.remove_list(database, list_uuid)
        cursor = database.cursor()
        # cursor.execute("DELETE FROM game_list_game WHERE list_uuid = ?",
        #                (list_uuid,))
        doc = self.fetch_json("/api/list-sync/1/{0}".format(list_uuid))
        for game_info in doc["games"]:
            game_uuid = game_info["uuid"]
            variant_uuid = game_info.get("variant", None)
            position = game_info.get("position", None)
            cursor.execute(
                "INSERT INTO game_list_game (list_uuid, game_uuid,"
                "variant_uuid, position) VALUES (?, ?, ?, ?)",
                (list_uuid, game_uuid, variant_uuid, position))
        cursor.execute(
            "INSERT INTO game_list (uuid, name, sync) "
            "VALUES (?, ?, ?)",
            (list_uuid, list_info["name"], list_info["sync"]))

    def remove_list(self, database, list_uuid):
        cursor = database.cursor()
        cursor.execute("DELETE FROM game_list WHERE uuid = ?",
                       (list_uuid,))
        cursor.execute("DELETE FROM game_list_game WHERE list_uuid = ?",
                       (list_uuid,))

    def synchronize(self):
        if self.stop_check():
            return

        if "game-lists" not in self.context.meta:
            # haven't looked up synchronization information from the server
            return

        self.set_status(gettext("Updating game lists..."))

        database = Database.instance()
        cursor = database.cursor()
        cursor.execute("SELECT uuid, name, sync FROM game_list")
        # existing_lists = {}
        existing_syncs = {}
        for row in cursor:
            uuid, name, sync = row
            # existing_lists[uuid] = {
            #     "name": name,
            #     "sync": sync,
            # }
            existing_syncs[uuid] = sync
        # existing_syncs.sort()

        for list_uuid, list_info in self.context.meta["game-lists"].items():
            if list_info["sync"] != existing_syncs.get(list_uuid, None):
                self.set_status(
                    gettext("Updating list '{0}'...".format(list_info["name"])))
                self.synchronize_list(database, list_uuid, list_info)

        for existing_list_uuid in existing_syncs:
            for list_uuid in self.context.meta["game-lists"]:
                if list_uuid == existing_list_uuid:
                    break
            else:
                # this old list should be removed
                self.set_status(gettext("Removing list {0}".format(existing_list_uuid)))
                self.remove_list(database, existing_list_uuid)

        database.commit()
