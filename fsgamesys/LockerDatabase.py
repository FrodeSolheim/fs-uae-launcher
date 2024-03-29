import os
import sqlite3
from binascii import unhexlify
from typing import Optional

# FIXME: remove dependency on launcher, have the Launcher tell this class
# the path instead
from fsgamesys.FSGSDirectories import FSGSDirectories

from .BaseDatabase import BaseDatabase

VERSION = 1


class LockerDatabase(BaseDatabase):
    def __init__(self, sentinel: str) -> None:
        BaseDatabase.__init__(self, sentinel)

    @classmethod
    def get_path(cls) -> str:
        return os.path.join(FSGSDirectories.databases_dir(), "Locker.sqlite")

    @classmethod
    def get_version(cls) -> int:
        return VERSION

    @classmethod
    def instance(cls, new: bool = False) -> "LockerDatabase":
        if new or not hasattr(cls.thread_local, "locker_database"):
            cls.thread_local.locker_database = cls(cls.SENTINEL)
        return cls.thread_local.locker_database

    def check_sha1(self, sha1: str) -> int:
        cursor = self.internal_cursor()
        # FIXME: Replace with EXISTS or something
        cursor.execute(
            "SELECT count(*) FROM file WHERE sha1 = ?",
            (sqlite3.Binary(unhexlify(sha1.encode("ASCII"))),),
        )
        return cursor.fetchone()[0]

    def get_sync_version(self) -> Optional[str]:
        cursor = self.internal_cursor()
        cursor.execute("SELECT sync_version FROM metadata")
        row = cursor.fetchone()
        return row[0]

    def set_sync_version(self, sync_version: str) -> None:
        cursor = self.internal_cursor()
        cursor.execute("UPDATE metadata set sync_version = ?", (sync_version,))

    def clear(self) -> None:
        if not self.connection:
            self.init()
        cursor = self.internal_cursor()
        cursor.execute("DELETE FROM file")

    def add_sha1_binary(self, sha1: bytes) -> None:
        cursor = self.internal_cursor()
        cursor.execute(
            "INSERT INTO file (sha1) VALUES (?)", (sqlite3.Binary(sha1),)
        )

    def update_database_to_version_1(self) -> None:
        cursor = self.internal_cursor()
        try:
            cursor.execute("SELECT count(*) FROM file")
        except sqlite3.OperationalError:
            cursor.execute(
                """CREATE TABLE file (
                    sha1 BLOB PRIMARY KEY
                    )"""
            )
        cursor.execute("ALTER TABLE metadata ADD COLUMN sync_version TEXT")
