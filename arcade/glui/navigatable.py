from arcade.glui.state import State


class Navigatable(object):
    def go_left(self, count=1):
        pass

    def go_right(self, count=1):
        pass

    def go_up(self):
        State.get().down_navigatable = self
        State.get().navigatable = State.get().top_menu

    def go_down(self):
        if State.get().down_navigatable:
            State.get().navigatable = State.get().down_navigatable
            State.get().down_navigatable = None

    def activate(self):
        pass
