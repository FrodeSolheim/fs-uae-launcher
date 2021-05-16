import logging
from typing import Any, Dict, Optional, Type, TypeVar

from fsui import Window

# from autologging import traced


log = logging.getLogger(__name__)


T = TypeVar("T", bound="Window")

# @traced
class WindowCache:
    cache = {}  # type: Dict[str, Window]

    @classmethod
    def open(
        cls,
        window_class: Type[T],
        cache_key: Optional[str] = None,
        center_on_window: Optional[Window] = None,
        centerOnWindow: Optional[Window] = None,
        **kwargs: Dict[str, Any]
    ) -> T:
        cache_key_str = cache_key or repr(window_class)
        try:
            window = cls.cache[cache_key_str]
        except LookupError:
            pass
        else:
            window.raise_and_activate()
            return window
        window = window_class()
        cls.cache[cache_key_str] = window

        # @traced
        def remove_window():
            log.debug("Remove window %s", window)
            del cls.cache[cache_key_str]

        window.closed.connect(remove_window)
        window.show()

        if center_on_window is not None:
            log.debug("Center on window %s", center_on_window)
            window.center_on_window(center_on_window)

        if centerOnWindow is not None:
            window.center_on_window(centerOnWindow)

        if kwargs.get("window") is not None:
            window.center_on_window(kwargs.get("window"))

        return window
