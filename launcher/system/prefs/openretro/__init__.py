from launcher.system.classes.windowcache import WindowCache
from launcher.system.prefs.common.baseprefswindow import BasePrefsWindow2
from launcher.system.prefs.openretro.openretroprefspanel import (
    OpenRetroPrefsPanel,
)

# def simple_window_cache(window_class, window_key, window=None, parent=None):
#     try:
#         win = window_registry[window_key]
#     except LookupError:
#         pass
#     else:
#         win.raise_and_activate()
#         return
#     win = window_class(None)

#     def remove_window():
#         del window_registry[window_key]

#     window_registry[window_key] = win
#     win.closed.connect(remove_window)
#     win.show()
#     # if parent is not None:
#     #     print("\n\nCENTER ON PARENT\n\n")
#     #     window.center_on_parent()
#     if window is not None:
#         print("\n\nCENTER ON WINDOW\n\n")
#         win.center_on_window(window)


def wsopen(window=None, **kwargs):
    # window = OpenRetroPrefsWindow()
    WindowCache.open(OpenRetroPrefsWindow, center_on_window=window)


class OpenRetroPrefsWindow(BasePrefsWindow2):
    def __init__(self):
        super().__init__("OpenRetro preferences", OpenRetroPrefsPanel)
