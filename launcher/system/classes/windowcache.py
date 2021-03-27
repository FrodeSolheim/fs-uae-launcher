import logging
from typing import Dict, Optional, Type

from autologging import traced

from fsui import Window

log = logging.getLogger(__name__)


@traced
class WindowCache:
    cache = {}  # type: Dict[str, Window]

    @classmethod
    def open(
        cls,
        window_class: Type[Window],
        cache_key: Optional[str] = None,
        center_on_window: Optional[Window] = None,
        centerOnWindow: Optional[Window] = None,
    ):
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

        @traced
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

        return window
