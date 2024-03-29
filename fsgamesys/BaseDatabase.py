import os
import sqlite3
import threading
from sqlite3.dbapi2 import Connection, Cursor
from types import TracebackType
from typing import Any, Optional, Type, Union

from fsbc.settings import Settings

global_database_lock = threading.Lock()


def log_query_plans() -> bool:
    return Settings.instance().get("log_query_plans") == "1"


def use_debug_cursor() -> bool:
    return log_query_plans()


class ResetException(Exception):
    pass


class DebuggingCursor(object):
    def __init__(self, cursor: Cursor):
        self._cursor = cursor

    def __getattr__(self, item: str) -> Any:
        return getattr(self._cursor, item)

    def __iter__(self) -> Cursor:
        return self._cursor.__iter__()

    def execute(self, query: str, *args: Any) -> Cursor:
        print(query, args)
        if log_query_plans():
            self._cursor.execute("EXPLAIN QUERY PLAN " + query, *args)
            for row in self._cursor:
                print(row[0], row[1], row[2], row[3])
        return self._cursor.execute(query, *args)


class BaseDatabase(object):
    SENTINEL = "fae7671d-e232-4b71-b179-b3cd45995f92"

    thread_local = threading.local()

    @classmethod
    def get_path(cls) -> str:
        raise Exception("get_path not implemented")

    @classmethod
    def get_version(cls) -> int:
        raise Exception("get_version not implemented")

    @classmethod
    def get_reset_version(cls) -> int:
        return 0

    def __init__(self, sentinel: str) -> None:
        assert sentinel == self.SENTINEL
        self._internal_cursor: Optional[Union[Cursor, DebuggingCursor]] = None
        self.connection: Optional[Connection] = None

    def __del__(self) -> None:
        print("BaseDatabase.__del__")

    def __enter__(self) -> "BaseDatabase":
        return self

    # noinspection PyUnusedLocal
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._internal_cursor = None
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def init(self) -> None:
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

    def internal_cursor(self) -> Union[Cursor, DebuggingCursor]:
        if self._internal_cursor is None:
            self._internal_cursor = self.cursor()
        return self._internal_cursor

    def cursor(self) -> Union[Cursor, DebuggingCursor]:
        if not self.connection:
            self.init()
        assert self.connection
        if use_debug_cursor():
            return DebuggingCursor(self.connection.cursor())
        return self.connection.cursor()

    def create_cursor(self) -> Union[Cursor, DebuggingCursor]:
        """ "
        :deprecated:
        """
        return self.cursor()

    def rollback(self) -> None:
        print("Database.rollback")
        if not self.connection:
            self.init()
        assert self.connection
        self.connection.rollback()

    def commit(self) -> None:
        print("BaseDatabase.commit")
        if not self.connection:
            self.init()
        assert self.connection
        self.connection.commit()

    def updated_database_if_needed(self) -> None:
        cursor = self.create_cursor()
        assert self.connection
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
                "application. Have you started an older version?"
            )
        if 0 < version < self.get_reset_version():
            print(" -- resetting database -- ")
            self.connection.close()
            self.connection = None
            os.unlink(self.get_path())
            raise ResetException()

        if self.get_version() > version:
            self.update_database(
                max(version, reset_version - 1), self.get_version()
            )

    def update_database(self, old: int, new: int) -> None:
        for i in range(old + 1, new + 1):
            print("upgrading database to version", i)
            getattr(self, "update_database_to_version_{0}".format(i))()
            cursor = self.create_cursor()
            cursor.execute("UPDATE metadata SET version = ?", (i,))
            self.commit()
