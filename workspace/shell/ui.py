import weakref

import workspace.path
import workspace.shell
import workspace.ui

ICON_WIDTH = 120
ICON_HEIGHT = 100


class ScrollArea(workspace.ui.Panel):
    """A widget containing the icons in a directory."""

    def __init__(self, parent):
        super().__init__(parent)
        self.selection = None
        self._sort_key_function = None

    def set_sort_key_function(self, function):
        self._sort_key_function = function

    def populate_with_icons(self, path):
        # self.icons.clear()
        items = workspace.path.listdir(path)
        print("populate_with_icons", items)
        x = 0
        y = 0
        width = self.size()[0]
        print("populate_with_icons width =", width)
        for item in sorted(items, key=self._sort_key_function):
            if item.startswith("."):
                continue
            if item.endswith(".fs-info"):
                continue
            if item.endswith(".uaem"):
                continue
            if item.endswith("~"):
                continue
            if item == "Makefile":
                continue
            icon = ShellIcon(self, workspace.path.join(path, item), item)
            icon_width = ICON_WIDTH
            if len(item) >= 45:
                icon_width *= 4
                icon.set_size((icon_width, ICON_HEIGHT))
            elif len(item) >= 30:
                icon_width *= 3
                icon.set_size((icon_width, ICON_HEIGHT))
            elif len(item) > 15:
                icon_width *= 2
                icon.set_size((icon_width, ICON_HEIGHT))
            if x + icon_width > width:
                x = 0
                y += ICON_HEIGHT
            print(item, x, y, "area width", width)
            icon.set_position((x, y))
            x += icon_width


class ShellIcon(workspace.ui.Canvas):
    """A widget representing a file or a directory."""

    STATE_NORMAL = 0
    STATE_SELECTED = 1

    def __init__(self, parent, path, name):
        super().__init__(parent)
        # self.dir_path = dir_path
        self._path = path
        self.name = name
        # self.set_min_size((ICON_WIDTH, ICON_HEIGHT))
        self.set_size((ICON_WIDTH, ICON_HEIGHT))
        # self.set_background_color(workspace.ui.Color(0xff, 0x00, 0xff))
        self._icon = [None, None]
        self._state = self.STATE_NORMAL

    def select(self):
        if self.parent().selection:
            self.parent().selection().set_state(self.STATE_NORMAL)
        self.set_state(self.STATE_SELECTED)
        self.parent().selection = weakref.ref(self)

    def set_state(self, state):
        self._state = state
        self.refresh()

    def path(self):
        return self._path

    #     path = self.dir_path
    #     if not path.endswith(":"):
    #         path += "/"
    #     path += self.name
    #     return path

    def icon(self, state=STATE_NORMAL) -> workspace.ui.Image:
        if self._icon[state] is None:
            is_dir = workspace.path.isdir(self.path())
            image = workspace.shell.icon(self.path(), state=state)
            if image is None and not is_dir:
                image = workspace.shell.default_icon(self.path(), state=state)
            if image is None:
                icon_name = "file"
                if is_dir:
                    icon_name = "folder"
                # if state == self.STATE_NORMAL:
                #     path = "SYS:Icons/FileTypes/{}.fs-info/icon.png".format(
                #             icon_name)
                # else:
                #     path = "SYS:Icons/FileTypes/{}.fs-info/" \
                #             "selected.png".format(icon_name)
                image = workspace.shell.file_type_icon(icon_name, state)
                # image = workspace.ui.Image(path)
            self._icon[state] = image
        return self._icon[state]

    def on_left_down(self):
        self.select()

    def on_left_dclick(self):
        path = self.path()
        name = workspace.path.basename(path)
        app_path = workspace.path.join(path, name + ".py")
        # FIXME: Use ShellOpen for directories too
        if workspace.shell.tool(path) is not None:
            # Icon has associated tool, use ShellOpen even if it is a
            # directory.
            workspace.shell.open(path)
        elif workspace.path.exists(app_path):
            workspace.shell.open(path)
        elif workspace.path.isdir(path):
            # FIXME: Ugly hack (app is set by FileManager.py)
            app.open(path)
        else:
            workspace.shell.open(path)

    def on_paint(self):
        painter = workspace.ui.Painter(self)
        w, h = painter.measure_text(self.name)
        painter.set_text_color(workspace.ui.Color(0x00, 0x00, 0x00, 0x80))
        painter.draw_text(self.name, (self.width() - w) // 2 + 1, 80 + 1)
        painter.set_text_color(workspace.ui.Color(0xFF, 0xFF, 0xFF))
        painter.draw_text(self.name, (self.width() - w) // 2, 80)
        icon = self.icon(self._state)
        # print(icon, icon)
        painter.draw_image(icon, (self.width() - icon.width()) // 2, 10)
