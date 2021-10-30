from typing import Callable, Optional

import fsui
from fscore.observable import Disposer, isObservable
from fswidgets.parentstack import ParentStack
from launcher.fswidgets2.style import Style, StyleParam


class ClickEvent:
    pass


# FIXME: Move to a types module? or events

ClickEventHandler = Callable[[Optional[ClickEvent]], None]


class Button(fsui.Button):
    def __init__(
        self,
        label: str = "",
        *,
        style: Optional[StyleParam] = None,
        onClick: Optional[ClickEventHandler] = None,
        enabled: bool = True
    ) -> None:
        parent = ParentStack.top()
        print("parent of button is", parent)
        super().__init__(parent, label)

        default_style = Style({})
        if style is not None:
            default_style.update(style)
        self.style = default_style

        fill = True

        # self.set_min_height(30)
        self.set_min_width(80)

        parent.layout.add(self, fill=fill)

        if onClick is not None:
            self.activated.connect(onClick)

        if isObservable(enabled):
            self.addEventListener(
                "destroy", Disposer(enabled.subscribe(self.onEnableNext))
            )
        else:
            self.set_enabled(enabled)

    def onEnableNext(self, value):
        print("onEnableNext", value)
        self.set_enabled(bool(value))

    def get_min_height(self, width):
        # FIXME: Default height if nothing else is specified. Implement via
        # default style?
        return 30
