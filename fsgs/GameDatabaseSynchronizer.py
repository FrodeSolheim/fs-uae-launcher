import json
import time
from gzip import GzipFile
from io import StringIO
from fsgs.ogd.client import OGDClient
from urllib.request import HTTPBasicAuthHandler, build_opener, Request
from urllib.parse import quote_plus
from fsgs.res import gettext


def bytes_to_int(m):
    return m[0] << 24 | m[1] << 16 | m[2] << 8 | m[3]


class GameDatabaseSynchronizer(object):

    username = ""
    password = ""

    def __init__(self, context, client, on_status=None, stop_check=None):
        self.context = context
        if client:
            self.client = client
            self.database = client.database
        self.downloaded_size = 0
        self.on_status = on_status
        self._stop_check = stop_check

    def stop_check(self):
        if self._stop_check:
            return self._stop_check()

    def set_status(self, title, status=""):
        if self.on_status:
            self.on_status((title, status))

    def synchronize(self):
        if "game-database-version" not in self.context.meta:
            # we haven't looked up synchronization information from the server,
            # that probably means we didn't want to synchronize with the
            # server now, therefore we just return
            return

        self._synchronize()
        if self.stop_check():
            self.client.database.rollback()
        else:
            print("commiting data")
            self.set_status(gettext("Updating database"), gettext("Committing data..."))
            self.database.commit()
            print("done")

    def _synchronize(self):
        if self.context.meta["game-database-version"] != \
                self.database.get_game_database_version():
            self.set_status(gettext("Resetting game database..."))
            self.database.clear()
            self.database.set_game_database_version(
                self.context.meta["game-database-version"])

        self.set_status(gettext("Synchronizing game database..."))

        while True:
            if self.stop_check():
                return
            data = self.fetch_game_sync_data()
            if not data:
                print("no more changes")
                break

            t1 = time.time()
            k = 0
            while k < len(data):
                game_sync_id = bytes_to_int(data[k:k + 4])
                k += 4
                game_uuid = data[k:k + 16]
                k += 16
                game_data_size = bytes_to_int(data[k:k + 4])
                k += 4
                game_data = data[k:k + game_data_size]
                k += game_data_size
                # print("game data len:", len(game_data))
                if len(game_data) > 0:
                    self.database.add_game(game_sync_id, game_uuid, game_data)
                else:
                    self.database.delete_game(game_sync_id, game_uuid)
            t2 = time.time()
            print("  {0:0.2f} seconds".format(t2 - t1))

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
                cursor = self.client.database.cursor()
                cursor.execute(
                    "SELECT count(*) FROM rating WHERE game_uuid = "
                    "? AND work_rating = ? AND like_rating = ? "
                    "AND updated = ?", (update["game"], update["work"],
                                        update["like"], update["updated"]))
                if cursor.fetchone()[0] == 1:
                    # we want to avoid needlessly creating update transactions
                    continue
                cursor.execute("DELETE FROM rating WHERE game_uuid = ?",
                               (update["game"],))
                cursor.execute(
                    "INSERT INTO rating (game_uuid, work_rating, "
                    "like_rating, updated) VALUES (?, ?, ?, ?)",
                    (update["game"], update["work"], update["like"],
                     update["updated"]))
            t2 = time.time()
            print("  {0:0.2f} seconds".format(t2 - t1))

        print("downloaded size: {0:0.2f} MiB".format(
            self.downloaded_size / (1024 * 1024)))

    def get_server(self):
        server = OGDClient.get_server()
        auth_handler = HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm="Open Amiga Game Database",
            uri="http://{0}".format(server), user=self.username,
            passwd=self.password)
        opener = build_opener(auth_handler)
        return server, opener

    def fetch_game_sync_data(self):
        last_id = self.database.get_last_game_id()
        self.set_status(
            gettext("Fetching database entries ({0})").format(last_id + 1))
        server = self.get_server()[0]
        url = "http://{0}/api/game-sync/1?last={1}".format(server, last_id)
        print(url)
        data = self.fetch_data(url)
        self.downloaded_size += len(data)
        return data

    def fetch_change_entries(self):
        last_id = self.client.get_last_change_id()
        self.set_status(
            gettext("Fetching database entries ({0})").format(last_id + 1))
        server = self.get_server()[0]
        url = "http://{0}/api/1/changes?from={1}".format(server, last_id + 1)
        print(url)
        data, json_data = self.fetch_json(url)
        self.downloaded_size += len(data)

        # print(json_data)
        return json_data

    def fetch_rating_entries(self):
        cursor = self.client.database.cursor()
        cursor.execute("SELECT max(updated) FROM rating")
        row = cursor.fetchone()
        last_time = row[0]
        if not last_time:
            last_time = "2012-01-01 00:00:00"            
        self.set_status(gettext("Fetching game ratings ({0})").format(last_time))
        server = self.get_server()[0]
        url = "http://{0}/api/1/ratings?from={1}".format(
            server, quote_plus(last_time))
        print(url)
        data, json_data = self.fetch_json(url)
        self.downloaded_size += len(data)

        # print(json_data)
        return json_data

    def fetch_json_attempt(self, url):
        server, opener = self.get_server()
        request = Request(url)
        request.add_header("Accept-Encoding", "gzip")
        response = opener.open(request)
        # print(response.headers)
        data = response.read()

        try:
            getheader = response.headers.getheader
        except AttributeError:
            getheader = response.getheader
        content_encoding = getheader("content-encoding", "").lower()
        if content_encoding == "gzip":
            # data = zlib.decompress(data)
            fake_stream = StringIO(data)
            data = GzipFile(fileobj=fake_stream).read()

        # else:
        #     data = response.read()
        # if int(time.time()) % 2 == 0:
        #     raise Exception("fail horribly")
        return data, json.loads(data.decode("UTF-8"))

    def fetch_json(self, url):
        for i in range(20):
            try:
                return self.fetch_json_attempt(url)
            except Exception as e:
                print(e)
                sleep_time = 2.0 + i * 0.3
                # FIXME: change second {0} to {1}
                self.set_status(gettext("Download failed (attempt {0}) - "
                                "retrying in {0} seconds").format(
                                i + 1, int(sleep_time)))
                time.sleep(sleep_time)
                self.set_status(
                    gettext("Retrying last operation (attempt {0})").format(i + 1))

        return self.fetch_json_attempt(url)

    def fetch_data_attempt(self, url):
        server, opener = self.get_server()
        request = Request(url)
        # request.add_header("Accept-Encoding", "gzip")
        response = opener.open(request)
        # print(response.headers)
        data = response.read()

        try:
            getheader = response.headers.getheader
        except AttributeError:
            getheader = response.getheader

        content_encoding = getheader("content-encoding", "").lower()
        if content_encoding == "gzip":
            # data = zlib.decompress(data)
            fake_stream = StringIO(data)
            data = GzipFile(fileobj=fake_stream).read()

        # else:
        #     data = response.read()
        # if int(time.time()) % 2 == 0:
        #     raise Exception("fail horribly")
        return data

    def fetch_data(self, url):
        for i in range(10):
            try:
                return self.fetch_data_attempt(url)
            except Exception as e:
                print(e)
                sleep_time = 2.0 + i * 0.3
                # FIXME: change second {0} to {1}
                self.set_status(gettext("Download failed (attempt {0}) - "
                                "retrying in {0} seconds").format(
                                i + 1, int(sleep_time)))
                time.sleep(sleep_time)
                self.set_status(
                    gettext("Retrying last operation (attempt {0})").format(i + 1))

        return self.fetch_data_attempt(url)
