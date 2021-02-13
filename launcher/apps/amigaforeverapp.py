import os

from fsgamesys.context import FSGameSystemContext
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.input.enumeratehelper import EnumerateHelper
from fsgamesys.platforms.platform import PlatformHandler


def app_main():
    from launcher.launcherapp import LauncherApp

    launcherapp = LauncherApp()

    gscontext = FSGameSystemContext()
    print("\n\n\n")
    # print(gscontext.config.items())
    config = gscontext.config
    config.set("amiga_model", "A4000")

    amigaforeverdir = os.path.join(
        FSGSDirectories.get_base_dir(), "AmigaForever"
    )
    amigafilesdir = os.path.join(amigaforeverdir, "Amiga Files")
    shareddir = os.path.join(amigafilesdir, "Shared")
    romdir = os.path.join(shareddir, "rom")
    systemdir = os.path.join(shareddir, "dir", "System")
    workdir = os.path.join(shareddir, "dir", "Work")
    config.set(
        "kickstart_file", os.path.join(romdir, "amiga-os-310-a4000.rom")
    )
    # FIXME: Shouldn't be necessary...
    config.set(
        "x_kickstart_file", os.path.join(romdir, "amiga-os-310-a4000.rom")
    )
    config.set("hard_drive_0", systemdir)
    config.set("hard_drive_1", workdir)

    # config.set("hard_drive_2", os.path.join(FSGSDirectories.get_base_dir(), "Work"))

    # config.set("zorro_iii_memory", "65536")
    config.set("graphics_card", "uaegfx")

    config.set("window_width", "800")
    config.set("window_height", "600")
    config.set("legacy", "1")

    print(gscontext.config.items())
    # sys.exit(1)
    # gscontext.config.set()

    platform_handler = PlatformHandler.create("amiga")
    driver = platform_handler.get_runner(gscontext)

    device_helper = EnumerateHelper()
    device_helper.default_port_selection(driver.ports, driver.options)

    driver.prepare()
    driver.install()
    # set_progress("__run__")
    driver.run()
    driver.wait()
    driver.finish()
