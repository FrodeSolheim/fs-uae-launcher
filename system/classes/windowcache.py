import logging
from typing import Any, Dict, Optional, Type, TypeVar, cast

from fsui import Window
from fsui.qt.toplevelwidget import TopLevelWidget
from system.classes.shellobject import ShellOpenArgs

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
        # args: Optional[ShellOpenArgs] = None,
        params: Optional[Dict[str, Any]] = None,  # FIXME: Any...
        *,
        cacheKey: Optional[Any] = None,
        centerOnWindow: Optional[TopLevelWidget] = None,
        cache_key: Optional[str] = None,
        center_on_window: Optional[TopLevelWidget] = None,
        window: Optional[Window] = None,
        **kwargs: Dict[str, Any],
    ) -> T:
        # if args is not None:
        #     if args.openedFrom is not None:
        #         centeronWindow

        cache_key_str = cacheKey or cache_key or repr(window_class)
        try:
            _window = cast(T, cls.cache[cache_key_str])
        except LookupError:
            pass
        else:
            _window.raise_and_activate()
            return _window
        if params is not None:
            _window = window_class(**params)
        else:
            _window = window_class()
        cls.cache[cache_key_str] = _window

        # @traced
        def remove_window():
            log.debug("Remove window %s", _window)
            del cls.cache[cache_key_str]

        _window.closed.connect(remove_window)
        _window.show()

        if center_on_window is not None:
            log.debug("Center on window %s", center_on_window)
            _window.center_on_window(center_on_window)

        if centerOnWindow is not None:
            _window.center_on_window(centerOnWindow)

        # if kwargs.get("window") is not None:
        if window is not None:
            # window.center_on_window(kwargs.get("window"))
            _window.center_on_window(window)

        # if args is not None:
        #     if args.openedFrom is not None:
        #         _window.center_on_window(args.openedFrom)

        return _window


class ShellWindowCache:
    cache = {}  # type: Dict[str, Window]

    @classmethod
    def open(
        cls,
        args: ShellOpenArgs,
        windowClass: Type[T],
        # *args
        params: Optional[Dict[str, Any]] = None,  # FIXME: Any...
        *,
        cacheKey: Optional[Any] = None,
    ) -> T:

        cacheKeyStr = repr(cacheKey or windowClass)
        try:
            window = cast(T, cls.cache[cacheKeyStr])
        except LookupError:
            pass
        else:
            window.raise_and_activate()
            return window
        if params is not None:
            window = windowClass(**params)
        else:
            window = windowClass()
        cls.cache[cacheKeyStr] = window

        # @traced
        def remove_window():
            log.debug("Remove window %s", window)
            del cls.cache[cacheKeyStr]

        window.closed.connect(remove_window)
        window.show()

        if args.openedFrom is not None:
            window.center_on_window(args.openedFrom)

        return window
