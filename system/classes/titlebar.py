from typing import List, Optional

import fsui
from fsui import Panel
from fsui.qt.color import Color
from fswidgets.overrides import overrides
from fswidgets.widget import Widget
from launcher.context import get_settings, get_theme

from .titlebarbutton import TitleBarButton


class TitleBar(Panel):
    menubutton = Optional[TitleBarButton]
    minimizebutton = Optional[TitleBarButton]
    maximizebutton = Optional[TitleBarButton]
    closebutton = Optional[TitleBarButton]

    def __init__(
        self,
        parent: Widget,
        *,
        title: str = "",
        menu: bool = False,
        minimizable: bool = True,
        maximizable: bool = True,
        foreground_color: Optional[Color] = None,
        background_color: Optional[Color] = None,
        foreground_inactive_color: Optional[Color] = None,
        background_inactive_color: Optional[Color] = None,
    ):
        super().__init__(parent, forceRealParent=True)
        self.layout = fsui.HorizontalLayout()

        self.override_foreground_color = foreground_color
        self.override_background_color = background_color
        self.override_foreground_inactive_color = foreground_inactive_color
        self.override_background_inactive_color = background_inactive_color

        self.title = title
        self.dragging = False
        self.dragging_mouse_origin = (0, 0)
        self.dragging_window_origin = (0, 0)
        self.buttons: List[Widget] = []

        theme = get_theme(self)
        self._height = theme.titlebar_height()
        self.set_min_height(self._height)

        button_size = (self._height, self._height)

        if self.override_foreground_color:
            fgcolor = self.override_foreground_color
        fgcolor = theme.titlebar_fgcolor()
        if self.override_foreground_inactive_color:
            fgcolor_inactive = self.override_foreground_inactive_color
        else:
            fgcolor_inactive = theme.titlebar_fgcolor_inactive()

        if menu:
            self.menubutton = TitleBarButton(
                self,
                icon_name="TitleBarMenu",
                size=button_size,
                fgcolor=fgcolor,
                fgcolor_inactive=fgcolor_inactive,
            )
            # FIXME: Menu should be activated by left down, actually...
            self.menubutton.activated.connect(self.__menu_activated)
            self.layout.add(self.menubutton)
            self.buttons.append(self.menubutton)
        else:
            self.menubutton = None

        self.layout.add_spacer(0, expand=True)

        if minimizable:
            self.minimizebutton = TitleBarButton(
                self,
                icon_name="TitleBarMinimize",
                size=button_size,
                fgcolor=fgcolor,
                fgcolor_inactive=fgcolor_inactive,
            )
            self.minimizebutton.activated.connect(self.__minimize_activated)
            self.layout.add(self.minimizebutton)
            self.buttons.append(self.minimizebutton)
        else:
            self.minimizebutton = None

        if maximizable:
            self.maximizebutton = TitleBarButton(
                self,
                icon_name="TitleBarMaximize",
                size=button_size,
                fgcolor=fgcolor,
                fgcolor_inactive=fgcolor_inactive,
            )
            self.maximizebutton.activated.connect(self.__maximize_activated)
            self.layout.add(self.maximizebutton)
            self.buttons.append(self.maximizebutton)
        else:
            self.maximizebutton = None

        self.closebutton = TitleBarButton(
            self,
            icon_name="TitleBarClose",
            size=button_size,
            fgcolor=fgcolor,
            fgcolor_inactive=fgcolor_inactive,
        )
        self.closebutton.activated.connect(self.__close_activated)
        self.layout.add(self.closebutton)
        self.buttons.append(self.closebutton)

        # self._window_active = False
        # parent.activated.connect(self.__on_window_activated)
        # parent.deactivated.connect(self.__on_window_deactivated)

        # FIXME: Would be better to do this via theme instead and get a theme
        # updated notification. Works well enough for now.
        for option in [
            "launcher_titlebar_bgcolor",
            "launcher_titlebar_bgcolor_inactive",
            "launcher_titlebar_fgcolor",
            "launcher_titlebar_fgcolor_inactive",
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

    def on_setting(self, option: str, value: str):
        if option == "launcher_titlebar_bgcolor":
            self.updateBackgroundColor()
        elif option == "launcher_titlebar_bgcolor_inactive":
            # print("- Titlebar << launcher_titlebar_bgcolor_inactive")
            self.updateBackgroundColor()
        elif option == "launcher_titlebar_fgcolor":
            if self.override_foreground_color:
                color = self.override_foreground_color
            else:
                color = get_theme(self).titlebar_fgcolor()
            for button in self.buttons:
                button.set_fgcolor(color)
            self.refresh()
        elif option == "launcher_titlebar_fgcolor_inactive":
            if self.override_foreground_inactive_color:
                color = self.override_foreground_inactive_color
            else:
                color = get_theme(self).titlebar_fgcolor_inactive()
            for button in self.buttons:
                button.set_fgcolor_inactive(color)
            self.refresh()
        elif option == "launcher_titlebar_font":
            self.refresh()
        elif option == "launcher_titlebar_uppercase":
            self.refresh()
        elif option == "launcher_titlebar_height":
            new_height = get_theme(self).titlebar_height()
            self.update_height(new_height)

    @overrides
    def onWindowFocusChanged(self):
        self.updateBackgroundColor()

    def updateBackgroundColor(self):
        theme = get_theme(self)
        if self.isWindowFocused():
            if self.override_background_color:
                color = self.override_background_color
            else:
                color = theme.titlebar_bgcolor()
        else:
            if self.override_background_inactive_color:
                color = self.override_background_inactive_color
            else:
                color = theme.titlebar_bgcolor_inactive()
        self.setBackgroundColor(color)

    def update_height(self, new_height: int):
        if self._height == new_height:
            return
        old_height = self._height
        self._height = new_height
        window = self.getWindow()
        window_x, window_y = window.getPosition()
        window_w, window_h = window.getSize()
        window_y = window_y + old_height - new_height
        window_h = window_h - old_height + new_height
        window.setPositionAndSize((window_x, window_y), (window_w, window_h))
        self.set_min_height(new_height)
        for button in self.buttons:
            button.set_size((new_height, new_height))
        if window.layout is not None:
            window.layout.update()

    def on_paint(self):
        theme = get_theme(self)
        text = self.title
        if theme.titlebar_uppercase():
            text = text.upper()
        _, wh = self.size()
        dc = self.create_dc()
        dc.set_font(theme.titlebar_font())
        # if window(self).window_focus():
        if self.window_focus():
            if self.override_foreground_color:
                color = self.override_foreground_color
            else:
                color = theme.titlebar_fgcolor()
        else:
            if self.override_foreground_inactive_color:
                color = self.override_foreground_inactive_color
            else:
                color = theme.titlebar_fgcolor_inactive()
        dc.set_text_color(color)
        _, th = dc.measure_text(text)
        if self.menubutton:
            # Adding width of button (same as height). Also, adding 6 gives
            # 20 pixels between edge of burger icon and start of text.
            x = self._height + 6
        else:
            x = 20
        y = (wh - th) // 2 + 1
        dc.draw_text(text, x, y)

    # def __on_window_activated(self):
    #     self._window_active = True
    #     self.updateBackgroundColor()

    # def __on_window_deactivated(self):
    #     print("Titlebar.__on_deactivated")
    #     self._window_active = False
    #     self.updateBackgroundColor()

    def __menu_activated(self):
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
        self.popup_menu(menu, (0, self._height))

    def __minimize_activated(self):
        self.getWindow().minimize()

    def __maximize_activated(self):
        window = self.getWindow()
        window.setMaximized(not window.isMaximized())

    def __close_activated(self):
        self.getWindow().close()

    def on_left_dclick(self):
        if self.maximizebutton is not None:
            self.__maximize_activated()

    def on_left_down(self):
        # FIXME: Capture mouse for window tracking
        # FIXME: This should only be a workaround if we cannot get native
        # dragging working
        # Actually, mouse tracking is default on left down it seems
        # FIXME: Update cursor
        # FIXME: Correct cursor? No, we want move cursor
        self.set_move_cursor()
        self.dragging = True
        self.dragging_mouse_origin = fsui.get_mouse_position()
        # self.dragging_window_origin = get_window(self).position()
        self.dragging_window_origin = self.getWindow().getPosition()

    def on_mouse_motion(self):
        mx, my = fsui.get_mouse_position()
        dx = mx - self.dragging_mouse_origin[0]
        dy = my - self.dragging_mouse_origin[1]
        wx = self.dragging_window_origin[0] + dx
        wy = self.dragging_window_origin[1] + dy
        self.getWindow().setPosition((wx, wy))
        # self.getWindow().setRealPosition((wx, wy))

    def on_left_up(self):
        self.set_normal_cursor()
        self.dragging = False
