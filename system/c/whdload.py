import os
from collections import defaultdict
from typing import List

from launcher.ws.shell import shell_hostpath, shell_realcase, shell_split

# FIXME
# from fsgamesys.amiga.whdload import populate_whdload_system_volume_2
from system.classes.runhelper import RunHelper

# FIXME: Consider preventing the same slave from being started twice at the
# same time (would be nice to be able to bring the existing  FS-UAE window to
# the front instead).


class WHDLoad:
    @classmethod
    def wsopen(cls, *, iconpath: str, tooltypes: List[str], **kwargs):
        print(f"WHDLoad.wsopen, iconpath={iconpath}, tooltypes ={tooltypes}")

        iconpath = shell_realcase(iconpath)
        slavedir, iconname = shell_split(iconpath)
        iconlabel = iconname
        if iconlabel.lower().endswith(".info"):
            iconlabel = iconlabel[:-5]

        config = defaultdict(str)

        destdir = "/tmp/whdload-FIXME"
        if not os.path.exists(destdir):
            os.makedirs(destdir)

        config["hard_drive_0"] = destdir
        config["hard_drive_0_label"] = "System"

        volumename = iconpath.split(":", 1)[0]
        volumedir = shell_hostpath(volumename + ":")

        config["hard_drive_1"] = volumedir
        config["hard_drive_1_label"] = volumename

        config["amiga_model"] = "A1200"
        config["fast_memory"] = "8192"

        config["window_title"] = iconlabel

        whdloadargs = []
        slave = ""
        for tooltype in tooltypes:
            if tooltype.lower().startswith("slave="):
                slave = tooltype[6:]
            elif tooltype.startswith("("):
                # Commented-out option
                pass
            else:
                whdloadargs.append(tooltype)
        whdloadargs.insert(0, slave)

        populate_whdload_system_volume_2(
            destdir,
            whdloadargs=" ".join(whdloadargs),
            slavedir=slavedir,
            config=config,
        )

        # return
        RunHelper.run_config_in_background(config)


#         print(config)

#         from fsgamesys.context import FSGameSystemContext

#         gscontext = FSGameSystemContext()
#         gscontext.config.set(config.items())

#         from fsgamesys.platforms.platform import PlatformHandler

#         platform_handler = PlatformHandler.create("amiga")
#         driver = platform_handler.get_runner(gscontext)

#         from fsgamesys.input.enumeratehelper import EnumerateHelper

#         device_helper = EnumerateHelper()
#         device_helper.default_port_selection(driver.ports, driver.options)

#         driver.prepare()
#         driver.install()

#         # import sys
#         # sys.exit(1)

#         # set_progress("__run__")
#         driver.run()

#         from threading import Thread

#         Thread(None, whdload_cleanup_thread, args=(driver,)).start()


# def whdload_cleanup_thread(driver):
#     print("whdload_cleanup_thread started")
#     driver.wait()
#     driver.finish()
#     print("whdload_cleanup_thread done")
