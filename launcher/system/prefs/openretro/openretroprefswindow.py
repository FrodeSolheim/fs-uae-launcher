from launcher.experimental.flexbox.flexlayout import FlexLayout
import fsui
from launcher.experimental.flexbox.parentstack import ParentStack
from launcher.experimental.flexbox.flexcontainer import FlexContainer, Style, VerticalFlexContainer
from launcher.experimental.flexbox.button import Button
from launcher.i18n import gettext
from launcher.system.prefs.common.baseprefswindow import BasePrefsWindow
from launcher.system.prefs.openretro.openretroprefspanel import (
    OpenRetroPrefsPanel,
)
from launcher.system.classes.windowresizehandle import WindowResizeHandle


from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def constructor(function: F) -> F:
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        ParentStack.push(self)
        try:
            return function(*args, **kwargs)
        finally:
            assert ParentStack.pop() == self

    return cast(F, wrapper)



class OpenRetroPrefsWindow(BasePrefsWindow):

    # @constructor
    def __init__(self, parent=None):
        # ParentStack.push(self)

        super().__init__(title=gettext("OpenRetro preferences"), style={"display": "flex"})

        # assert ParentStack.pop() == self

        WindowResizeHandle(self)

    def __del__(self):
        print("OpenRetroPrefsWindow.__del__")
