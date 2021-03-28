import weakref
from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar, cast
from weakref import WeakMethod

import fsui
from fscore.observable import Disposable, Observable, mapOperator
from fsgamesys.platforms.platform import Platform
from fsui import HorizontalLayout, MultiLineLabel, Window
from launcher.fswidgets2.button import Button
from launcher.fswidgets2.flexcontainer import (
    FlexContainer,
    Style,
    VerticalFlexContainer,
)
from launcher.fswidgets2.flexlayout import FlexLayout
from launcher.fswidgets2.label import Label
from launcher.fswidgets2.parentstack import AsParent, ParentStack
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.option import Option
from launcher.settings.option_ui import OptionUI
from launcher.settings.platformsettingsdialog import PlatformSettingsDialog
from launcher.system.classes.shellobject import shellObject
from launcher.system.classes.windowcache import WindowCache
from launcher.system.classes.windowresizehandle import WindowResizeHandle
from launcher.system.prefs.components.baseprefspanel import BasePrefsPanel
from launcher.system.prefs.components.baseprefswindow import (
    BasePrefsWindow,
    BasePrefsWindow2,
)
from launcher.ui.IconButton import IconButton

# F = TypeVar("F", bound=Callable[..., Any])


# def constructor(function: F) -> F:
#     @wraps(function)
#     def wrapper(self, *args, **kwargs):
#         ParentStack.push(self)
#         try:
#             return function(*args, **kwargs)
#         finally:
#             assert ParentStack.pop() == self

#     return cast(F, wrapper)


@shellObject
class OpenRetroPrefs:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(OpenRetroPrefsWindow, **kwargs)


class OpenRetroPrefsWindow(BasePrefsWindow2):
    def __init__(self):
        super().__init__("OpenRetro preferences", OpenRetroPrefsPanel)


# class SettingsBehavior:
#     def __init__(self, parent, names):
#         parent.__settings_enable_behavior = self
#         self._parent = weakref.ref(parent)
#         self._names = set(names)
#         LauncherSettings.add_listener(self)
#         try:
#             parent.destroyed.connect(self.__on_parent_destroyed)
#         except AttributeError:
#             print(
#                 "WARNING: SettingsBehavior without remove_listener "
#                 "implementation"
#             )
#         for name in names:
#             # Broadcast initial value
#             self.on_setting(name, LauncherSettings.get(name))

#     def __on_parent_destroyed(self):
#         # print("SettingsBehavior: remove_listener", self._parent())
#         LauncherSettings.remove_listener(self)

#     def on_setting(self, key, value):
#         if key in self._names:
#             widget = self._parent()
#             try:
#                 func = getattr(widget, "on_{0}_setting".format(key))
#             except AttributeError:
#                 func = getattr(widget, "on_settings".format(key))
#                 func(key, value)
#             else:
#                 func(value)


# class SettingObservable:
#     def __init__(self, key):
#         # super().__init__(name)
#         self._key = key
#         self._value = "Heisann"
#         self._observer = None
#         LauncherSettings.add_listener(self)
#         self._value = LauncherSettings.get(self._key)

#     def __del__(self):
#         LauncherSettings.remove_listener(self)

#     def on_setting(self, key, value):
#         if self._key == key:
#             self._value = value
#             if self._observer is None:
#                 pass
#             else:
#                 # print(self._observer)
#                 # observer = self._observer()
#                 # if observer is None:
#                 #     print("Observer died")
#                 #     self._observer = None
#                 #     pass
#                 # else:
#                 #     observer(value)
#                 if isinstance(self._observer, WeakMethod):
#                     observer = self._observer()
#                     if observer is not None:
#                         observer(self.transform(value))
#                 else:
#                     self._observer.next(self.transform(value))
#             # observer = self._observer() if self._observer is None

#     def subscribe(self, observer):
#         # print("observer is", observer)
#         # self._observer = weakref.ref(observer)
#         if hasattr(observer, "__self__"):
#             self._observer = WeakMethod(observer)
#         else:
#             self._observer = observer

#     @property
#     def current(self):
#         return self.transform(self._value)

#     @property
#     def value(self):
#         return self.transform(self._value)

#     def transform(self, value):
#         return value


class SettingListener:
    def __init__(self, key, observer):
        self.key = key
        self.observer = observer

    def on_setting(self, key, value):
        print("SettingListener.on_setting", key, value)
        if self.key == key:
            self.observer.on_next(value)


