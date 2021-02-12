import fsbc.settings
from fscore.deprecated import deprecated


# def setting(name):
#     pass


# def default_setting(name):
#     pass


# def set_default_setting(name, value):
#     pass


class Settings:
    @staticmethod
    def get(key: str) -> str:
        return fsbc.settings.Settings.instance().get(key)

    @staticmethod
    def set(key: str, value: str) -> None:
        fsbc.settings.Settings.instance().set(key, value)

    # @staticmethod
    # def default(key: str):
    #     pass

    @staticmethod
    def set_default(key: str, value: str):
        fsbc.settings.Settings.instance().defaults[key] = value

    @deprecated
    @staticmethod
    def instance():
        return Settings
