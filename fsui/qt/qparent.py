from typing import Any, Optional

from fswidgets.qt.widgets import QWidget

# FIXME: Using Any right now to avoid import cycles


def QParent(
    parent: Any, window: "Optional[Any]" = False, forceRealParent: bool = False
) -> Optional[QWidget]:
    # print(f"\n\n\nQParent parent={parent}")
    if parent is None:
        # print("none")
        return None
    # FIXME: Better way
    from fsui.common.group import Group

    if not forceRealParent:
        # if hasattr(parent, "qcontainer") and parent.qcontainer is not None:
        #     return parent.qcontainer

        if hasattr(parent, "container") and parent.container is not None:
            return parent.container.qwidget

    while isinstance(parent, Group):
        parent = parent.parent()
    # FIXME end
    if window:
        if hasattr(parent, "real_window"):
            # print("real_window")
            return parent.real_window()
    else:
        if hasattr(parent, "real_widget"):
            # print("real_widget")
            return parent.real_widget()
    if hasattr(parent, "get_container"):
        # print("get_container")
        return parent.get_container()
    if isinstance(parent, QWidget):
        return parent
    # if hasattr(parent, "_qwidget"):
    #     return parent._qwidget
    raise Exception("Could not find QParent")


# from fswidgets.widget import Widget
