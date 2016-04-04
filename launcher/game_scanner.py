import json
import os
import time
from binascii import hexlify
from functools import lru_cache

from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.FileDatabase import FileDatabase
from fsgs.GameDatabaseClient import GameDatabaseClient
from fsgs.context import fsgs
from fsgs.ogd.GameDatabaseSynchronizer import GameDatabaseSynchronizer
from fsgs.util.gamenameutil import GameNameUtil
from .i18n import gettext
from .launcher_settings import LauncherSettings

# from fsgs.ogd.context import SynchronizerContext
# from fsgs.ogd.meta import MetaSynchronizer
from fsgs.ogd.locker import LockerSynchronizer

from launcher.options import Option

GAME_ENTRY_TYPE_GAME = 1 << 0
GAME_ENTRY_TYPE_VARIANT = 1 << 1


class GameScanner(object):

    def __init__(self, context, _, on_status=None, stop_check=None):
        self.fsgs = fsgs
        self.context = context
        # self.paths = paths
        self.on_status = on_status
        self._stop_check = stop_check
        self.scan_count = 0
        self.scan_version = int(time.time() * 100)

    def stop_check(self):
        if self._stop_check:
            return self._stop_check()

    def set_status(self, title, status):
        if self.on_status:
            self.on_status((title, status))

    def game_databases(self, custom=True):
        if True:
            # yield "openretro.org/amiga", self.fsgs.get_game_database()
            yield "Amiga", self.fsgs.get_game_database()
            yield "CD32", self.fsgs.game_database("CD32")
            yield "CDTV", self.fsgs.game_database("CDTV")
        if LauncherSettings.get(Option.DATABASE_ARCADE) == "1":
            yield "Arcade", self.fsgs.game_database("Arcade")
        if LauncherSettings.get(Option.DATABASE_C64) == "1":
            yield "C64", self.fsgs.game_database("C64")
        if LauncherSettings.get(Option.DATABASE_CPC) == "1":
            yield "CPC", self.fsgs.game_database("CPC")
        if LauncherSettings.get(Option.DATABASE_DOS) == "1":
            yield "DOS", self.fsgs.game_database("DOS")
        if LauncherSettings.get(Option.DATABASE_GBA) == "1":
            yield "GBA", self.fsgs.game_database("GBA")
        if LauncherSettings.get(Option.DATABASE_NES) == "1":
            yield "NES", self.fsgs.game_database("NES")
        if LauncherSettings.get(Option.DATABASE_SNES) == "1":
            yield "SNES", self.fsgs.game_database("SNES")
        if LauncherSettings.get(Option.DATABASE_ATARI) == "1":
            yield "Atari", self.fsgs.game_database("Atari")
        if custom:
            for name in self.custom_database_names():
                yield name, self.fsgs.game_database(name)

    @lru_cache()
    def custom_database_names(self):
        custom_dir = os.path.join(FSGSDirectories.databases_dir(), "Custom")
        custom_databases = []
        if os.path.exists(custom_dir):
            for item in os.listdir(custom_dir):
                if item.endswith(".sqlite"):
                    custom_databases.append("Custom/" + item[:-7])
        return custom_databases

    def update_game_database(self):
        for database_name, game_database in self.game_databases(custom=False):
            with game_database:
                self._update_game_database(database_name, game_database)
            if self.stop_check():
                return
        # with self.fsgs.get_game_database() as game_database:
        #     self._update_game_database(game_database)
        #     if self.stop_check():
        #         return

        synchronizer = LockerSynchronizer(
            self.context, on_status=self.on_status, stop_check=self.stop_check)
        synchronizer.synchronize()

    def _update_game_database(self, database_name, game_database):
        game_database_client = GameDatabaseClient(game_database)
        synchronizer = GameDatabaseSynchronizer(
            self.context, game_database_client, on_status=self.on_status,
            stop_check=self.stop_check, platform_id=database_name)
        synchronizer.username = "auth_token"
        synchronizer.password = LauncherSettings.get("database_auth")
        synchronizer.synchronize()

    def scan(self, database):
        self.set_status(
            gettext("Scanning games"), gettext("Please wait..."))

        self.set_status(gettext("Scanning configurations"),
                        gettext("Scanning game database entries..."))

        helper = ScanHelper(database)
        for database_name, game_database in self.game_databases():
            with game_database:
                self.scan_game_database(helper, database_name, game_database)
            if self.stop_check():
                return

        # if False:
        #     with self.fsgs.get_game_database() as game_database:
        #         self.scan_game_database(helper, game_database)
        #         if self.stop_check():
        #             return
        # if Settings.get(Option.DATABASE_SNES) == "1":
        #     with self.fsgs.game_database("snes") as game_database:
        #         self.scan_game_database(helper, game_database)
        #         if self.stop_check():
        #             return
        helper.finish()

    def scan_game_database(self, helper, database_name, game_database):
        """
        :type helper: ScanHelper
        :type game_database: fsgs.GameDatabase.GameDatabase
        """
        database_cursor = helper.database.cursor()

        # this holds a list of game entry UUIDs which must exist / be checked
        # after variants have been processed
        # ensure_updated_games = set()

        game_database_cursor = game_database.cursor()

        # this list will contain game entries which are not variants
        game_rows = []

        game_database_cursor.execute(
            "SELECT id, uuid FROM game WHERE data != ''")
        for row in game_database_cursor:
            if self.stop_check():
                return

            variant_id, variant_uuid_bin = row
            variant_uuid = binary_to_uuid(variant_uuid_bin)
            update_stamp = variant_id

            existing_variant = helper.existing_variants.get(
                variant_uuid, (None, None, None))

            if update_stamp == existing_variant[0]:
                # entry was already updated and has not changed
                if existing_variant[1] and not helper.deleted_files:
                    # have this entry already and no files have been deleted
                    # since the last time

                    # print("skipping variant (no deleted files)")
                    helper.variant_seen(variant_uuid)
                    continue
                if not existing_variant[1] and not helper.added_files:
                    # do not have this entry, but no files have been added
                    # since the last time

                    # print("skipping variant (no added files)")
                    helper.variant_seen(variant_uuid)
                    continue
            else:
                # when the game entry has changed, we always check it
                # regardless of file database status, since file_list may
                # have been changed, or download status... (or other info
                # needs to be corrected)
                pass

            self.scan_count += 1
            self.set_status(
                gettext("Scanning game variants ({count} scanned)").format(
                    count=self.scan_count), variant_uuid)

            doc = game_database.get_game_values(variant_id)

            file_list_json = doc.get("file_list", "")
            if not file_list_json:
                # not a game variant... (parent game only probably)
                game_rows.append(row)
                continue

            entry_type = int(doc.get("_type", "0"))
            if (entry_type & GAME_ENTRY_TYPE_VARIANT) == 0:
                # game entry is not tagged with variant -- add to game list
                # instead
                game_rows.append(row)
                continue

            helper.variant_seen(variant_uuid)

            all_files_found = True
            try:
                file_list = json.loads(file_list_json)
            except Exception:
                # invalid JSON string
                # FIXME: log error
                all_files_found = False
                file_list = []

            for file_item in file_list:
                if file_item["name"].endswith("/"):
                    # skip directory entries:
                    continue
                result = self.fsgs.file.check_sha1(file_item["sha1"])
                if not result:
                    all_files_found = False
                    break

            if all_files_found:
                have_variant = 4
            elif doc.get("download_file", ""):
                have_variant = 2
            elif doc.get("download_page", ""):
                have_variant = 1
            else:
                have_variant = 0

            parent_uuid = doc.get("parent_uuid", "")
            variant_name = doc.get("variant_name", "")

            # the following is used by the FS Game Center frontend

            game_variant_id = existing_variant[2]
            if not game_variant_id:
                # variant is not in database
                database_cursor.execute(
                    "INSERT INTO game_variant (uuid) VALUES (?)",
                    (variant_uuid,))
                game_variant_id = database_cursor.lastrowid

            database_cursor.execute(
                "UPDATE game_variant SET name = ?, game_uuid = ?, have = ?, "
                "update_stamp = ?, database = ? WHERE id = ?",
                (variant_name, parent_uuid, have_variant, update_stamp,
                 database_name, game_variant_id))

            # ensure_updated_games.add(parent_uuid)

        for row in game_rows:
            if self.stop_check():
                return

            game_id, game_uuid_bin = row
            game_uuid = binary_to_uuid(game_uuid_bin)
            update_stamp = game_id

            existing_game = helper.existing_games.get(
                game_uuid, (None, None, None))

            if update_stamp == existing_game[0]:
                # after the loop has run its course, games to be removed
                # are left in existing_games
                helper.game_seen(game_uuid)
                continue

            self.scan_count += 1
            self.set_status(gettext("Scanning games ({count} scanned)").format(
                count=self.scan_count), game_uuid)

            doc = game_database.get_game_values(game_id)

            entry_type = int(doc.get("_type", "0"))
            if (entry_type & GAME_ENTRY_TYPE_GAME) == 0:
                continue

            # after the loop has run its course, games to be removed
            # are left in existing_games
            try:
                del helper.existing_games[game_uuid]
            except KeyError:
                pass

            game_name = doc.get("game_name", "")
            game_subtitle = doc.get("game_subtitle", "")

            platform = doc.get("platform", "")
            tags = doc.get("tags", "")
            year = doc.get("year", "")
            publisher = doc.get("publisher", "")

            front_sha1 = doc.get("front_sha1", "")
            title_sha1 = doc.get("title_sha1", "")
            screen1_sha1 = doc.get("screen1_sha1", "")
            screen2_sha1 = doc.get("screen2_sha1", "")
            screen3_sha1 = doc.get("screen3_sha1", "")
            screen4_sha1 = doc.get("screen4_sha1", "")
            screen5_sha1 = doc.get("screen5_sha1", "")
            thumb_sha1 = doc.get("thumb_sha1", "")
            backdrop_sha1 = doc.get("backdrop_sha1", "")

            sort_key = doc.get("sort_key", "")
            if not sort_key:
                # FIXME: handle the/a (etc)
                sort_key = game_name.lower()

            game_id = existing_game[2]
            if not game_id:
                # game is not in database
                database_cursor.execute(
                    "INSERT INTO game (uuid) VALUES (?)", (game_uuid,))
                game_id = database_cursor.lastrowid

            search_terms = set()
            for key in ["game_name", "full_name", "game_name_alt",
                        "search_terms", "game_subtitle"]:
                value = doc.get(key, "")
                if value:
                    search_terms.update(GameNameUtil.extract_index_terms(
                        value))

            letter = ""
            if len(sort_key) > 0:
                letter = sort_key[0].lower()
            if letter in "abcdefghijklmnopqrstuvwxyz":
                pass
            elif letter in "0123456789":
                letter = "#"
            else:
                letter = "?"
            search_terms.add("l:" + letter)
            for tag in tags.split(","):
                tag = tag.strip().lower()
                search_terms.add("t:" + tag)
            if year:
                search_terms.add("y:" + str(year))
            if platform:
                search_terms.add("s:" + platform.lower())

            if thumb_sha1:
                search_terms.add("t:thumb")
            if backdrop_sha1:
                search_terms.add("t:backdrop")
                backdrop_image = "sha1:{}/{}/{}/{}/{}".format(
                    backdrop_sha1,
                    doc.get("backdrop_zoom", "1.0"),
                    doc.get("backdrop_zoom", "1.0"),
                    doc.get("backdrop_halign", "0.5"),
                    doc.get("backdrop_valign", "0.5"))
            else:
                backdrop_image = ""

            min_players = 0
            max_players = 0
            sim_players = 0
            players = doc.get("players", "")
            if players == "1":
                min_players = max_players = 1
                search_terms.add("p:1")
            elif players:
                try:
                    parts1 = players.split("-")
                    parts2 = parts1[1].split("(")
                    min_players = int(parts1[0].strip())
                    max_players = int(parts2[0].strip())
                    sim_players = int(parts2[1].strip(" )"))
                except Exception as e:
                    print("error parsing players")
                    print(repr(e))
            if min_players > 0:
                if max_players > 0:
                    # we ignore players = 1 here, that is reserved for games
                    # with max 1 players
                    for i in range(min_players + 1, max_players + 1):
                        search_terms.add("p:{0}".format(i))
                if sim_players > 0:
                    # we ignore players = 1 here, that is reserved for games
                    # with max 1 players
                    for i in range(min_players + 1, sim_players + 1):
                        search_terms.add("p:{0}s".format(i))

            database_cursor.execute(
                "UPDATE game SET name = ?, update_stamp = ?, sort_key = ?, "
                "platform = ?, "
                "publisher = ?, year = ?, front_image = ?, title_image = ?, "
                "screen1_image = ?, screen2_image = ?, screen3_image = ?, "
                "screen4_image = ?, screen5_image = ?, "
                "thumb_image = ?, backdrop_image = ?, "
                "adult = ?, subtitle = ? WHERE id = ?",
                (game_name, update_stamp, sort_key, platform,
                 publisher or "", year or 0,
                 "sha1:" + front_sha1 if front_sha1 else "",
                 "sha1:" + title_sha1 if title_sha1 else "",
                 "sha1:" + screen1_sha1 if screen1_sha1 else "",
                 "sha1:" + screen2_sha1 if screen2_sha1 else "",
                 "sha1:" + screen3_sha1 if screen3_sha1 else "",
                 "sha1:" + screen4_sha1 if screen4_sha1 else "",
                 "sha1:" + screen5_sha1 if screen5_sha1 else "",
                 "sha1:" + thumb_sha1 if thumb_sha1 else "",
                 backdrop_image,
                 1 if "t:adult" in search_terms else None,
                 game_subtitle,
                 game_id))

            helper.database.update_game_search_terms(game_id, search_terms)


