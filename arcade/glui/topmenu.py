import os
import time

from arcade.gamecentersettings import GameCenterSettings
from arcade.glui.constants import TOP_ITEM_LEFT
from arcade.glui.constants import TOP_ITEM_NOBORDER
from arcade.glui.font import BitmapFont
from arcade.glui.items import MenuItem, create_item_menu
from arcade.glui.navigatable import Navigatable
from arcade.glui.opengl import gl, fs_emu_blending
from arcade.glui.sdl import *
from arcade.glui.state import State
from arcade.glui.texture import Texture
from arcade.resources import gettext
from fsbc.application import app
from fsbc.settings import Settings


def post_quit_event():
    State.get().quit = True


class TopMenuItem(MenuItem):
    def __init__(self):
        super().__init__()
        self.normal_texture = None
        self.selected_texture = None

    def update_size_right(self):
        self.w = 80

    def render_top_right(self, selected=False):
        state = State.get()
        mouse_state = state.mouse_item == self
        mouse_pressed_state = mouse_state and state.mouse_press_item == self
        self.render_top_background(
            selected, style=TOP_ITEM_LEFT, mouse_state=mouse_state,
            mouse_pressed_state=mouse_pressed_state)
        fs_emu_blending(True)
        if selected:
            texture = self.selected_texture
        else:
            texture = self.normal_texture
        # texture.render(self.x, self.y, self.w, self.h)
        texture.render(
            self.x + (self.w - texture.w) / 2,
            self.y + (self.h - texture.h) / 2, texture.w, texture.h)


class CloseItem(TopMenuItem):
    def __init__(self):
        super().__init__()
        self.normal_texture = Texture.close
        self.selected_texture = Texture.close_selected

    def activate(self, menu):
        post_quit_event()


class ShutdownItem(TopMenuItem):
    def __init__(self):
        super().__init__()
        self.normal_texture = Texture.shutdown
        self.selected_texture = Texture.shutdown_selected

    def activate(self, menu):
        command = GameCenterSettings.get_shutdown_command()
        if command:
            os.system(command)
        post_quit_event()


class MaximizeItem(TopMenuItem):
    def __init__(self):
        super().__init__()
        self.title = "Ma"


class MinimizeItem(TopMenuItem):
    def __init__(self):
        super().__init__()
        self.normal_texture = Texture.minimize
        self.selected_texture = Texture.minimize_selected

    def activate(self, menu):
        SDL_Minimize()
        # want item menu focused when window is restored
        # FIXME: temporarily disabled
        # set_current_menu(State.get().current_menu)


class ClockItem(MenuItem):
    def __init__(self):
        super().__init__()
        self.title = "00:00"
        self.enabled = False

    def update_size(self, text):
        self.w = 148

    def render_top_right(self, selected=False):
        self.render_top_background(selected, style=TOP_ITEM_NOBORDER)
        self.render_top(self.get_top_right_text(), selected, right_align=True)

    def get_top_right_text(self):
        return time.strftime("%H:%M")

    def activate(self, menu):
        pass


class AspectItem(TopMenuItem):
    def __init__(self):
        super().__init__()
        self.normal_texture = Texture.stretch
        self.selected_texture = Texture.stretch
        self.update_texture()

    def update_texture(self):
        # TODO: Ideally, this class should listen for settings changes.
        if Settings.instance()["keep_aspect"] == "0":
            texture = Texture.stretch
        else:
            texture = Texture.aspect
        self.normal_texture = texture
        self.selected_texture = texture

    def activate(self, menu):
        if Settings.instance()["keep_aspect"] == "0":
            Settings.instance()["keep_aspect"] = ""
        else:
            Settings.instance()["keep_aspect"] = "0"
        self.update_texture()


class VideoSyncItem(MenuItem):
    def __init__(self):
        super().__init__()
        self.title = "V-SYNC"

    def activate(self, menu):
        if Settings.instance()["video_sync"] == "1":
            Settings.instance()["video_sync"] = ""
        else:
            Settings.instance()["video_sync"] = "1"

    def render_top_right(self, selected=False):
        self.render_top_background(selected, style=TOP_ITEM_LEFT)
        gl.glDisable(gl.GL_DEPTH_TEST)
        fs_emu_blending(True)
        if Settings.instance()["video_sync"] == "1":
            r = 1.0
            g = 1.0
            b = 1.0
            alpha = 1.0
        else:
            r = 1.0
            g = 1.0
            b = 1.0
            alpha = 0.33
        x = self.x + 20
        BitmapFont.title_font.render(self.title, x, self.y + 14,
                                     r=r, g=g, b=b, alpha=alpha)
        gl.glEnable(gl.GL_DEPTH_TEST)


