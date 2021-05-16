from fsui import Color, HorizontalLayout, Image, Panel, get_window
from launcher.context import get_settings, get_theme
from launcher.settings import get_workspace_window_title
from launcher.settings.fullscreentogglebutton import FullscreenToggleButtonBase
from launcher.settings.monitorbutton import MonitorButtonBase
from launcher.settings.volumebutton import VolumeButtonBase
from system.classes.titlebarbutton import TitleBarButton
from system.exceptionhandler import exceptionhandler


class WorkspaceTitleBar(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = HorizontalLayout()

        self.title = get_workspace_window_title()
        self.dragging = False
        self.dragging_mouse_origin = (0, 0)
        self.dragging_window_origin = (0, 0)
        self.buttons = []

        theme = get_theme(self)
        self.height = theme.titlebar_height()
        self.set_min_height(self.height)

        button_size = (self.height, self.height)
        # fgcolor = theme.titlebar_fgcolor()
        # fgcolor_inactive = theme.titlebar_fgcolor_inactive()
        fgcolor = Color(0x000000)
        fgcolor_inactive = Color(0x000000)

        self.set_background_color(Color(0xFFFFFF))

        menu = True
        if menu:
            self.menubutton = TitleBarButton(
                self,
                icon_name="TitleBarMenu",
                size=button_size,
                fgcolor=fgcolor,
                fgcolor_inactive=fgcolor_inactive,
            )
            self.menubutton.activated.connect(self.__onMenu_activated)
            self.layout.add(self.menubutton)
            self.buttons.append(self.menubutton)
        else:
            self.menubutton = None

        self.layout.add_spacer(0, expand=True)

        self.volumebutton = VolumeButton(self)
        self.layout.add(self.volumebutton)
        self.monitorbutton = MonitorButton(self)
        self.layout.add(self.monitorbutton)
        self.fullscreenbutton = FullscreenToggleButton(self)
        self.layout.add(self.fullscreenbutton)

        self._window_active = True

        # parent.activated.connect(self.__on_window_activated)
        # parent.deactivated.connect(self.__on_window_deactivated)

        # FIXME: Would be better to do this via theme instead and get a theme
        # updated notification. Works well enough for now.

        for option in [
            "launcher_titlebar_font",
            "launcher_titlebar_height",
            "launcher_titlebar_uppercase",
        ]:
            self.on_setting(
                option,
                get_settings(self).get(option),
            )
        get_settings(self).add_listener(self)

    def onDestroy(self):
        get_settings(self).remove_listener(self)
        super().onDestroy()

    @exceptionhandler
    def on_setting(self, option, _):
        if option == "launcher_titlebar_font":
            self.refresh()
        elif option == "launcher_titlebar_uppercase":
            self.refresh()
        elif option == "launcher_titlebar_height":
            new_height = get_theme(self).titlebar_height()
            self.update_height(new_height)

    def update_height(self, new_height):
        if self.height == new_height:
            return
        self.height = new_height
        self.set_min_height(new_height)
        for button in self.buttons:
            button.set_size((new_height, new_height))
        get_window(self).layout.update()

    @exceptionhandler
    def on_paint(self):
        theme = get_theme(self)
        text = self.title
        if theme.titlebar_uppercase():
            text = text.upper()
        _, wh = self.size()
        dc = self.create_dc()
        dc.set_font(theme.titlebar_font())
        color = Color(0, 0, 0)
        dc.set_text_color(color)
        _, th = dc.measure_text(text)
        if self.menubutton:
            # Adding width of button (same as height). Also, adding 6 gives
            # 20 pixels between edge of burger icon and start of text.
            x = self.height + 6
        else:
            x = 20
        y = (wh - th) // 2 + 1
        dc.draw_text(text, x, y)

    @exceptionhandler
    def __onMenu_activated(self):
        try:
            onMenu = self.window.onMenu
        except AttributeError:
            print(
                f"WARNING: Window {self.window} has menu enabled, but missing "
                "onMenu method"
            )
            return
        menu = onMenu()
        if menu is None:
            return
        print("FIXME: Open menu")
        # menu.open()
        self.popup_menu(menu, (0, self.height))


class ButtonWrapper(TitleBarButton):
    def __init__(self, parent, icons):
        print("ButtonWrapper.__init__")
        super().__init__(parent, image=icons[0], size=(40, 40))


class FullscreenToggleButton(FullscreenToggleButtonBase, ButtonWrapper):
    def __init__(self, parent):
        super().__init__(
            parent,
            [
                Image("launcher:/data/windowed_16.png"),
                Image("launcher:/data/fullscreen_16.png"),
            ],
        )
        self.set_tooltip(self.tooltip_text)
        self.set_min_width(40)


class MonitorButton(MonitorButtonBase, ButtonWrapper):
    def __init__(self, parent):
        super().__init__(
            parent,
            [
                Image("launcher:/data/16x16/monitor_left.png"),
                Image("launcher:/data/16x16/monitor_middle_left.png"),
                Image("launcher:/data/16x16/monitor_middle_right.png"),
                Image("launcher:/data/16x16/monitor_right.png"),
            ],
        )
        self.set_tooltip(self.tooltip_text)
        self.set_min_width(40)


class VolumeButton(VolumeButtonBase, ButtonWrapper):
    def __init__(self, parent):
        super().__init__(
            parent,
            [
                Image(
                    "launcher:/data/icons/audio-volume-high_16/audio-volume-high.png"
                ),
                Image(
                    "launcher:/data/icons/audio-volume-medium_16/audio-volume-medium.png"
                ),
                Image(
                    "launcher:/data/icons/audio-volume-low_16/audio-volume-low.png"
                ),
                Image(
                    "launcher:/data/icons/audio-volume-muted_16/audio-volume-muted.png"
                ),
            ],
        )
        self.set_tooltip(self.tooltip_text)
        self.set_min_width(40)
