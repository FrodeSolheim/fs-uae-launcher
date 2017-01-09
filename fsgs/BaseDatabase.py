import os
import sqlite3
import threading
import fsbc.settings


global_database_lock = threading.Lock()


def log_query_plans():
    return fsbc.settings.get("log_query_plans") == "1"


def use_debug_cursor():
    return log_query_plans()


class ResetException(Exception):
    pass


class BaseDatabase(object):

    SENTINEL = "fae7671d-e232-4b71-b179-b3cd45995f92"

    thread_local = threading.local()

    @classmethod
    def get_path(cls):
        raise Exception("get_path not implemented")

    @classmethod
    def get_version(cls):
        raise Exception("get_version not implemented")

    @classmethod
    def get_reset_version(cls):
        return 0

    def __init__(self, sentinel):
        assert sentinel == self.SENTINEL
        self._internal_cursor = None
        self.connection = None

    def __del__(self):
        print("BaseDatabase.__del__")

    def __enter__(self):
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._internal_cursor = None
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def init(self):
        if self.connection:
            return
        path = self.get_path()
        with global_database_lock:
            try:
                print("opening database", path)
                self.connection = sqlite3.connect(path)
                # noinspection PyPropertyAccess
                self.connection.row_factory = sqlite3.Row
                self.updated_database_if_needed()
            except ResetException:
                print("re-opening database", path)
                self.connection = sqlite3.connect(path)
                # noinspection PyPropertyAccess
                self.connection.row_factory = sqlite3.Row
                self.updated_database_if_needed()

    def internal_cursor(self):
        if self._internal_cursor is None:
            self._internal_cursor = self.cursor()
        return self._internal_cursor

    def cursor(self):
        if not self.connection:
            self.init()
        if use_debug_cursor():
            return DebuggingCursor(self.connection.cursor())
        return self.connection.cursor()

    def create_cursor(self):
        """"
        :deprecated:
        """
        return self.cursor()

    def rollback(self):
        print("Database.rollback")
        if not self.connection:
            self.init()
        self.connection.rollback()

    def commit(self):
        print("BaseDatabase.commit")
        if not self.connection:
            self.init()
        self.connection.commit()

    def updated_database_if_needed(self):
        cursor = self.create_cursor()
        reset_version = self.get_reset_version()
        try:
            cursor.execute("SELECT version FROM metadata")
            version = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            cursor.execute("CREATE TABLE metadata (version INTEGER)")
            cursor.execute("INSERT INTO metadata (version) VALUES (?)", (0,))
            self.connection.commit()
            version = 0

        if self.get_version() < version:
            raise Exception(
                "The database has been created by a newer version of this "
                "application. Have you started an older version?")
        if 0 < version < self.get_reset_version():
            print(" -- resetting database -- ")
            self.connection.close()
            self.connection = None
            os.unlink(self.get_path())
            raise ResetException()

        if self.get_version() > version:
            self.update_database(max(version, reset_version - 1),
                                 self.get_version())

    def update_database(self, old, new):
        for i in range(old + 1, new + 1):
            print("upgrading database to version", i)
            getattr(self, "update_database_to_version_{0}".format(i))()
            cursor = self.create_cursor()
            cursor.execute("UPDATE metadata SET version = ?", (i,))
            self.commit()


class DebuggingCursor(object):

    def __init__(self, cursor):
        self._cursor = cursor

    def __getattr__(self, item):
        return getattr(self._cursor, item)

    def __iter__(self):
        return self._cursor.__iter__()

    def execute(self, query, *args, **kwargs):
        print(query, args)
        if log_query_plans():
            self._cursor.execute("EXPLAIN QUERY PLAN " + query,
                                 *args, **kwargs)
            for row in self._cursor:
                print(row[0], row[1], row[2], row[3])
        return self._cursor.execute(query, *args, **kwargs)
