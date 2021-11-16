import os

from fsgamesys.config.configevent import ConfigEvent
from fsgamesys.options.constants2 import (
    CONFIG_PATH__,
    GAME_NAME,
    PROGRESS__,
    RUNNING__,
)
from fsui import Button, Color, Font, HorizontalLayout, Icon, Label, Panel
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.settings.fullscreentogglebutton import FullscreenToggleButton
from launcher.settings.monitorbutton import MonitorButton
from launcher.settings.volumebutton import VolumeButton
from launcher.ui2.screenshotspanel import ScreenshotsPanel
from launcher.ui2.startbutton import StartButton
from system.classes.configdispatch import ConfigDispatch


class Launcher2LaunchPanel(Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        horilayout = HorizontalLayout()
        # Using 6 for top/bottom margins so final height is 28 + 2 * 6 = 40
        # (and 60 with 2 * 10 spacing in outside that).
        self.layout.add(
            horilayout,
            fill=True,
            expand=True,
            margin_top=6,
            margin_right=20,
            margin_bottom=6,
            margin_left=10,
        )

        self.statuslabel = Label(self, "")
        horilayout.add(
            self.statuslabel, fill=True, expand=True, margin_left=10
        )
        self.cancelbutton = Button(
            self, gettext("Cancel"), icon=Icon("flag_red", "pkg:launcher")
        )
        self.cancelbutton.set_min_width(StartButton.MIN_WIDTH)
        self.cancelbutton.activated.connect(self.__on_cancel)
        horilayout.add(self.cancelbutton, fill=True, margin_left=10)
        # self.statuslabel.hide()
        # self.cancelbutton.hide()

        # horilayout.add_spacer(0, expand=True)
        self.volumebutton = VolumeButton(self)
        horilayout.add(self.volumebutton, fill=True, margin_left=10)
        self.volumebutton.disable()  # Currently not implemented properly

        self.monitorbutton = MonitorButton(self)
        horilayout.add(self.monitorbutton, fill=True, margin_left=10)
        # self.monitorbutton.disable()  # Currently not implemented properly

        self.fullscreentogglebutton = FullscreenToggleButton(self)
        horilayout.add(self.fullscreentogglebutton, fill=True, margin_left=10)
        self.startbutton = StartButton(self, dialog=False)
        horilayout.add(self.startbutton, fill=True, margin_left=10)

        self.title_font = Font.from_description("Saira Condensed Semi-Bold 22")

        self._is_running: bool = False
        self._config_path: str = ""
        self._game_name: str = ""
        self._display_name: str = ""
        ConfigDispatch(
            self,
            {
                CONFIG_PATH__: self.__on_config_path_config,
                GAME_NAME: self.__on_game_name_config,
                PROGRESS__: self.__on_progress_config,
                RUNNING__: self.__on_running_config,
            },
        )

    def __on_cancel(self) -> None:
        print("FIXME: CANCEL BUTTON DOES NOTHING")
        pass

    def __on_config_path_config(self, event: ConfigEvent) -> None:
        self._config_path = event.value
        self.update_display_name()

    def __on_game_name_config(self, event: ConfigEvent) -> None:
        self._game_name = event.value
        self.update_display_name()

    def display_name(self, *, config_path: str, game_name: str) -> str:
        if game_name:
            return game_name
        else:
            config_filename = os.path.basename(config_path)
            config_name = os.path.splitext(config_filename)[0]
            return config_name

    def on_paint(self) -> None:
        x = 20
        height = self.height()
        dc = self.create_dc()
        dc.set_font(self.title_font)
        # text = self.display_name(
        #     config_path=self._config_path, game_name=self._game_name
        # )
        # text = "Indiana Jones and the Fate of Atlantis: The Action Game"
        # text = "3D World Boxing"
        # text = "Lotus Turbo Challenge 2"
        text = self._display_name
        dc.set_text_color(Color(0x222222))
        _, th = dc.measure_text(text)
        dc.draw_text(text, x, (height - th) // 2)

    def __on_progress_config(self, event: ConfigEvent) -> None:
        self.statuslabel.set_text(event.value)

    def __on_running_config(self, event: ConfigEvent) -> None:
        self._is_running = bool(event.value)
        # self.cancelbutton.set_enabled(self._is_running)
        # self.statuslabel.set_visible(self._is_running)
        self.cancelbutton.set_visible(self._is_running)

        self.volumebutton.set_visible(not self._is_running)
        self.monitorbutton.set_visible(not self._is_running)
        self.fullscreentogglebutton.set_visible(not self._is_running)
        self.startbutton.set_visible(not self._is_running)
        if not self._is_running:
            self.statuslabel.set_text("")
        self.layout.update()
        self.update_display_name()

    def update_display_name(self) -> None:
        if self._is_running:
            new_display_name = ""
        else:
            new_display_name = self.display_name(
                config_path=self._config_path, game_name=self._game_name
            )
        if new_display_name != self._display_name:
            self._display_name = new_display_name
            self.refresh()


class Launcher2BottomPanel(Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        # panel = Panel(self)
        # panel.set_min_height(1)
        # panel.set_background_color(Color(0x888888))
        # self.layout.add(panel, fill=True)

        self.layout.add_spacer(10)

        self.launchpanel = Launcher2LaunchPanel(self)
        self.layout.add(self.launchpanel, fill=True)

        # self.layout.add_spacer(5)

        self.screenshotspanel = ScreenshotsPanel(self)
        self.layout.add(self.screenshotspanel, expand=True, fill=True)

        self.layout.add_spacer(10)

        # self.set_min_height(200)

        # Make sure that the height cannot collapse below the height of the
        # Launch button bar + associated padding.
        self.set_min_height(self.launchpanel.get_min_height(0) + 10 + 10)

    def getPreferredInitialHeight(self) -> int:
        # FIXME: Remove magic numbers
        return self.get_min_height(0) + 10 + 150 + 10
