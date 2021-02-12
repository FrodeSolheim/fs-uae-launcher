import threading
import traceback

import requests

from fsbc.application import Application
from fscore.system import System
from fsbc.util import compare_versions, unused
from fstd.desktop import open_url_in_browser
from launcher.launcher_settings import LauncherSettings
from launcher.launcher_signal import LauncherSignal
from launcher.version import VERSION


class UpdateManager:
    @classmethod
    def run_update_check(cls):
        threading.Thread(target=cls.update_thread_function).start()

    @classmethod
    def update_thread_function(cls):
        try:
            cls._update_thread_function()
        except Exception:
            traceback.print_exc()

    @classmethod
    def series(cls):
        if "dev" in Application.instance().version:
            return "devel"
        elif "beta" in Application.instance().version:
            return "beta"
        return "stable"

    @classmethod
    def _update_thread_function(cls):
        if System.windows:
            platform = "windows"
        elif System.macos:
            platform = "macosx"
        elif System.linux:
            platform = "linux"
        else:
            platform = "other"
        url = f"https://fs-uae.net/{cls.series()}/latest-{platform}"
        r = requests.get(url)
        r.raise_for_status()
        version_str = r.text.strip()
        print("Latest version available:", version_str)
        print("Current version:", VERSION)
        result = compare_versions(version_str, VERSION)
        print("Update check result: ", result)
        if result > 0 and version_str != "9.9.9":
            web_url = "https://fs-uae.net/{0}/download/".format(cls.series())
            LauncherSignal.broadcast("update_available", version_str, web_url)
            # FIXME: Thread safety...
            # FIXME: Use above signal instead
            LauncherSettings.set("__update_available", version_str)

    @classmethod
    def start_update(cls, version_str):
        unused(version_str)
        web_url = "https://fs-uae.net/{0}/download/".format(cls.series())
        open_url_in_browser(web_url)
