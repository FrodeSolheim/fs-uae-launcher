from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import time
import json
from binascii import hexlify
from fsgs import fsgs
from .Settings import Settings
from .I18N import gettext
from fsgs.FileDatabase import FileDatabase
from fsgs.GameDatabaseClient import GameDatabaseClient
from fsgs.GameDatabaseSynchronizer import GameDatabaseSynchronizer
from fsgs.util.GameNameUtil import GameNameUtil

# from fsgs.ogd.context import SynchronizerContext
# from fsgs.ogd.meta import MetaSynchronizer
from fsgs.ogd.locker import LockerSynchronizer


def binary_to_uuid(v):
    v = hexlify(v).decode("ASCII")
    return "{0}-{1}-{2}-{3}-{4}".format(
        v[0:8], v[8:12], v[12:16], v[16:20], v[20:32])


GAME_ENTRY_TYPE_GAME = 1 << 0
GAME_ENTRY_TYPE_VARIANT = 1 << 1


class GameScanner(object):

    def __init__(self, context, _, on_status=None, stop_check=None):
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

    def scan(self, database):
        self.set_status(
            gettext("Scanning games"), gettext("Please wait..."))

        self.set_status(gettext("Scanning configurations"),
                        gettext("Scanning game database entries..."))

        with fsgs.get_game_database() as game_database:
            #self.update_game_database(game_database)
            #if self.stop_check():
            #    return

            self.scan_game_database(database, game_database)
            if self.stop_check():
                return

    def update_game_database(self, database):
        with fsgs.get_game_database() as game_database:
            self._update_game_database(game_database)
            if self.stop_check():
                return

    def _update_game_database(self, game_database):
        game_database_client = GameDatabaseClient(game_database)
        synchronizer = GameDatabaseSynchronizer(
            self.context, game_database_client, on_status=self.on_status,
            stop_check=self.stop_check)
        synchronizer.username = "auth_token"
        synchronizer.password = Settings.get("database_auth")
        synchronizer.synchronize()

        synchronizer = LockerSynchronizer(
            self.context, on_status=self.on_status, stop_check=self.stop_check)
        synchronizer.synchronize()

    def scan_game_database(self, database, game_database):
        """

        :type game_database: fsgs.GameDatabase.GameDatabase
        :type database: fsgs.Database.Database
        """
        cursor = database.cursor()

        existing_games = {}
        cursor.execute("SELECT uuid, update_stamp, have, id FROM game "
                       "WHERE uuid IS NOT NULL")
        for row in cursor:
            existing_games[row[0]] = row[1], row[2], row[3]

        existing_variants = {}
        cursor.execute("SELECT uuid, update_stamp, have, id FROM game_variant")
        for row in cursor:
            existing_variants[row[0]] = row[1], row[2], row[3]

        # this holds a list of game entry UUIDs which must exist / be checked
        # after variants have been processed
        ensure_updated_games = set()

        file_stamps = FileDatabase.get_instance().get_last_event_stamps()
        cached_file_stamps = database.get_last_file_event_stamps()
        added_files = file_stamps["last_file_insert"] != \
            cached_file_stamps["last_file_insert"]
        deleted_files = file_stamps["last_file_delete"] != \
            cached_file_stamps["last_file_delete"]

        game_cursor = game_database.cursor()
        #game_cursor.execute(
        #    "SELECT a.uuid, a.game, a.variant, a.name, a.platform, "
        #    "a.downloadable, a.update_stamp, value, b.uuid, b.game, "
        #    "b.sort_key, "
        #    "b.year, b.publisher, b.front_sha1, b.title_sha1, "
        #    "b.screen1_sha1, b.screen2_sha1, b.screen3_sha1, "
        #    "b.screen4_sha1, b.screen5_sha1 "
        #    "FROM game a LEFT JOIN game b ON a.parent = b.id, value "
        #    "WHERE a.id = value.game AND value.status = 1 AND "
        #    "value.name = 'file_list' AND a.status > -30")

        # this list will contain game entries which are not variants
        game_rows = []

        game_cursor.execute("SELECT id, uuid FROM game WHERE data != ''")
        for row in game_cursor:
            if self.stop_check():
                return

            variant_id, variant_uuid_bin = row
            variant_uuid = binary_to_uuid(variant_uuid_bin)
            update_stamp = variant_id
            #(uuid, game_name, variant, alt_name, platform, downloadable,
            # update_stamp,
            # file_list_json, parent_uuid, parent_game, parent_sort_key, year,
            # publisher, front_sha1, title_sha1, screen1_sha1, screen2_sha1,
            # screen3_sha1, screen4_sha1, screen5_sha1) = row

            #if not file_list_json:
            #    # not a game variant (with files)
            #    continue

            existing_variant = existing_variants.get(
                variant_uuid, (None, None, None))

            def variant_seen(seen_variant_uuid):
                # after the loop has run its course, variants to be removed
                # are left in existing_variants
                try:
                    del existing_variants[seen_variant_uuid]
                except KeyError:
                    pass

            def game_seen(seem_game_uuid):
                # after the loop has run its course, games to be removed
                # are left in existing_games
                try:
                    del existing_games[seem_game_uuid]
                except KeyError:
                    pass

            if update_stamp == existing_variant[0]:
                # entry was already updated and has not changed
                if existing_variant[1] and not deleted_files:
                    # have this entry already and no files have been deleted
                    # since the last time

                    # print("skipping variant (no deleted files)")
                    variant_seen(variant_uuid)
                    continue
                if not existing_variant[1] and not added_files:
                    # do not have this entry, but no files have been added
                    # since the last time

                    # print("skipping variant (no added files)")
                    variant_seen(variant_uuid)
                    continue
            else:
                # when the game entry has changed, we always check it
                # regardless of file database status, since file_list may
                # have been changed, or download status... (or other info
                # needs to be corrected)
                pass

            #print("\nscanning", alt_name, update_stamp, existing_variant)

            self.scan_count += 1
            self.set_status(
                gettext("Scanning game variants ({count} scanned)").format(
                    count=self.scan_count), variant_uuid)

            #cursor.execute("SELECT data FROM game WHERE id = ?", (variant_id,))
            #doc = json.loads(cursor.fetchone()[0])
            #next_parent_uuid = doc.get("parent_uuid", "")
            #while next_parent_uuid:
            #    cursor.execute(
            #        "SELECT data FROM game WHERE uuid = ?",
            #        (sqlite3.Binary(unhexlify(next_parent_uuid)),))
            #    next_doc = json.loads(cursor.fetchone()[0])
            #    next_parent_uuid = next_doc.get("parent_uuid", "")
            #    # let child doc overwrite and append values to parent doc
            #    next_doc.update(doc)
            #    doc = next_doc
            #del next_parent_uuid
            #del next_doc

            doc = game_database.get_game_values(variant_id)

            file_list_json = doc.get("file_list", "")
            if not file_list_json:
                # not a game variant... (parent game only probably)
                game_rows.append(row)
                continue

            #print(sorted(doc.items()))
            entry_type = int(doc.get("_type", "0"))
            #print("\n\n\nentry type:", entry_type, "\n\n\n")
            if (entry_type & GAME_ENTRY_TYPE_VARIANT) == 0:
                # game entry is not tagged with variant -- add to game list
                # instead
                game_rows.append(row)
                continue

            variant_seen(variant_uuid)

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
                #location = fsgs.file.find_by_sha1(file_item["sha1"])
                #location = fsgs.file.check_sha1(file_item["sha1"])
                result = fsgs.file.check_sha1(file_item["sha1"])
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
            game_name = doc.get("game_name", "")
            platform_name = doc.get("platform", "")
            variant_name = doc.get("variant_name", "")
            if not game_name:
                alt_name = doc.get("alt_name", "")
                game_name = alt_name.split("(", 1)[0]

            name = "{0} ({1}, {2})".format(
                game_name, platform_name, variant_name)

            ## search = self.create_configuration_search(name)
            ## config_name = self.create_configuration_name(name)
            #
            #if not parent_uuid:
            #    have_variant = 0
            #
            ##    reference = parent_uuid
            ##    type = game_entry_type + 4
            ## else:
            ##    reference = uuid
            ##    type = game_entry_type
            #
            ## cursor = game_database.cursor()
            ## cursor.execute("SELECT like_rating, work_rating FROM game_rating "
            ##               "WHERE game = ?", (uuid,))
            ## row = cursor.fetchone()
            ## if row is None:
            ##    like_rating, work_rating = 0, 0
            ## else:
            ##    like_rating, work_rating = row
            #
            ## the following is used by FS-UAE Launcher for the combined
            ## game / configurations list
            #
            ## database.add_configuration(
            ##    path="", uuid=uuid, name=config_name, scan=self.scan_version,
            ##    search=search, type=type, reference=reference,
            ##    like_rating=like_rating, work_rating=work_rating)
            ##
            ## if parent_uuid:
            ##    parent_name = "{0}\n{1}".format(parent_game, platform)
            ##    database.ensure_game_configuration(
            ##        parent_uuid, parent_name, parent_sort_key,
            ##        scan=self.scan_version, type=game_entry_type)

            # the following is used by the FS Game Center frontend

            game_variant_id = existing_variant[2]
            if not game_variant_id:
                # variant is not in database
                cursor.execute("INSERT INTO game_variant (uuid) "
                               "VALUES (?)", (variant_uuid,))
                game_variant_id = cursor.lastrowid

            cursor.execute(
                "UPDATE game_variant SET name = ?, game_uuid = ?, have = ?, "
                "update_stamp = ? WHERE id = ?",
                (variant_name, parent_uuid, have_variant, update_stamp,
                 game_variant_id))

            ensure_updated_games.add(parent_uuid)

            # database.add_game_variant_new(
            #    uuid=uuid, name=name, game_uuid=parent_uuid,
            #    like_rating=like_rating, work_rating=work_rating,
            #    scanned=self.scan_version)

            # if parent_uuid:
            #     # parent_name = "{0}\n{1}".format(parent_game, platform)
            #     # database.ensure_game_configuration(parent_uuid, parent_name,
            #     #        parent_sort_key, scan=self.scan_version)
            #     year = year or 0
            #     publisher = publisher or ""
            #     front_sha1 = "sha1:" + front_sha1 if front_sha1 else ""
            #     title_sha1 = "sha1:" + title_sha1 if title_sha1 else ""
            #     screen1_sha1 = "sha1:" + screen1_sha1 if screen1_sha1 else ""
            #     screen2_sha1 = "sha1:" + screen2_sha1 if screen2_sha1 else ""
            #     screen3_sha1 = "sha1:" + screen3_sha1 if screen3_sha1 else ""
            #     screen4_sha1 = "sha1:" + screen4_sha1 if screen4_sha1 else ""
            #     screen5_sha1 = "sha1:" + screen5_sha1 if screen5_sha1 else ""
            #
            #     database.add_game_new(
            #         parent_uuid, parent_game, platform, year, publisher,
            #         front_sha1, title_sha1, screen1_sha1, screen2_sha1,
            #         screen3_sha1, screen4_sha1, screen5_sha1,
            #         parent_sort_key, scanned=self.scan_version)

        #game_cursor = game_database.cursor()
        #game_cursor.execute(
        #    "SELECT b.uuid, b.game, b.update_stamp, "
        #    "b.sort_key, b.platform, "
        #    "b.year, b.publisher, b.front_sha1, b.title_sha1, "
        #    "b.screen1_sha1, b.screen2_sha1, b.screen3_sha1, "
        #    "b.screen4_sha1, b.screen5_sha1, b.id "
        #    "FROM game b WHERE files = 0")
        #for row in game_cursor:
        for row in game_rows:
            if self.stop_check():
                return

            game_id, game_uuid_bin = row
            game_uuid = binary_to_uuid(game_uuid_bin)
            update_stamp = game_id

            # (game_uuid, game_name, update_stamp, sort_key, platform, year,
            #  publisher, front_sha1, title_sha1, screen1_sha1, screen2_sha1,
            #  screen3_sha1, screen4_sha1, screen5_sha1, game_id) = row

            existing_game = existing_games.get(
                game_uuid, (None, None, None))

            if update_stamp == existing_game[0]:
                # after the loop has run its course, games to be removed
                # are left in existing_games
                try:
                    del existing_games[game_uuid]
                except KeyError:
                    pass

                continue

            # print("\nscanning game", game_name, update_stamp, existing_game)

            self.scan_count += 1
            self.set_status(gettext("Scanning games ({count} scanned)").format(
                count=self.scan_count), game_uuid)

            # values = game_database_client.get_final_game_values(game_id)

            doc = game_database.get_game_values(game_id)

            #print(sorted(doc.items()))
            entry_type = int(doc.get("_type", "0"))
            #print("\n\n\nentry type:", entry_type, "\n\n\n")
            if (entry_type & GAME_ENTRY_TYPE_GAME) == 0:
                continue

            # after the loop has run its course, games to be removed
            # are left in existing_games
            try:
                del existing_games[game_uuid]
            except KeyError:
                pass

            #if not game_name:
            #    game_name = alt_name.split("(", 1)[0]
            #name = "{0} ({1}, {2})".format(game_name, platform, variant)
            game_name = doc.get("game_name", "")
            search = self.create_configuration_search(game_name)
            config_name = self.create_configuration_name(game_name)

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
            sort_key = doc.get("sort_key", "")
            if not sort_key:
                # FIXME: handle the/a (etc)
                sort_key = game_name.lower()

            game_id = existing_game[2]
            if not game_id:
                # game is not in database
                cursor.execute(
                    "INSERT INTO game (uuid) VALUES (?)", (game_uuid,))
                game_id = cursor.lastrowid

            search_terms = set()
            for key in ["game_name", "full_name", "game_name_alt",
                        "search_terms"]:
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

            cursor.execute(
                "UPDATE game SET name = ?, update_stamp = ?, sort_key = ?, "
                "platform = ?, "
                "publisher = ?, year = ?, front_image = ?, title_image = ?, "
                "screen1_image = ?, screen2_image = ?, screen3_image = ?, "
                "screen4_image = ?, screen5_image = ?, adult = ? "
                "WHERE id = ?",
                (game_name, update_stamp, sort_key, platform,
                 publisher or "", year or 0,
                 "sha1:" + front_sha1 if front_sha1 else "",
                 "sha1:" + title_sha1 if title_sha1 else "",
                 "sha1:" + screen1_sha1 if screen1_sha1 else "",
                 "sha1:" + screen2_sha1 if screen2_sha1 else "",
                 "sha1:" + screen3_sha1 if screen3_sha1 else "",
                 "sha1:" + screen4_sha1 if screen4_sha1 else "",
                 "sha1:" + screen5_sha1 if screen5_sha1 else "",
                 1 if "t:adult" in search_terms else None,
                 game_id))

            database.update_game_search_terms(game_id, search_terms)

        # print("a")
        # cursor.execute("SELECT game.id FROM game LEFT JOIN game_variant ON "
        #                "game.uuid = game_variant.game_uuid WHERE "
        #                "game_variant.id IS NULL")
        # print("b")
        # for row in cursor.fetchall():
        #     cursor.execute("DELETE FROM game WHERE id = ?", (row[0],))

        # variants left in this list must now be deleted
        for row in existing_variants.values():
            variant_id = row[2]
            cursor.execute("DELETE FROM game_variant WHERE id = ?",
                           (variant_id,))

        # games left in this list must now be deleted
        for row in existing_games.values():
            game_id = row[2]
            cursor.execute("DELETE FROM game WHERE id = ?", (game_id,))

        cursor.execute("SELECT count(*) FROM game WHERE uuid IS NOT NULL "
                       "AND (have IS NULL OR have "
                       "!= (SELECT coalesce(max(have), 0) FROM game_variant "
                       "WHERE game_uuid = game.uuid))")
        #if cursor.rowcount > 0:
        update_rows = cursor.fetchone()[0]
        print(update_rows, "game entries need update for have field")
        if update_rows > 0:
            #print("c1")
            cursor.execute(
                "UPDATE game SET have = (SELECT coalesce(max(have), 0) FROM "
                "game_variant WHERE game_uuid = game.uuid) WHERE uuid IS NOT "
                "NULL AND (have IS NULL OR have != (SELECT coalesce(max("
                "have), 0) FROM game_variant WHERE game_uuid = game.uuid))")
        #print("d")
        FileDatabase.get_instance().get_last_event_stamps()
        database.update_last_file_event_stamps(file_stamps)

    @classmethod
    def create_configuration_search(cls, name):
        return name.lower()

    @classmethod
    def create_configuration_name(cls, name):
        if "(" in name:
            primary, secondary = name.split("(", 1)
            secondary = secondary.replace(", ", " \u00b7 ")
            #name = primary.rstrip() + " \u2013 " + secondary.lstrip()
            name = primary.rstrip() + "\n" + secondary.lstrip()
            if name[-1] == ")":
                name = name[:-1]
            name = name.replace(") (", " \u00b7 ")
            name = name.replace(")(", " \u00b7 ")
        return name
