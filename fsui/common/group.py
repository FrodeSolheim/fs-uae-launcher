import weakref


class Group(object):

    def __init__(self, parent):
        self._parent = weakref.ref(parent)
        if hasattr(parent, "_window"):
            # noinspection PyProtectedMember
            self._window = parent._window
        self.position = (0, 0)
        self.__visible = True

    # def __on_destroy(self):
    #     self.on_destroy()

    @property
    def parent(self):
        return self._parent()

    # def show_or_hide(self, show):
    #     self.__visible = show

    def is_visible(self):
        return self.__visible

    # def on_destroy(self):
    #     pass

    def get_window(self):
        return self.parent.get_window()

    def get_container(self):
        return self.parent.get_container()

    def get_min_width(self):
        return self.layout.get_min_width()

    def get_min_height(self):
        return self.layout.get_min_height()

    def set_position(self, position):
        self.position = position
        if self.layout:
            self.layout.set_position(position)

    def set_size(self, size):
        if self.layout:
            self.layout.set_size(size)

    def set_position_and_size(self, position, size):
        self.position = position
        if self.layout:
            self.layout.set_position_and_size(position, size)
