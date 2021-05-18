from typing import Optional

from fswidgets.types import WindowState
from launcher.launcher_settings import LauncherSettings


class LauncherSettings2:
    """Transition class for cleaning up settings mess."""

    @property
    def checkForUpdates(self) -> bool:
        return self.get("check_for_updates") != "0"

    def get(self, key: str) -> str:
        return LauncherSettings.get(key)

    def set(self, key: str, value: str):
        LauncherSettings.set(key, value)

    def getLauncherBottomSplit(self):
        try:
            split = int(self.get("launcher_window_bottom_split"))
        except ValueError:
            return None
        return split

    def getLauncherMainSplit(self):
        try:
            split = int(self.get("launcher_window_main_split"))
        except ValueError:
            return None
        return split

    def getLauncherWindowState(self) -> Optional[WindowState]:
        try:
            x = int(self.get("launcher_window_x"))
            y = int(self.get("launcher_window_y"))
            width = int(self.get("launcher_window_width"))
            height = int(self.get("launcher_window_height"))
            maximized = int(self.get("launcher_window_maximized")) == 1
        except ValueError:
            return None
        if width and height:
            return WindowState(
                x=x, y=y, width=width, height=height, maximized=maximized
            )
        else:
            return None

    def setLauncherBottomSplit(self, split: int):
        self.set("launcher_window_bottom_split", str(split))

    def setLauncherMainSplit(self, split: int):
        self.set("launcher_window_main_split", str(split))

    def setLauncherWindowState(self, windowState: WindowState):
        self.set("launcher_window_x", str(windowState.x))
        self.set("launcher_window_y", str(windowState.y))
        self.set("launcher_window_width", str(windowState.width))
        self.set("launcher_window_height", str(windowState.height))
        self.set("launcher_window_maximized", str(int(windowState.maximized)))
