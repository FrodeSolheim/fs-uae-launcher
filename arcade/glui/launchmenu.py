from arcade.glui.dialog import Dialog
from arcade.glui.gamecenterrunner import GameCenterRunner
from arcade.glui.input import InputHandler
from arcade.glui.menu import Menu
from arcade.glui.opengl import gl, fs_emu_texturing, fs_emu_blending
from arcade.glui.render import Render
from arcade.glui.state import State
from arcade.glui.texture import Texture
from arcade.glui.topmenu import GameCenterItem
from arcade.glui.window import set_current_menu, render_fade
from arcade.glui.window import set_ingame_status, back_to_menu_from_game

STATE_STARTING = 0
STATE_PREPARING = 1
STATE_WAITRUN = 2
STATE_RUNNING = 3
STATE_STOPPING = 4
STATE_ABORTING = 5
STATE_ABORTED = 6

FADE_TIME = 0.5


class LaunchMenu(Menu):
    def __init__(self, item, controller):
        Menu.__init__(self)
        # self.top_menu_transition = 0.0
        self.items.append(item)
        if self.use_game_center_item():
            self.top.left.append(GameCenterItem())
        # self.top.left.append(HomeItem())
        # self.top.left.append(MenuItem(item.title))
        self.top.set_selected_index(
            len(self.top.left) + len(self.top.right) - 1
        )
        self.state = STATE_STARTING
        self.gc_runner = None
        self.controller = controller
        self.throbber = Throbber()
        self.wait_run_time = 0

    # noinspection PyMethodMayBeStatic
    def on_status(self, status):
        print("received status", status)

    def update_state(self):
        if self.state == STATE_STARTING:
            self.gc_runner = GameCenterRunner(controller=self.controller)
            # prepare will unpack the game and prepare game files
            self.gc_runner.prepare()
            self.state = STATE_PREPARING
            self.throbber.throbber_start_time = 0

        elif self.state == STATE_PREPARING:
            if self.gc_runner.error:
                pass
            elif self.gc_runner.done:
                self.wait_run_time = State.get().time
                FadeDialog(self.wait_run_time).show()
                self.state = STATE_WAITRUN

        elif self.state == STATE_WAITRUN:
            if State.get().time - self.wait_run_time > FADE_TIME:
                set_ingame_status()
                self.gc_runner.run()
                self.state = STATE_RUNNING

        elif self.state == STATE_RUNNING:
            InputHandler.set_inhibited(True)
            if self.gc_runner.error:
                pass
            elif self.gc_runner.done:
                self.state = STATE_STOPPING

        elif self.state == STATE_STOPPING:
            InputHandler.set_inhibited(False)
            State.get().history.pop()
            State.get().history.pop()
            State.get().history.pop()
            set_current_menu(State.get().history[-1])
            back_to_menu_from_game()
            Dialog.get_current().close()

            from arcade.glui.window import main_window

            main_window.restore_window_if_necessary()

        elif self.state == STATE_ABORTING:
            pass

    def go_back(self):
        print("LaunchMenu.go_back")
        if self.state in [STATE_STARTING, STATE_PREPARING]:
            if self.gc_runner:
                self.gc_runner.abort()
                self.state = STATE_ABORTING
        if self.state in [STATE_ABORTED]:
            State.get().history.pop()
            set_current_menu(State.get().history[-1])

    def activate(self):
        print("LaunchMenu.activate")

    def update(self):
        self.update_state()

    def render(self):
        Render.get().hd_perspective()
        fs_emu_texturing(True)
        fs_emu_blending(False)
        Texture.sidebar_background.render(
            0, 0, 1920, Texture.sidebar_background.h
        )

        if self.state in [STATE_PREPARING, STATE_WAITRUN]:
            self.throbber.render()
            # elif self.state in [STATE_RUNNING, STATE_STOPPING]:
            #     pass
            # gl.glDisable(gl.GL_DEPTH_TEST)
            # render_fade(0.0, 0.0, 0.0, 1.0)
            # gl.glEnable(gl.GL_DEPTH_TEST)


class FadeDialog(Dialog):
    def __init__(self, wait_run_time):
        super().__init__()
        self.wait_run_time = wait_run_time

    def render(self):
        gl.glDisable(gl.GL_DEPTH_TEST)
        alpha = (State.get().time - self.wait_run_time) / FADE_TIME
        render_fade(0.0, 0.0, 0.0, alpha)
        gl.glEnable(gl.GL_DEPTH_TEST)


