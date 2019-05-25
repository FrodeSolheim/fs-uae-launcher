import sys
import platform
import webbrowser


def default_url_open_function(url: str):
    webbrowser.open(url)


_url_open_function = default_url_open_function


def open_url_in_browser(url: str) -> None:
    if _url_open_function:
        _url_open_function(url)


def set_open_url_in_browser_function(func):
    global _url_open_function
    _url_open_function = func


def is_running_gnome_3():
    import fstd.desktop.gnome3

    return fstd.desktop.gnome3.running_in_gnome_3()


def is_running_windows_10():
    if sys.platform != "win32":
        return False
    return platform.uname()[2] == "10"