class TopMenu(Navigatable):
    def __init__(self):
        super().__init__()
        self.left = []
        self.right = []
        self.right.append(VideoSyncItem())
        self.right.append(AspectItem())
        if self.use_clock_item():
            self.right.append(ClockItem())
        # if Render.get().allow_minimize:
        #     if Config.get_bool("menu/minimize", True):
        #         self.right.append(MinimizeItem())
        command = GameCenterSettings.get_shutdown_command()
        if command:
            self.right.append(ShutdownItem())
        else:
            self.right.append(CloseItem())
        self._selected_index = 0

    @staticmethod
    def use_clock_item():
        return app.settings["game-center:top-clock"] != "0"

    def append_left(self, item):
        self.left.append(item)

    def append_right(self, item):
        self.right.insert(0, item)

    @property
    def selected_item(self):
        index = self._selected_index
        return self[index]

    def get_selected_index(self):
        return self._selected_index

    def set_selected_index(self, index, immediate=False):
        assert immediate is not None
        self._selected_index = index

    def go_left(self, count=1):
        index = self._selected_index - 1
        while index >= 0:
            if self[index].enabled:
                self._selected_index = index
                break
            index -= 1

    def go_right(self, count=1):
        index = min(len(self) - 1, self._selected_index + count)
        self._selected_index = index
        if not self[index].enabled:
            self.go_right()

    def go_up(self):
        # do nothing
        pass

    def activate(self):
        result = self.selected_item.activate(State.get().current_menu)
        # FIXME:
        from arcade.glui.menu import Menu
        if isinstance(result, Menu):
            # FIXME:
            from arcade.glui.window import enter_menu
            enter_menu(result)

    def __getitem__(self, index):
        if index < len(self.left):
            return self.left[index]
        return self.right[index - len(self.left)]

    def __len__(self):
        return len(self.left) + len(self.right)


class OldGameCenterItem(MenuItem):
    def __init__(self):
        super().__init__()
        # if app.name == "fs-uae-arcade":
        self.title = gettext("FS-UAE   Arcade")
        # else:
        #     self.title = gettext("Game   Center")
        self.path_title = self.title
        self.enabled = False

    def activate(self, menu):
        pass

    # def update_size(self, text):
    #     MenuItem.update_size(text)
    #     #self.w = Texture.top_logo.w + 83

    def render_top_left(self, selected=False):
        # self.render_top_background(selected, style=TOP_ITEM_ARROW)
        MenuItem.render_top_left(self, selected=selected)
        gl.glDisable(gl.GL_DEPTH_TEST)
        fs_emu_blending(True)
        # if app.name == "fs-uae-arcade":
        x = 161
        # else:
        #     x = 138
        y = 14
        # if selected:
        # texture = Texture.top_logo_selected
        # else:
        texture = Texture.top_logo
        texture.render(x, 1080 - y - texture.h, texture.w, texture.h)
        # fs_emu_blending(False)
        gl.glEnable(gl.GL_DEPTH_TEST)


class GameCenterItem(MenuItem):
    def __init__(self):
        super().__init__()
        self.title = gettext("FS-UAE Arcade")
        self.path_title = self.title
        self.enabled = False

    def activate(self, menu):
        pass

    def update_size(self, text):
        tw, _ = BitmapFont.title_font.measure("FS-UAE")
        tw2, _ = BitmapFont.title_font.measure("Arcade")
        self.w = 20 + 32 + 20 + tw + 20 + tw2 + 20

    def render_top_left(self, selected=False):
        gl.glDisable(gl.GL_DEPTH_TEST)
        fs_emu_blending(True)
        x = 20
        y = 14
        texture = Texture.logo_32
        texture.render(x, 1080 - y - texture.h, texture.w, texture.h)
        x += 32 + 20
        BitmapFont.title_font.render("FS-UAE", x, self.y + 14)
        tw, _ = BitmapFont.title_font.measure("FS-UAE")
        x += tw + 20
        BitmapFont.title_font.render("Arcade", x, self.y + 14, alpha=0.5)
        gl.glEnable(gl.GL_DEPTH_TEST)


class HomeItem(MenuItem):
    def __init__(self):
        super().__init__()
        self.title = gettext("Home")
        self.path_title = self.title

    def activate(self, menu):
        from arcade.glui.window import create_main_menu
        new_menu = create_main_menu()
        # State.get().history = [new_menu]
        State.get().history.append(new_menu)
        from arcade.glui.window import set_current_menu
        set_current_menu(new_menu)

    def update_size_left(self):
        self.w = 80

    def render_top_left(self, selected=False):
        self.render_top_background(selected)
        # fs_emu_blending(True)
        if selected:
            texture = Texture.home_selected
        else:
            texture = Texture.home
        texture.render(self.x, self.y, texture.w, texture.h)


class AddItem(MenuItem):
    def __init__(self):
        super().__init__()
        self.title = gettext("Add")
        self.path_title = self.title

    def update_size_left(self):
        self.w = 80

    def render_top_left(self, selected=False):
        self.render_top_background(selected)
        # fs_emu_blending(True)
        if selected:
            texture = Texture.add_selected
        else:
            texture = Texture.add
        texture.render(self.x, self.y, texture.w, texture.h)

    def activate(self, menu):
        new_menu = create_item_menu(self.title)
        menu_path = self.create_menu_path(menu)
        new_menu.update_path(menu_path)
        for item in self.generate_category_items(menu_path):
            new_menu.append(item)
        return new_menu
