import time

from arcade.notification import Notification
from fsgamesys.input.device import Device
from fsgamesys.input.devicemanager import DeviceManager
from fsgamesys.input.eventhelper import EventHelper

CHECK_DELAY = 0.5


class EventListener:
    def __init__(self):
        self.helper = EventHelper()
        self.helper.init()
        self.device_names = {}
        self.device_manager = DeviceManager(None)
        self.remove_count = 0
        self.restart_after_add_count = 0
        self.reinit_time = 0.0
        self.check_time = 0.0
        self.check_list = None

    def get_next_event(self):
        # print(self.reinit_time - self.check_time)
        if self.reinit_time > self.check_time:
            delay = CHECK_DELAY
            if self.check_time == 0.0:
                # Force longer delay on startup to suppress false insert
                # notifications on the initial set of devices.
                delay = 2.5
            if time.time() - self.reinit_time > delay:
                self.check_for_device_changes()

        event = self.helper.get_next_event()
        if event is None:
            return None

        if self.helper.is_remove_event(event):
            print("[INPUT] Remove event:", event)
            # Restarting event helper so all devices are re-enumerated
            self.remove_count += 1
            self.reinit()

        if self.helper.is_add_event(event):
            if self.restart_after_add_count < self.remove_count:
                # New device added after a device has been removed. Restarting
                # device helper so device enumeration is consistent.
                # Enumeration must be the same as emulators will do by
                # themselves.
                self.restart_after_add_count += 1
                self.reinit()
                return

            count = self.device_names.get(event["name"], 0) + 1
            self.device_names[event["name"]] = count
            if count > 1:
                event["id"] = "{0} #{1}".format(event["name"], count)
            else:
                event["id"] = event["name"]
            # self.event_id = event["type"] + "-" + event["device"]
            self.device_manager.add_device_from_event(event)
            # self.notification((device.type, device.id))
            # self.check_for_device_changes()
            self.reinit_time = time.time()

        return event

    def reinit(self):
        self.device_manager.remove_all_devices()
        self.device_names = {}
        self.helper = EventHelper()
        self.helper.init()
        self.reinit_time = time.time()

    def check_for_device_changes(self):
        print("[INPUT] Checking for device change notifications")
        print(time.time(), self.reinit_time, self.check_time)
        new_list = []
        for device in self.device_manager.get_devices():
            new_list.append((device.type, device.id))
        old_list = self.check_list
        if old_list is not None:
            print("[INPUT] Old:", old_list)
            print("[INPUT] New:", new_list)
            old_set = set(old_list)
            new_set = set(new_list)
            for item in old_list:
                if item not in new_set:
                    self.notification(item, "Removed")
            for item in new_list:
                if item not in old_set:
                    self.notification(item, "Added")
        self.check_list = new_list
        self.check_time = time.time()

    def notification(self, item, action):
        if item[0] == Device.TYPE_JOYSTICK:
            text = "Joystick {}:\n{}".format(action, item[1])
        elif item[0] == Device.TYPE_KEYBOARD:
            text = "Keyboard {}:\n{}".format(action, item[1])
        elif item[0] == Device.TYPE_MOUSE:
            text = "Mouse {}:\n{}".format(action, item[1])
        else:
            text = "Device {}:\n{}".format(action, item[1])
        Notification(text)
