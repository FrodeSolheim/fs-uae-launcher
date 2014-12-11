from .eventhelper import EventHelper
from .manager import DeviceManager


class EventListener:

    def __init__(self):
        self.helper = EventHelper()
        self.helper.init()
        self.device_names = {}
        self.manager = DeviceManager(None)

    def get_next_event(self):
        event = self.helper.get_next_event()
        if event is None:
            return None

        if event["type"] in ["joy-device-added", "mouse-device-added",
                             "keyboard-device-added"]:
            count = self.device_names.get(event["name"], 0) + 1
            self.device_names[event["name"]] = count
            if count > 1:
                event["id"] = "{0} #{1}".format(event["name"], count)
            else:
                event["id"] = event["name"]

            if event["type"] == "joy-device-added":
                self.manager.add_joystick_device(event)
            elif event["type"] == "mouse-device-added":
                self.manager.add_mouse_device(event)
            elif event["type"] == "keyboard-device-added":
                self.manager.add_keyboard_device(event)

        return event
