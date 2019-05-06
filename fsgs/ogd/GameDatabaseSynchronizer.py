import json
import time
from gzip import GzipFile
from io import StringIO
from urllib.parse import quote_plus
from urllib.request import Request

from fsgs.network import (
    openretro_url_prefix,
    opener_for_url_prefix,
    is_http_url,
)
from fsgs.res import gettext


def bytes_to_int(m):
    return m[0] << 24 | m[1] << 16 | m[2] << 8 | m[3]


class GameDatabaseSynchronizer(object):
    username = ""
    password = ""

    def __init__(
        self,
        context,
        client,
        on_status=None,
        stop_check=None,
        platform_id="amiga",
    ):
        self.context = context
        if client:
            self.client = client
            self.database = client.database
        self.downloaded_size = 0
        self.on_status = on_status
        self._stop_check = stop_check
        if "/" in platform_id:
            self.host, self.platform_id = platform_id.split("/")
        else:
            self.host = ""
            self.platform_id = platform_id.lower()
        self.opener_cache_dict = {}

    def stop_check(self):
        if self._stop_check:
            return self._stop_check()

    def set_status(self, title, status=""):
        if self.on_status:
            self.on_status((title, status))

    def synchronize(self):
        if "database" not in self.context.meta:
            # we haven't looked up synchronization information from the server,
            # that probably means we didn't want to synchronize with the
            # server now, therefore we just return
            return

        self._synchronize()
        if self.stop_check():
            self.client.database.rollback()
        else:
            print("committing data")
            self.set_status(
                gettext("Updating database"), gettext("Committing data...")
            )
            self.database.commit()
            print("done")

    def _synchronize(self):
        if (
            self.context.meta["database"]["version"]
            != self.database.get_game_database_version()
        ):
            self.set_status(gettext("Resetting game database..."))
            self.database.clear()
            self.database.set_game_database_version(
                self.context.meta["database"]["version"]
            )

        self.set_status(gettext("Synchronizing game database..."))

        while True:
            if self.stop_check():
                return
            data = self.fetch_game_sync_data()
            if self.stop_check():
                return
            if not data:
                print("no more changes")
                break

            t1 = time.time()
            k = 0
            while k < len(data):
                game_sync_id = bytes_to_int(data[k : k + 4])
                k += 4
                game_uuid = data[k : k + 16]
                k += 16
                game_data_size = bytes_to_int(data[k : k + 4])
                k += 4
                game_data = data[k : k + game_data_size]
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
            if self.stop_check():
                return
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
                    "AND updated = ?",
                    (
                        update["game"],
                        update["work"],
                        update["like"],
                        update["updated"],
                    ),
                )
                if cursor.fetchone()[0] == 1:
                    # we want to avoid needlessly creating update transactions
                    continue
                cursor.execute(
                    "DELETE FROM rating WHERE game_uuid = ?", (update["game"],)
                )
                cursor.execute(
                    "INSERT INTO rating (game_uuid, work_rating, "
                    "like_rating, updated) VALUES (?, ?, ?, ?)",
                    (
                        update["game"],
                        update["work"],
                        update["like"],
                        update["updated"],
                    ),
                )
            t2 = time.time()
            print("  {0:0.2f} seconds".format(t2 - t1))

        print(
            "downloaded size: {0:0.2f} MiB".format(
                self.downloaded_size / (1024 * 1024)
            )
        )

    def url_prefix(self):
        if self.host:
            if is_http_url(self.host):
                url_prefix = self.host
            else:
                url_prefix = "http://{}".format(self.host)
        else:
            url_prefix = openretro_url_prefix()
        return url_prefix

    def opener(self):
        return opener_for_url_prefix(
            self.url_prefix(),
            self.username,
            self.password,
            cache_dict=self.opener_cache_dict,
        )

    def fetch_game_sync_data(self):
        last_id = self.database.get_last_game_id()
        if self.context.meta["games"][self.platform_id]["sync"] == last_id:
            print("[SYNC] Platform {} already synced".format(self.platform_id))
            return b""
        self.set_status(
            gettext("Fetching database entries ({0})").format(last_id + 1)
        )
        url = "{0}/api/sync/{1}/games?v=3&sync={2}".format(
            self.url_prefix(), self.platform_id, last_id
        )
        print(url)
        data = self.fetch_data(url)
        self.downloaded_size += len(data)
        return data

    def fetch_rating_entries(self):
        cursor = self.client.database.cursor()
        cursor.execute("SELECT max(updated) FROM rating")
        row = cursor.fetchone()
        last_time = row[0]
        if not last_time:
            last_time = "2012-01-01 00:00:00"
        self.set_status(
            gettext("Fetching game ratings ({0})").format(last_time)
        )
        url = "{0}/api/sync/{1}/ratings?from={2}".format(
            self.url_prefix(), self.platform_id, quote_plus(last_time)
        )
        print(url)
        data, json_data = self.fetch_json(url)
        self.downloaded_size += len(data)
        return json_data

    def fetch_json_attempt(self, url):
        request = Request(url)
        request.add_header("Accept-Encoding", "gzip")
        response = self.opener().open(request)
        # print(response.headers)
        data = response.read()
        try:
            getheader = response.headers.getheader
        except AttributeError:
            getheader = response.getheader
        content_encoding = getheader("content-encoding", "").lower()
        if content_encoding == "gzip":
            fake_stream = StringIO(data)
            data = GzipFile(fileobj=fake_stream).read()
        return data, json.loads(data.decode("UTF-8"))

    def fetch_data_attempt(self, url):
        request = Request(url)
        # request.add_header("Accept-Encoding", "gzip")
        response = self.opener().open(request)
        # print(response.headers)
        data = response.read()
        try:
            getheader = response.headers.getheader
        except AttributeError:
            getheader = response.getheader
        content_encoding = getheader("content-encoding", "").lower()
        if content_encoding == "gzip":
            fake_stream = StringIO(data)
            data = GzipFile(fileobj=fake_stream).read()
        return data

    def fetch_json(self, url):
        for i in range(20):
            try:
                return self.fetch_json_attempt(url)
            except Exception as e:
                print(e)
                sleep_time = 2.0 + i * 0.3
                # FIXME: change second {0} to {1}
                self.set_status(
                    gettext(
                        "Download failed (attempt {0}) - "
                        "retrying in {1} seconds"
                    ).format(i + 1, int(sleep_time))
                )
                for _ in range(int(sleep_time) * 10):
                    time.sleep(0.1)
                    if self.stop_check():
                        return
                self.set_status(
                    gettext("Retrying last operation (attempt {0})").format(
                        i + 1
                    )
                )
        return self.fetch_json_attempt(url)

    def fetch_data(self, url):
        for i in range(10):
            try:
                return self.fetch_data_attempt(url)
            except Exception as e:
                print(e)
                sleep_time = 2.0 + i * 0.3
                # FIXME: change second {0} to {1}
                self.set_status(
                    gettext(
                        "Download failed (attempt {0}) - "
                        "retrying in {1} seconds"
                    ).format(i + 1, int(sleep_time))
                )
                for _ in range(int(sleep_time) * 10):
                    time.sleep(0.1)
                    if self.stop_check():
                        return
                self.set_status(
                    gettext("Retrying last operation (attempt {0})").format(
                        i + 1
                    )
                )
        return self.fetch_data_attempt(url)
