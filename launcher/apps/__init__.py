#!/usr/bin/env python3
import sys

import fstd.typing
import launcher.version

# Workaround to make import typing work without having it on the default
# python path (would confuse mypy).
from launcher.option import Option

sys.modules["typing"] = fstd.typing


def main():
    app = "fs-uae-launcher"

    # Check deprecated/legacy app options.
    if "--server" in sys.argv:
        sys.argv.remove("--server")
        app = "fs-uae-netplay-server"
    if "--arcade" in sys.argv:
        sys.argv.remove("--arcade")
        app = "fs-uae-arcade"
    if "--fs-uae-arcade" in sys.argv:
        sys.argv.remove("--fs-uae-arcade")
        app = "fs-uae-arcade"
    if sys.argv[0].endswith("fs-game-center"):
        app = "fs-game-center"
    if len(sys.argv) > 1:
        if sys.argv[1] == "xdftool":
            app = "xdftool"
            del sys.argv[1]
    if "--xdftool" in sys.argv:
        sys.argv.remove("--xdftool")
        app = "xdftool"

    import fsgs
    if "--openretro" in sys.argv:
        sys.argv.remove("--openretro")
        fsgs.product = "OpenRetro"
        fsgs.openretro = True
        Option.get(Option.ARCADE_DATABASE)["default"] = "1"
        Option.get(Option.ATARI_DATABASE)["default"] = "1"
        Option.get(Option.C64_DATABASE)["default"] = "1"
        Option.get(Option.CPC_DATABASE)["default"] = "1"
        Option.get(Option.DOS_DATABASE)["default"] = "1"
        Option.get(Option.GB_DATABASE)["default"] = "1"
        Option.get(Option.GBA_DATABASE)["default"] = "1"
        Option.get(Option.GBC_DATABASE)["default"] = "1"
        Option.get(Option.NES_DATABASE)["default"] = "1"
        Option.get(Option.PSX_DATABASE)["default"] = "1"
        Option.get(Option.SNES_DATABASE)["default"] = "1"
        Option.get(Option.ZXS_DATABASE)["default"] = "1"

    # Check new app option.
    for arg in sys.argv:
        if arg.startswith("--app="):
            app = arg[6:]
            sys.argv.remove(arg)

    # Check for (fake) version override
    for arg in sys.argv:
        if arg.startswith("--") and "=" in arg:
            key, value = arg[2:].split("=", 1)
            key = key.replace("-", "_")
            if key == "fake_version":
                launcher.version.VERSION = value

    import socket
    socket.setdefaulttimeout(30.0)

    if app == "xdftool":
        sys.argv[0] = "xdftool"
        import amitools.tools.xdftool
        sys.exit(amitools.tools.xdftool.main())

    from fsbc.init import initialize_application
    initialize_application(app, version=launcher.version.VERSION)

    if app in ["launcher", "fs-uae-launcher"]:
        from launcher.apps.fs_uae_launcher import app_main
    elif app in ["arcade", "fs-uae-arcade"]:
        from launcher.apps.fs_uae_arcade import app_main
    elif app in ["workspace"]:
        from launcher.apps.workspace import app_main
    elif app == "fs-uae-netplay-server":
        from launcher.apps.fs_uae_netplay_server import app_main
    elif app == "fs-game-center":
        from launcher.apps.fs_game_center import app_main
    elif app == "game-database-dumper":
        from fsgs.gamedb.game_database_dumper import game_database_dumper_main
        app_main = game_database_dumper_main
    elif app == "fs-game-runner":
        from launcher.apps.fs_game_runner import app_main
    elif app == "dosbox-fs":
        from launcher.apps.dosbox_fs import app_main
    elif app == "mame-fs":
        from launcher.apps.mame_fs import app_main
    elif app == "mednafen-fs":
        from launcher.apps.mednafen_fs import app_main
    elif app == "uade-fs":
        from launcher.apps.uade_fs import app_main
    elif app == "list-plugins":
        from launcher.apps.list_plugins import app_main
    elif app == "list-dirs":
        from launcher.apps.list_dirs import app_main
    else:
        raise Exception("Unknown app specified")
    app_main()
