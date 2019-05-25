import sys

from fsbc.settings import Settings
from fsgs.context import default_context


def app_main():
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)
    if len(args) == 0:
        print("Usage: fsgc [options] <game_uuid | variant_uuid>")
        return

    game_or_variant_uuid = args[-1]
    print(game_or_variant_uuid)

    fsgc = default_context()
    fsgc.load_game_by_uuid(game_or_variant_uuid)
    fsgc.config.add_from_argv()

    print("settings:fullscreen", Settings.instance()["fullscreen"])
    print("config:fullscreen", fsgc.config.get("fullscreen"))

    # sys.exit(1)
    # fsgc.run_game()

    from fsgs.platform import Platform

    platform = Platform.create(fsgc.game.platform.id)
    driver = platform.driver(fsgc)

    from fsgs.input.enumeratehelper import EnumerateHelper

    device_helper = EnumerateHelper()
    device_helper.default_port_selection(driver.ports, driver.options)

    print("")
    for port in driver.ports:
        print("Port", port.index)
        print(" ", port.type, [x["type"] for x in port.types])
        print(" ", port.device)
    print("")

    # sys.exit(1)

    driver.prepare()
    process = driver.run()
    process.wait()
    driver.finish()
