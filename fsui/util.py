from typing import Any, Optional, Type, TypeVar, cast

from fsui.qt.toplevelwidget import TopLevelWidget

# from fsui.qt.window import Window

T = TypeVar("T", bound=TopLevelWidget)


def open_window_instance(
    cls: Type[T], parent: Optional[TopLevelWidget] = None
) -> T:
    if not hasattr(cls, "_window_instance"):
        cls._window_instance = None  # type: ignore
    if cls._window_instance is not None:  # type: ignore
        instance = cls._window_instance  # type: ignore
        assert isinstance(instance, TopLevelWidget)
        instance.raise_and_activate()
        return instance  # type: ignore
    instance = cls(parent)  # type: ignore
    cls._window_instance = instance  # type: ignore

    def reset_instance() -> None:
        print("SettingsDialog.reset_instance")
        # cls._window_instance.deleteLater()
        cls._window_instance = None  # type: ignore

    instance.closed.connect(reset_instance)
    instance.show()
    assert isinstance(instance, TopLevelWidget)
    return cast(T, instance)

    # def monitor_instance_2(count):
    #     if count < 100:
    #         call_after(monitor_instance_2, count + 1)
    #         return
    #     print("DESTROYED SIGNAL RECEIVED 2")
    #     instance = weak_instance()
    #     if instance is not None:
    #         print("WARNING: SettingsDialog is still alive")
    #         import gc
    #         print(gc.get_referrers(instance))
    #         print("real window:")
    #         print(gc.get_referrers(instance.real_window()))
    #     else:
    #         print("Instance is now", instance)
    #
    # def monitor_instance():
    #     print("DESTROYED SIGNAL RECEIVED")
    #     call_after(monitor_instance_2, 1)
    #
    # weak_instance = weakref.ref(cls._window_instance)
    # # cls._window_instance.destroyed.connect(monitor_instance)
    # cls._window_instance.closed.connect(monitor_instance)

    # if getattr(cls, "_window_instance", None) and cls._window_instance():
    #     cls._window_instance().raise_and_activate()
    # else:
    #     window = cls(parent)
    #     window.show()
    #     cls._window_instance = weakref.ref(window)


def current_window_instance(cls: Any) -> Optional[TopLevelWidget]:
    if not hasattr(cls, "_window_instance"):
        return None
    assert isinstance(cls._window_instance, TopLevelWidget)
    return cls._window_instance