class SettingObservable(Observable):
    listeners = []  # type: List[SettingListener]

    def __init__(self, key):
        def observe(observer, scheduler):
            print(" -- new listener")
            # def listener(key, value):
            #     if key ==
            #     observer.on_next(value)

            # Broadcast initial value
            observer.on_next(LauncherSettings.get(key))
            listener = SettingListener(key, observer)
            # HACK, BECAUSE LauncherSettings do not keep ref
            SettingObservable.listeners.append(listener)
            LauncherSettings.add_listener(listener)

            def dispose():
                SettingObservable.listeners.remove(listener)
                LauncherSettings.remove_listener(listener)

            return Disposable(dispose)
            # return Disposable(
            #     lambda: LauncherSettings.remove_listener(listener)
            # )

        super().__init__(observe)

    #     # super().__init__(name)
    #     self._key = key
    #     self._value = "Heisann"
    #     self._observer = None
    #     LauncherSettings.add_listener(self)
    #     self._value = LauncherSettings.get(self._key)

    # def __del__(self):
    #     LauncherSettings.remove_listener(self)

    # def on_setting(self, key, value):
    #     if self._key == key:
    #         self._value = value
    #         if self._observer is None:
    #             pass
    #         else:
    #             # print(self._observer)
    #             # observer = self._observer()
    #             # if observer is None:
    #             #     print("Observer died")
    #             #     self._observer = None
    #             #     pass
    #             # else:
    #             #     observer(value)
    #             if isinstance(self._observer, WeakMethod):
    #                 observer = self._observer()
    #                 if observer is not None:
    #                     observer(self.transform(value))
    #             else:
    #                 self._observer.next(self.transform(value))
    #         # observer = self._observer() if self._observer is None

    # def subscribe(self, observer):
    #     # print("observer is", observer)
    #     # self._observer = weakref.ref(observer)
    #     if hasattr(observer, "__self__"):
    #         self._observer = WeakMethod(observer)
    #     else:
    #         self._observer = observer

    # @property
    # def current(self):
    #     return self.transform(self._value)

    # @property
    # def value(self):
    #     return self.transform(self._value)

    # def transform(self, value):
    #     return value


class UsernameObservable(SettingObservable):
    def __init__(self):
        super().__init__("database_username")

    def transform(self, value):
        if value == "Foo":
            return "FooTransformed"
        return value


def username(x: str) -> str:
    if x == "Foo":
        return "Not logged in"
    return x


class LoginPanel(FlexContainer):
    def __init__(self):
        super().__init__(
            style={
                "backgroundColor": "#cccccc",
                "gap": 10,
                "padding": 10,
            }
        )
        with AsParent(self):
            Label(gettext("Currently logged in as:"))
            # Label("Username", style={"fontWeight": "bold", "flexGrow": 1})
            # from rx.core.typing import Observable
            # from rx.core.typing import Observable as ObservableT
            # from typing import Union
            # a = None  # type: Union[None, ObservableT[int]]
            # print(a)
            a = SettingObservable(
                "database_username"
            )  # x-type: ObservableT[int]
            Label(
                # UsernameObservable(),
                SettingObservable("database_username").pipe(
                    mapOperator(username),
                    # op.map(lambda x: "Not logged in " if x == "Foo" else x)
                ),
                style={"fontWeight": "bold", "flexGrow": 1},
            )
            Button(
                "Log in",
                enabled=SettingObservable("database_username").pipe(
                    mapOperator(lambda x: not x)
                ),
                onClick=self.onLogInButton,
            )
            Button(
                "Log out",
                enabled=SettingObservable("database_username"),
                onClick=self.onLogOutButton,
            )

    def onLogInButton(self):
        print("Log in button")
        # LauncherSettings.set("database_username", "FooBar")
        from launcher.system.wsopen import wsopen

        wsopen("SYS:Special/Login", window=self.getWindow())

    def onLogOutButton(self):
        print("Log out button")
        # LauncherSettings.set("database_username", "")
        # if LauncherSettings.get("database_username") == "Foo":
        #     LauncherSettings.set("database_username", "")
        # else:
        #     LauncherSettings.set("database_username", "Foo")
        from launcher.system.wsopen import wsopen

        wsopen("SYS:Special/Logout", window=self.getWindow())


