from fsui.qt import QWidget


# noinspection PyPep8Naming
def QParent(parent, window=False):
    if parent is None:
        return None
    if window:
        if hasattr(parent, "real_window"):
            return parent.real_window()
    else:
        if hasattr(parent, "real_widget"):
            return parent.real_widget()
    if hasattr(parent, "get_container"):
        return parent.get_container()
    if isinstance(parent, QWidget):
        return parent
    raise Exception("Could not find QParent")
