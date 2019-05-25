import weakref

from arcade.glui.animation import AnimationSystem
from arcade.glui.input import InputHandler
from arcade.glui.state import State
from arcade.glui.texturemanager import TextureManager


class Callbacks:
    def __init__(self):
        self.width = 320
        self.height = 200
        self.window = None
        self.idle_counter = 0

    def initialize(self, width, height):
        self.width = width
        self.height = height

        # Re-create state object
        State.reset()

        TextureManager.reset()

        import arcade.glui.window

        arcade.glui.window.main_window = self
        arcade.glui.window.show()

    def active(self):
        """Check whether the user interface is active or not. If not active,
        we do not want to force regular/timed refresh event."""
        state = State.get()
        # print("state.game_running", state.game_running)
        if state.game_running:
            # print("inactive")
            return False
        # print(state.idle_from)
        # if state.idle_from and state.idle_from < get_current_time():
        # print(InputHandler.peek_button())
        if not InputHandler.peek_button():
            if not state.dirty:
                if not AnimationSystem.is_active():
                    self.idle_counter += 1
                    if self.idle_counter < 16:
                        # We render 1 frame per second when "idling". We need
                        # to "render" regularly, because some state is updated
                        # during the render phase.
                        return False
        self.idle_counter = 0
        return True

    def resize(self, width, height):
        print("Callbacks.resize", width, height)
        from arcade.glui.window import on_resize

        self.width = width
        self.height = height
        on_resize((width, height))

    def render(self):
        # print("render")
        from arcade.glui.window import main_loop_iteration

        if main_loop_iteration():
            print("main_loop_iteration signalled quit")
            TextureManager.get().unload_textures()
            self.window().quit()

    def timer(self):
        InputHandler.update()

    def restore_window_if_necessary(self):
        pass
        # noinspection PyCallingNonCallable
        # window = self.window()
        # under Gnome 3, the window is minized when launching FS-UAE
        # full-screen from full-screen arcade/game center.
        # window.restore_window_if_necessary()

    def set_window(self, window):
        self.window = weakref.ref(window)
