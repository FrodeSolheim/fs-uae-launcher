from urllib.request import urlopen
import traceback
import threading
from .Signal import Signal
from .Settings import Settings
from fsbc.Application import Application
from fsbc.system import windows, macosx, linux
from fsbc.util import compare_versions, unused
from fstd.desktop import open_url_in_browser


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
        return "stable"

    @classmethod
    def _update_thread_function(cls):
        if windows:
            platform = "windows"
        elif macosx:
            platform = "macosx"
        elif linux:
            platform = "linux"
        else:
            platform = "other"
        url = "http://fs-uae.net/{0}/latest-{1}".format(cls.series(), platform)
        f = urlopen(url)
        version_str = f.read().strip().decode("UTF-8")
        print("latest version available: ", version_str)
        print("current version: ", Application.instance().version)
        result = compare_versions(version_str, Application.instance().version)
        print("update check result: ", result)
        if result > 0 and version_str != "9.9.9":
            web_url = "http://fs-uae.net/{0}/download/".format(cls.series())
            Signal.broadcast("update_available", version_str, web_url)
            Settings.set("__update_available", version_str)

    @classmethod
    def start_update(cls, version_str):
        unused(version_str)
        web_url = "http://fs-uae.net/{0}/download/".format(cls.series())
        open_url_in_browser(web_url)
