import time
from urllib.parse import quote_plus
from .i18n import gettext
from fsgs.GameDatabaseSynchronizer import GameDatabaseSynchronizer


class GameRatingSynchronizer(GameDatabaseSynchronizer):

    username = ""
    password = ""

    def __init__(self, context, database, on_status=None, stop_check=None):
        GameDatabaseSynchronizer.__init__(
            self, context, None, on_status, stop_check)
        self.database = database

    def synchronize(self):
        if "game-database-version" not in self.context.meta:
            # we haven't looked up synchronization information from the server,
            # that probably means we didn't want to synchronize with the
            # server now, therefore we just return
            return

        self.set_status(gettext("Synchronizing personal ratings..."))

        last_json_data = ""
        while True:
            if self.stop_check():
                return
            json_data = self.fetch_rating_entries()
            if json_data == last_json_data:
                print("no more changes")
                break
            last_json_data = json_data
            num_changes = len(json_data["ratings"])
            print("  processing {0} entries".format(num_changes))
            t1 = time.time()
            for update in json_data["ratings"]:
                cursor = self.database.cursor()
                cursor.execute("SELECT count(*) FROM rating WHERE game_uuid = "
                               "? AND work_rating = ? AND like_rating = ? "
                               "AND updated = ?",
                               (update["game"], update["work"], update["like"],
                                update["updated"]))
                if cursor.fetchone()[0] == 1:
                    # we want to avoid needlessly creating update transactions
                    continue
                cursor.execute(
                    "DELETE FROM rating WHERE game_uuid = ?",
                    (update["game"],))
                cursor.execute(
                    "INSERT INTO rating (game_uuid, work_rating, "
                    "like_rating, updated) VALUES (?, ?, ?, ?)",
                    (update["game"], update["work"], update["like"],
                     update["updated"]))
            t2 = time.time()
            print("  {0:0.2f} seconds".format(t2 - t1))

    def fetch_rating_entries(self):
        cursor = self.database.cursor()
        cursor.execute("SELECT max(updated) FROM rating")
        row = cursor.fetchone()
        last_time = row[0]
        if not last_time:
            last_time = "2012-01-01 00:00:00"            
        self.set_status(
            gettext("Fetching user game ratings ({0})").format(last_time))
        server = self.get_server()[0]
        url = "http://{0}/games/api/1/user_ratings?from={1}".format(
            server, quote_plus(last_time))
        print(url)
        data, json_data = self.fetch_json(url)
        # self.downloaded_size += len(data)

        return json_data
