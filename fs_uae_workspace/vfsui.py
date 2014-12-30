from fsui import Window, VerticalLayout
from .iconview import IconView
from .vfs import get_vfs_item


class VFSIconView(IconView):

    def __init__(self, parent, item):
        IconView.__init__(self, parent)
        self.item = item
        self.children = sorted(self.item.children())

    def get_item_count(self):
        return len(self.children)

    def get_item_text(self, index):
        return self.children[index]

    def get_item_icon(self, index):
        name = self.children[index]
        item = self.item.item(name)
        icon = item.icon()
        # return fsui.Image("")
        return icon.image()

    def on_activate_item(self, index):
        name = self.children[index]
        item = self.item.item(name)
        # window = VFSWindow(item)
        # window.show()
        VFSWindow.open_item(item)


class VFSWindow(Window):

    opened_count = 0

    @classmethod
    def open_item(cls, item):
        content_type = item.content_type()
        if content_type == "application/x-fs-uae-application":
            item.open()
        elif content_type == "application/x-fs-uae-vfolder":
            uri = item.uri()
            # try:
            #     window = window_uris[uri]
            # except KeyError:
            #     window = VFSWindow(item)
            #     window.show()
            # else:
            #     assert isinstance(window, Window)
            #     window.raise_()
            #    return
            from .shell import raise_window, register_window
            if not raise_window(uri):
                window = VFSWindow(item)
                window.show()
                register_window(uri, window)

    @classmethod
    def open_uri(cls, uri):
        item = get_vfs_item(uri)
        cls.open_item(item)

    def __init__(self, item):
        Window.__init__(self)
        self.setWindowTitle(item.name())
        self.layout = VerticalLayout()
        self.icon_view = VFSIconView(self, item)
        self.icon_view.setStyleSheet("background-color: #ededed")
        self.layout.add(self.icon_view, expand=True, fill=True)
        w, h = 600, 400
        self.set_size((w, h))
