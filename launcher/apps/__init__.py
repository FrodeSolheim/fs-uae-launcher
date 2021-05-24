#!/usr/bin/env python3
import sys

import fsgamesys
import launcher.version
from fscore.settings import Settings
from fsgamesys.product import Product
from launcher.option import Option


def find_app(app):
    print("find_app", app)
    if app in ["launcher", "fs-uae-launcher"]:
        app = "SYS:Launcher"

    # elif app in ["fs-fuse-launcher", "fs-fuse"]:
    #     app = configure_launcher_app(
    #         "FS-Fuse", [Option.SPECTRUM_DATABASE], "spectrum", "#c46262"
    #     )
    # elif app in ["fs-mame-launcher", "fs-mame"]:
    #     app = configure_launcher_app(
    #         "FS-MAME", [Option.ARCADE_DATABASE], "arcade", "#c46262"
    #     )
    # elif app in ["openretro-launcher", "openretro"]:
    #     app = configure_launcher_app(
    #         "OpenRetro",
    #         fsgamesys.OPENRETRO_DEFAULT_DATABASES,
    #         "amiga",
    #         # "#945ebe",
    #         # "#444444",
    #         None,
    #     )

    if ":" in app:
        from functools import partial

        from launcher.apps.launcher2 import wsopen_main

        app_main = partial(wsopen_main, app)

    elif app in ["fs-uae-launcher-legacy"]:
        from launcher.apps.fs_uae_launcher import app_main
    elif app in ["arcade", "fs-uae-arcade"]:
        from launcher.apps.fs_uae_arcade import app_main
    elif app in ["workspace"]:
        from launcher.apps.workspace import app_main
    elif app == "fs-uae-netplay-server":
        from launcher.apps.fs_uae_netplay_server import app_main
    elif app == "fs-game-center":
        from launcher.apps.fs_game_center import app_main
    elif app in ["dump-game-database", "game-database-dumper"]:
        from fsgamesys.gamedb.game_database_dumper import (
            game_database_dumper_main,
        )

        app_main = game_database_dumper_main

    elif app in ["fsgs", "fs-game-runner"]:
        from launcher.apps.fsgs import app_main
    elif app == "list-plugins":
        from launcher.apps.listplugins import app_main
    elif app == "list-dirs":
        from launcher.apps.listdirs import app_main

    elif app == "AmigaForever:AmigaForever":
        from launcher.apps.amigaforeverapp import app_main

    elif app in ["dosbox", "dosbox-fs"]:
        from launcher.apps.dosbox_fs import app_main
    elif app in ["mame", "mame-fs"]:
        from launcher.apps.mame_fs import app_main
    elif app in ["mednafen", "mednafen-fs"]:
        from launcher.apps.mednafen_fs import app_main
    elif app in ["libretro-nestopia"]:
        from launcher.apps.libretro_nestopia import app_main

    elif app in ["uade", "uade-fs"]:
        from launcher.apps.uade_fs import app_main
    elif app in ["x64sc", "x64sc-fs"]:
        from launcher.apps.x64sc_fs import app_main
    else:
        return None

    return app_main


def main(app_name: str = "") -> None:
    # FIXME: This entire module is a mess and should be rewritten

    # Check deprecated/legacy app options.
    if "--server" in sys.argv:
        sys.argv.remove("--server")
        app_name = "fs-uae-netplay-server"
    if "--arcade" in sys.argv:
        sys.argv.remove("--arcade")
        app_name = "fs-uae-arcade"
    if "--fs-uae-arcade" in sys.argv:
        sys.argv.remove("--fs-uae-arcade")
        app_name = "fs-uae-arcade"
    if sys.argv[0].endswith("fs-game-center"):
        app_name = "fs-game-center"
    if len(sys.argv) > 1:
        if sys.argv[1] == "xdftool":
            app_name = "xdftool"
            del sys.argv[1]
    if "--xdftool" in sys.argv:
        sys.argv.remove("--xdftool")
        app_name = "xdftool"
    # Check new app option.
    for arg in sys.argv:
        if arg.startswith("--app="):
            app_name = arg[6:]
            sys.argv.remove(arg)

    import fsgamesys

    if "--openretro" in sys.argv:
        sys.argv.remove("--openretro")
        app_name = "openretro-launcher"
        # Product.base_name = "OpenRetro"
        # fsgamesys.openretro = True
        # for option_name in fsgamesys.OPENRETRO_DEFAULT_DATABASES:
        #     Option.get(option_name)["default"] = "1"

    # Check for (fake) version override
    for arg in sys.argv:
        if arg.startswith("--") and "=" in arg:
            key, value = arg[2:].split("=", 1)
            key = key.replace("-", "_")
            if key == "fake_version":
                launcher.version.VERSION = value

    if app_name == "xdftool":
        sys.argv[0] = "xdftool"
        import amitools.tools.xdftool

        sys.exit(amitools.tools.xdftool.main())

    app_main = None
    if app_main is None:
        if app_name:
            app_main = find_app(app_name)
        elif len(sys.argv) > 1:
            app_main = find_app(sys.argv[1])
            if app_main is not None:
                # Remove app name from sys.argv
                del sys.argv[1]

    print(app_main, app_name)
    sys.exit(1)

    if app_main is None and not app_name:
        app_name = "fs-uae-launcher"
        app_main = find_app(app_name)
    # if openretro:
    #     if app_name == "fs-uae-launcher":
    #         app_name = "openretro-launcher"
    #     elif app_name == "fs-uae-arcade":
    #         app_name = "openretro-arcade"

    import socket

    socket.setdefaulttimeout(30.0)
    from fsbc.init import initialize_application

    initialize_application(app_name, version=launcher.version.VERSION)

    if app_main is None:
        print("No valid app specified", file=sys.stderr)
        sys.exit(1)
    app_main()
