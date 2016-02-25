import sys

from fsbc.settings import Settings
from fsgs.context import fsgs


def app_main():
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)
    if len(args) == 0:
        print("Usage: fs-game-runner [options] <game_uuid | variant_uuid>")
        return

    game_or_variant_uuid = args[-1]
    print(game_or_variant_uuid)

    fsgs.load_game_by_uuid(game_or_variant_uuid)
    fsgs.config.add_from_argv()
    print("settings:fullscreen", Settings.instance()["fullscreen"])
    print("config:fullscreen", fsgs.config.get("fullscreen"))
    fsgs.run_game()
