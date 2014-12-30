from weakref import WeakValueDictionary
from fs_uae_workspace.vfs import get_vfs_item


window_uris = WeakValueDictionary()
# window_uris = {}
opened_count = 0


def set_initial_window_position(window):
    global opened_count
    x = 100 + (opened_count % 10) * 40
    y = x
    window.set_position((x, y))
    opened_count += 1


def raise_window(uri):
    print("raise_window", uri)
    try:
        window = window_uris[uri]
    except KeyError:
        return False
    # window.raise_()
    # # window.setFocus()
    # window.activateWindow()
    window.raise_and_activate()
    return True


def register_window(uri, window):
    print("register_window", uri, window)

    # def on_window_closed():
    #     print("on_window_closed")
    #     del window_uris[uri]
    # window.closed.connect(on_window_closed)

    window_uris[uri] = window


def shell_open(uri, args=None, parent=None, center=None):
    if args is None:
        args = []
    item = get_vfs_item(uri)
    import fsui
    if parent:
        fsui.default_window_parent.append(parent)
    if center:
        fsui.default_window_center.append(center)
    try:
        item.open(args)
    finally:
        if parent:
            fsui.default_window_parent.pop()
        if center:
            fsui.default_window_center.pop()


# noinspection PyPep8Naming
def SimpleApplication(window_class):

    def application(uri, args):
        fake_uri = uri + repr(args)
        if not raise_window(fake_uri):
            window = window_class()
            window.show()
            register_window(fake_uri, window)

    return application


# noinspection PyUnresolvedReferences
from .window import Window, QWindow