class OpenRetroPrefsPanel(BasePrefsPanel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(20, 20, 20, 20)
        # self.layout.set_padding(10, 10, 10, 10)
        import fsui

        # self.layout.add(fsui.Button(self, "hei"))

        with AsParent(self):
            LoginPanel()

        self.add_section("Platforms")

        self.add_option(Option.PLATFORMS_FEATURE)

        self.hori_layout = None
        self.hori_counter = 0

        # if openretro or settings.get(Option.PLATFORMS_FEATURE) == "1":
        #     # self.add_section(gettext("Game Databases"))

        label = MultiLineLabel(
            self,
            gettext(
                "Note: This is an experimental feature. "
                "Additional plugins are needed."
            ),
            640,
        )
        self.layout.add(label, margin_top=20, margin_bottom=20)

        self.add_database_option(
            Platform.CPC, Option.CPC_DATABASE, "Amstrad CPC"
        )
        self.add_database_option(
            Platform.ARCADE, Option.ARCADE_DATABASE, "Arcade"
        )
        self.add_database_option(
            Platform.A7800, Option.A7800_DATABASE, "Atari 7800"
        )
        self.add_database_option(
            Platform.C64, Option.C64_DATABASE, "Commodore 64"
        )
        self.add_database_option(Platform.DOS, Option.DOS_DATABASE, "DOS")
        self.add_database_option(Platform.GB, Option.GB_DATABASE, "Game Boy")
        self.add_database_option(
            Platform.GBA, Option.GBA_DATABASE, "Game Boy Advance"
        )
        self.add_database_option(
            Platform.GBC, Option.GBC_DATABASE, "Game Boy Color"
        )
        self.add_database_option(
            Platform.SMS, Option.SMS_DATABASE, "Master System"
        )
        self.add_database_option(
            Platform.SMD, Option.SMD_DATABASE, "Mega Drive"
        )
        self.add_database_option(
            Platform.NEOGEO, Option.NEOGEO_DATABASE, "Neo-Geo"
        )
        self.add_database_option(Platform.NES, Option.NES_DATABASE, "Nintendo")
        self.add_database_option(
            Platform.PSX, Option.PSX_DATABASE, "PlayStation"
        )
        self.add_database_option(
            Platform.SNES, Option.SNES_DATABASE, "Super Nintendo"
        )
        self.add_database_option(Platform.ST, Option.ST_DATABASE, "Atari ST")
        self.add_database_option(
            Platform.TG16, Option.TG16_DATABASE, "TurboGrafx-16"
        )
        self.add_database_option(
            Platform.TGCD, Option.TGCD_DATABASE, "TurboGrafx-CD"
        )
        self.add_database_option(
            Platform.ZXS, Option.ZXS_DATABASE, "ZX Spectrum"
        )

        # label = fsui.MultiLineLabel(
        #     self, gettext(
        #         "Note: Support for additional game databases is an "
        #         "experimental feature and does not provide the "
        #         "same level of maturity as Amiga/CDTV/CD32. "
        #         "Also, additional plugins are needed to play the "
        #         "games."), 640)
        # self.layout.add(label, margin_top=20)

    def add_database_option(self, platform, name, description=""):
        # self.options_on_page.add(name)
        group = OptionUI.create_group(
            self, name, description=description, help_button=False
        )

        if self.hori_counter % 2 == 0:
            self.hori_layout = HorizontalLayout()
            self.layout.add(
                self.hori_layout,
                fill=True,
                margin_top=10,
                margin_bottom=10,
                margin_left=-10,
                margin_right=-10,
            )

        self.hori_layout.add(
            group,
            fill=True,
            expand=-1,
            margin=10,
            margin_top=0,
            margin_bottom=0,
        )
        self.hori_layout.add(
            PlatformSettingsButton(self, platform), margin_right=10
        )

        if self.hori_counter % 2 == 0:
            self.hori_layout.add_spacer(0)
        self.hori_counter += 1


class PlatformSettingsButton(IconButton):
    def __init__(self, parent, platform):
        super().__init__(parent, "16x16/settings.png")
        self.platform = platform
        self.set_enabled(
            len(PlatformSettingsDialog.option_list_for_platform(platform)) > 0
        )

    def on_activate(self):
        PlatformSettingsDialog.open(self.window, self.platform)
