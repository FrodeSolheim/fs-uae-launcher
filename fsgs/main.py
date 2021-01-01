import io
import os
import sys
from configparser import ConfigParser

import fsbc.application
from fsgs.Database import Database
from fsgs.application import ApplicationMixin
from fsgs.context import fsgs
from fsgs.util.gamenameutil import GameNameUtil


class Application(ApplicationMixin, fsbc.application.Application):
    pass


def main():
    Application("fs-uae-game-system")

    if "--unsupported" in sys.argv:
        if "--http-server" in sys.argv:
            from fsgs.http.server import http_server_main

            return http_server_main()

    if len(sys.argv) < 3:
        print("")
        print("usage: fsgs run <game>")
        print("")
        print("game:")
        print(" - search term(s) identifying a single game")
        print(" - path to a .fsgs file")
        print(" - path to a recognized cartridge ROM or disk file format")
        print("")
        sys.exit(1)
    assert sys.argv[1] == "run"
    game_arg = " ".join(sys.argv[2:])
    print(game_arg)
    if os.path.exists(game_arg):
        load_file(game_arg)
    else:
        search = game_arg.lower()
        database = Database.instance()
        # cursor.execute("SELECT id FROM game WHERE name like")
        terms = GameNameUtil.extract_search_terms(search)
        found_games = database.find_games_new(" ".join(terms))
        games = []
        for game in found_games:
            print(list(game))
            if game[0]:
                # only process entries with a game uuid
                games.append(game)
        game_uuid = None
        if len(games) == 0:
            print("no games found")
            sys.exit(2)
        if len(games) > 1:
            matches = 0
            for row in games:
                if row[1].lower() == search:
                    if game_uuid is None:
                        game_uuid = row[0]
                        matches += 1
            if matches != 1:
                print("")
                print("More than one game matches:")
                print("")
                for row in games:
                    print("    {0} ({1})".format(row[1], row[2]))
                    print("        {0}".format(row[0]))
                print("")
                sys.exit(3)
        game_uuid = games[0][0]
        assert game_uuid
        variant_uuid = find_preferred_variant(game_uuid)
        load_game_variant(variant_uuid)
    fsgs.run_game()


def find_preferred_variant(game_uuid):
    return fsgs.find_preferred_game_variant(game_uuid)


def load_game_variant(variant_uuid):
    return fsgs.load_game_variant(variant_uuid)


def load_file(path):
    config = {}
    name, ext = os.path.splitext(path)
    if ext in [".fs-uae", ".fsgs"]:
        return load_config_file(path)
    elif ext == ".st":
        config["platform"] = "atari-st"
        config["floppy_drive_0"] = path
    elif ext in [".adf", ".dms", ".ipf"]:
        config["platform"] = "amiga"
        config["floppy_drive_0"] = path
    elif ext in [".tap"]:
        config["platform"] = "commodore-64"
        config["tape_drive"] = path
    if config:
        load_config(config)


def load_config_file(fsgs_file):
    cp = ConfigParser()
    with io.open(fsgs_file, "r", encoding="UTF-8") as f:
        cp.read_file(f)
    config = {}
    if cp.has_section("fsgs"):
        for key in cp.options("fsgs"):
            value = cp.get("fsgs", key)
            config[key.lower().replace("-", "_")] = value
    load_config(config)


def load_config(config):
    fsgs.config.load(config)
    fsgs.game.platform.id = config["platform"]
    fsgs.game.uuid = "7bc9ae8b-e454-4108-87fe-6aac09cfb1e9"
    fsgs.game.name = "Default Game"
    fsgs.game.variant.uuid = "973d787f-2cc4-4d8d-b0c1-1bd911ef407a"
    fsgs.game.variant.name = "Default Variant"
