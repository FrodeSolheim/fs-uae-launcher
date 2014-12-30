from game_center.glui.state import State


class Navigatable(object):
    
    def go_left(self, count=1):
        pass

    def go_right(self, count=1):
        pass

    def go_up(self):
        State.down_navigatable = self
        State.navigatable = State.top_menu

    def go_down(self):
        if State.down_navigatable:
            State.navigatable = State.down_navigatable
            State.down_navigatable = None

    def activate(self):
        pass