class Throbber:
    def __init__(self):
        self.throbber_colors = [1.0, 0.8, 0.6, 0.2, 0.2, 0.2, 0.2, 0.2]
        self.throbber_start_time = 0
        self.throbber_progress = 0
        self.throbber_opacity = 1.0
        # self.start_time = 0

    def render(self):
        Render.get().hd_perspective()
        if self.throbber_start_time == 0:
            self.throbber_start_time = State.get().time
        dt = State.get().time - self.throbber_start_time
        # run animation with 15 fps
        self.throbber_progress = int(dt * 15)

        # bg_fade = (State.get().time - State.get().dialog_time) / 0.5
        # if bg_fade > 1.0:
        #     bg_fade = 1.0
        # elif bg_fade < 0.0:
        #     bg_fade = 0.0
        fs_emu_texturing(False)
        fs_emu_blending(True)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDepthMask(False)

        # gl.glBegin(gl.GL_QUADS)
        # gl.glColor4f(0.0, 0.0, 0.0, bg_fade)
        # gl.glVertex2f(0, 0)
        # gl.glVertex2f(1920, 0)
        # gl.glVertex2f(1920, 1020)
        # gl.glVertex2f(0, 1020)
        # gl.glEnd()

        # gl.glBegin(gl.GL_QUADS)
        # gl.glColor4f(0.0, 0.0, 0.0, bg_fade * 0.5)
        # gl.glVertex2f(0, 1020)
        # gl.glVertex2f(1920, 1020)
        # gl.glVertex2f(1920, 1080)
        # gl.glVertex2f(0, 1080)
        # gl.glEnd()

        # y = 0.0
        # tw, th = Render.get().text("LAUNCHING GAME", self.title_font,
        #         0.0, y, w=32 / 9, h=self.height,
        #         color=(1.0, 1.0, 1.0, 1.0), halign=0.0)
        #
        fs_emu_blending(True)
        # if bg_fade > 0.5:
        #     self.throbber_opacity = (bg_fade - 0.5) / 0.5
        #     #self.throbber_opacity = bg_fade
        #     self.render_throbber()
        # if bg_fade == 1.0:
        # if State.get().time - State.get().dialog_time > 1.0:
        #     # gradually show over 1/4 second
        #     self.throbber_opacity = (
        #         (State.get().time - State.get().dialog_time - 1.0) * 4)
        #     if self.throbber_opacity > 1.0:
        #         self.throbber_opacity = 1.0
        #     self.render_throbber()
        if State.get().time - self.throbber_start_time > 0.25:
            # gradually show over 1/3 second
            self.throbber_opacity = (
                State.get().time - self.throbber_start_time - 0.25
            ) * 4
            if self.throbber_opacity > 1.0:
                self.throbber_opacity = 1.0
            self.render_throbber()

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthMask(True)
        # fs_emu_texturing(1)
        # fs_emu_blending(0)
        # print("Setting dirty..")
        Render.get().dirty = True

    def render_throbber(self):
        cell_width = 32
        cell_spacing = 16
        throbber_width = 3 * cell_width + 2 * cell_spacing
        # throbber_height = throbber_width
        left = (1920 - throbber_width) / 2
        bottom = (1080 - throbber_width) / 2

        self.render_cell(0, left, bottom)
        self.render_cell(1, left + 1 * cell_width + 1 * cell_spacing, bottom)
        self.render_cell(2, left + 2 * cell_width + 2 * cell_spacing, bottom)
        self.render_cell(
            3,
            left + 2 * cell_width + 2 * cell_spacing,
            bottom + 1 * cell_width + 1 * cell_spacing,
        )
        self.render_cell(
            4,
            left + 2 * cell_width + 2 * cell_spacing,
            bottom + 2 * cell_width + 2 * cell_spacing,
        )
        self.render_cell(
            5,
            left + 1 * cell_width + 1 * cell_spacing,
            bottom + 2 * cell_width + 2 * cell_spacing,
        )
        self.render_cell(6, left, bottom + 2 * cell_width + 2 * cell_spacing)
        self.render_cell(7, left, bottom + 1 * cell_width + 1 * cell_spacing)

    def render_cell(self, index, x, y):
        color = self.throbber_colors[(self.throbber_progress + index) % 8]
        color *= self.throbber_opacity
        gl.glColor4f(color, color, color, self.throbber_opacity)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(x, y)
        gl.glVertex2f(x + 32, y)
        gl.glVertex2f(x + 32, y + 32)
        gl.glVertex2f(x, y + 32)
        gl.glEnd()