class ScanHelper(object):

    def __init__(self, database):
        self.database = database
        database_cursor = self.database.cursor()

        database_cursor.execute(
            "SELECT uuid, update_stamp, have, id FROM game "
            "WHERE uuid IS NOT NULL")
        self.existing_games = {}
        for row in database_cursor:
            self.existing_games[row[0]] = row[1], row[2], row[3]
        database_cursor.execute(
            "SELECT uuid, update_stamp, have, id FROM game_variant")
        self.existing_variants = {}
        for row in database_cursor:
            self.existing_variants[row[0]] = row[1], row[2], row[3]

        self.file_stamps = FileDatabase.get_instance().get_last_event_stamps()
        cached_file_stamps = self.database.get_last_file_event_stamps()
        self.added_files = self.file_stamps["last_file_insert"] != \
            cached_file_stamps["last_file_insert"]
        self.deleted_files = self.file_stamps["last_file_delete"] != \
            cached_file_stamps["last_file_delete"]

    def game_seen(self, seen_game_uuid):
        # after the loop has run its course, games to be removed
        # are left in existing_games
        try:
            del self.existing_games[seen_game_uuid]
        except KeyError:
            pass

    def variant_seen(self, seen_variant_uuid):
        # after the loop has run its course, variants to be removed
        # are left in existing_variants
        try:
            del self.existing_variants[seen_variant_uuid]
        except KeyError:
            pass

    def finish(self):
        database_cursor = self.database.cursor()

        # variants left in this list must now be deleted
        for row in self.existing_variants.values():
            variant_id = row[2]
            database_cursor.execute(
                "DELETE FROM game_variant WHERE id = ?", (variant_id,))

        # games left in this list must now be deleted
        for row in self.existing_games.values():
            game_id = row[2]
            database_cursor.execute(
                "DELETE FROM game WHERE id = ?", (game_id,))

        database_cursor.execute(
            "SELECT count(*) FROM game WHERE uuid IS NOT NULL "
            "AND (have IS NULL OR have != (SELECT coalesce(max(have), 0) "
            "FROM game_variant WHERE game_uuid = game.uuid))")
        update_rows = database_cursor.fetchone()[0]
        print(update_rows, "game entries need update for have field")
        if update_rows > 0:
            database_cursor.execute(
                "UPDATE game SET have = (SELECT coalesce(max(have), 0) FROM "
                "game_variant WHERE game_uuid = game.uuid) WHERE uuid IS NOT "
                "NULL AND (have IS NULL OR have != (SELECT coalesce(max("
                "have), 0) FROM game_variant WHERE game_uuid = game.uuid))")
        FileDatabase.get_instance().get_last_event_stamps()
        self.database.update_last_file_event_stamps(self.file_stamps)


def binary_to_uuid(v):
    v = hexlify(v).decode("ASCII")
    return "{0}-{1}-{2}-{3}-{4}".format(
        v[0:8], v[8:12], v[12:16], v[16:20], v[20:32])
