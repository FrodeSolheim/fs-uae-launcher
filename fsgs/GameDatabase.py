import json
import sqlite3
from binascii import unhexlify
import zlib
from .BaseDatabase import BaseDatabase


VERSION = 17
RESET_VERSION = 17
DUMMY_UUID = b"'\\x8b\\xbb\\x00Y\\x8bqM\\x15\\x972\\xa8-t_\\xb2\\xfd'"


class GameDatabase(BaseDatabase):

    def __init__(self, path):
        BaseDatabase.__init__(self, BaseDatabase.SENTINEL)
        self._path = path
        # self._connection = None
        # self._cursor = None

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

    def get_license_code_for_url(self, url):
        cursor = self.internal_cursor()
        cursor.execute(
            "SELECT license_code FROM file "
            "WHERE external = ? LIMIT 1", (url,))
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]

    def add_game(self, game_id, game_uuid, game_data):
        # print("add game", repr(game_id), repr(game_uuid), repr(game_data))
        cursor = self.internal_cursor()
        cursor.execute("DELETE FROM game WHERE uuid = ?",
                       (sqlite3.Binary(game_uuid),))
        cursor.execute("INSERT INTO game (id, uuid, data) VALUES (?, ?, ?)",
                       (game_id, sqlite3.Binary(game_uuid),
                        sqlite3.Binary(game_data)))

    def delete_game(self, game_id, game_uuid):
        cursor = self.internal_cursor()
        cursor.execute("DELETE FROM game WHERE uuid = ?",
                       (sqlite3.Binary(game_uuid),))
        cursor.execute("DELETE FROM game WHERE uuid = ?",
                       (sqlite3.Binary(DUMMY_UUID),))
        cursor.execute("INSERT INTO game (id, uuid, data) VALUES (?, ?, ?)",
                       (game_id, sqlite3.Binary(DUMMY_UUID), ""))

    def get_game_values_for_uuid(self, game_uuid, recursive=True):
        print("get_game_values_for_uuid", game_uuid)
        assert game_uuid
        assert isinstance(game_uuid, str)
        cursor = self.internal_cursor()
        cursor.execute(
            "SELECT id FROM game WHERE uuid = ?",
            (sqlite3.Binary(unhexlify(game_uuid.replace("-", ""))),))
        game_id = cursor.fetchone()[0]
        return self.get_game_values(game_id, recursive)

    def get_game_values(self, game_id, recursive=True):
        cursor = self.internal_cursor()
        cursor.execute("SELECT data FROM game WHERE id = ?", (game_id,))
        data = zlib.decompress(cursor.fetchone()[0])
        data = data.decode("UTF-8")
        doc = json.loads(data)
        next_parent_uuid = doc.get("parent_uuid", "")
        while next_parent_uuid and recursive:
            # treat game_uuid special, it will be the first parent_uuid
            # in the chain
            doc["game_uuid"] = next_parent_uuid
            cursor.execute(
                "SELECT data FROM game WHERE uuid = ?",
                (sqlite3.Binary(
                    unhexlify(next_parent_uuid.replace("-", ""))),))
            row = cursor.fetchone()
            if not row:
                raise Exception("could not find parent {0}".format(
                    next_parent_uuid))
            data = zlib.decompress(row[0])
            data = data.decode("UTF-8")
            next_doc = json.loads(data)
            next_parent_uuid = next_doc.get("parent_uuid", "")
            # let child doc overwrite and append values to parent doc
            next_doc.update(doc)
            doc = next_doc
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

    def update_database_to_version_17(self):
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
