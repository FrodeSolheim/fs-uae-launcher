import json
import sqlite3
from binascii import hexlify, unhexlify
import zlib
from .BaseDatabase import BaseDatabase


VERSION = 19
RESET_VERSION = 19
DUMMY_UUID = b"'\\x8b\\xbb\\x00Y\\x8bqM\\x15\\x972\\xa8-t_\\xb2\\xfd'"


class IncompleteGameException(Exception):
    pass


class GameDatabase(BaseDatabase):

    def __init__(self, path):
        BaseDatabase.__init__(self, BaseDatabase.SENTINEL)
        self._path = path

    def get_path(self):
        return self._path

    def get_version(self):
        return VERSION

    def get_reset_version(self):
        return RESET_VERSION

    @staticmethod
    def query(q):
        return q.replace("%s", "?")

    def get_last_game_id(self):
        cursor = self.internal_cursor()
        cursor.execute("SELECT max(id) FROM game")
        row = cursor.fetchone()
        return row[0] or 0

    def get_ratings_for_game(self, game_uuid):
        cursor = self.internal_cursor()
        cursor.execute(
            "SELECT like_rating, work_rating FROM rating WHERE "
            "game_uuid = ?", (game_uuid,))
        row = cursor.fetchone()
        if row is not None:
            return row[0], row[1]
        else:
            return 0, 0

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get_license_code_for_url(self, url):
        # cursor = self.internal_cursor()
        # cursor.execute(
        #     "SELECT license_code FROM file "
        #     "WHERE external = ? LIMIT 1", (url,))
        # row = cursor.fetchone()
        # if not row:
        #     return None
        # return row[0]
        return None

    def add_game(self, game_id, game_uuid, game_data):
        cursor = self.internal_cursor()
        cursor.execute(
            "DELETE FROM game WHERE uuid = ?",
            (sqlite3.Binary(game_uuid),))
        cursor.execute(
            "INSERT INTO game (id, uuid, data) VALUES (?, ?, ?)",
            (game_id, sqlite3.Binary(game_uuid), sqlite3.Binary(game_data)))

    def delete_game(self, game_id, game_uuid):
        cursor = self.internal_cursor()
        cursor.execute(
            "DELETE FROM game WHERE uuid = ?",
            (sqlite3.Binary(game_uuid),))
        cursor.execute(
            "DELETE FROM game WHERE uuid = ?",
            (sqlite3.Binary(DUMMY_UUID),))
        cursor.execute(
            "INSERT INTO game (id, uuid, data) VALUES (?, ?, ?)",
            (game_id, sqlite3.Binary(DUMMY_UUID), ""))

    @staticmethod
    def binary_uuid_to_str(data):
        s = hexlify(data).decode("ASCII")
        return "{}-{}-{}-{}-{}".format(
            s[0:8], s[8:12], s[12:16], s[16:20], s[20:32])

    def get_all_uuids(self):
        cursor = self.internal_cursor()
        cursor.execute("SELECT uuid FROM game WHERE data IS NOT NULL")
        result = set()
        for row in cursor:
            data = row[0]
            if len(data) != 16:
                print("WARNING: Invalid UUID ({} bytes) found: {}".format(
                      len(data), repr(data)))
                continue
            result.add(self.binary_uuid_to_str(data))
        return result

    def get_game_values_for_uuid(self, game_uuid, recursive=True):
        print("get_game_values_for_uuid", game_uuid)
        assert game_uuid
        assert isinstance(game_uuid, str)
        return self.get_game_values(game_uuid=game_uuid, recursive=recursive)

    def get_game_values(self, game_id=None, *, game_uuid=None, recursive=True):
        cursor = self.internal_cursor()
        if game_uuid is not None:
            cursor.execute(
                "SELECT uuid, data FROM game WHERE uuid = ?",
                (sqlite3.Binary(unhexlify(game_uuid.replace("-", ""))),))
            row = cursor.fetchone()
            if not row:
                raise LookupError("Cannot find game uuid {}".format(game_uuid))
        else:
            cursor.execute(
                "SELECT uuid, data FROM game WHERE id = ?", (game_id,))
            row = cursor.fetchone()
            if not row:
                raise LookupError("Cannot find game id {}".format(game_id))
        if game_uuid is None:
            game_uuid = self.binary_uuid_to_str(row[0])
        else:
            assert self.binary_uuid_to_str(row[0]) == game_uuid
        data = zlib.decompress(row[1])
        data = data.decode("UTF-8")

        doc = json.loads(data)
        doc["variant_uuid"] = game_uuid

        # This is a hack so we can retrieve the published-status of the
        # child entry. The original key should have been named _published,
        # probably, to avoid it being inherited.
        variant_published = doc.get("publish", "")

        next_parent_uuid = doc.get("parent_uuid", "")
        next_parent_database = doc.get("parent_database", "")
        while next_parent_uuid and recursive:
            # Treat game_uuid special, it will be the first parent_uuid
            # in the chain.
            doc["game_uuid"] = next_parent_uuid
            if next_parent_database:
                break
            else:
                cursor.execute(
                    "SELECT data FROM game WHERE uuid = ?",
                    (sqlite3.Binary(
                        unhexlify(next_parent_uuid.replace("-", ""))),))
                row = cursor.fetchone()
                if not row:
                    raise IncompleteGameException(
                        "Could not find parent {0} of game {1}".format(
                            next_parent_uuid, game_uuid))
                data = zlib.decompress(row[0])
                data = data.decode("UTF-8")
                next_doc = json.loads(data)
            next_parent_uuid = next_doc.get("parent_uuid", "")
            next_parent_database = next_doc.get("parent_database", "")
            # Let child doc overwrite and append values to parent doc.
            next_doc.update(doc)
            doc = next_doc

        doc["__publish_hack__"] = variant_published
        return doc

    def get_game_database_version(self):
        cursor = self.internal_cursor()
        cursor.execute("SELECT database_version FROM metadata")
        return cursor.fetchone()[0]

    def set_game_database_version(self, version):
        cursor = self.internal_cursor()
        cursor.execute("UPDATE metadata SET database_version = ?", (version,))

    def clear(self):
        cursor = self.internal_cursor()
        cursor.execute("DELETE FROM rating")
        cursor.execute("DELETE FROM game")

    def update_database_to_version_19(self):
        cursor = self.internal_cursor()
        cursor.execute("""
            ALTER TABLE metadata ADD COLUMN games_version
            INTEGER NOT NULL DEFAULT 0;
        """)
        cursor.execute("""
            CREATE TABLE game (
                id INTEGER PRIMARY KEY,
                uuid BLOB,
                data BLOB
            );
        """)
        cursor.execute("""
            CREATE INDEX game_uuid ON game (uuid);
        """)
        cursor.execute("""
            CREATE TABLE rating (
                game_uuid VARCHAR(36) PRIMARY KEY NOT NULL,
                work_rating INT NOT NULL,
                like_rating INT NOT NULL,
                updated TIMESTAMP NULL
            );
        """)
        cursor.execute("""
            ALTER TABLE metadata ADD COLUMN database_version
            INTEGER NOT NULL DEFAULT 0;
        """)
