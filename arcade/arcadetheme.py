import fsbc.settings as settings
from arcade.resources import resources
from fsgamesys.options.option import Option
from fsui.qt import QImage


class ArcadeTheme:
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        self.theme = settings.get(Option.ARCADE_THEME)
        if not self.theme:
            self.theme = "blue"

    def qimage(self, name: str) -> QImage:
        if self.theme != "blue":
            theme_path = "themes/{}/{}".format(self.theme, name)
            try:
                im = resources.resource_qt_image(theme_path)
            except LookupError:
                pass
            else:
                return im
        theme_path = "themes/blue/{}".format(name)
        im = resources.resource_qt_image(theme_path)
        return im
