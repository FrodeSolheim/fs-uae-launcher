from threading import Thread

from fsgamesys.context import FSGameSystemContext
from fsgamesys.input.enumeratehelper import EnumerateHelper
from fsgamesys.platforms.platform import PlatformHandler


class RunHelper:
    @staticmethod
    def run_config_in_background(config):
        print(config)

        gscontext = FSGameSystemContext()
        gscontext.config.set(config.items())

        platform_handler = PlatformHandler.create("amiga")
        driver = platform_handler.get_runner(gscontext)

        device_helper = EnumerateHelper()
        device_helper.default_port_selection(driver.ports, driver.options)

        driver.prepare()
        driver.install()

        # import sys
        # sys.exit(1)

        # set_progress("__run__")
        driver.run()

        Thread(None, runhelper_cleanup_thread, args=(driver,)).start()


def runhelper_cleanup_thread(driver):
    print("whdload_cleanup_thread started")
    driver.wait()
    driver.finish()
    print("whdload_cleanup_thread done")
