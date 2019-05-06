import json
import atexit
from queue import Queue, Empty
from threading import Thread
import traceback
import subprocess
from fsgs.amiga.fsuaedevicehelper import FSUAEDeviceHelper


class EventHelper(Thread):
    def __init__(self):
        Thread.__init__(self, name="EventHelperThread")
        self.setDaemon(True)

        self.devices = []
        self.joystick_devices = []
        self.keyboard_devices = []
        self.joystick_like_devices = []
        self.initialized = False

        self.process = None
        self.events = Queue()
        self.stopping = False

    def init(self):
        if self.initialized:
            return
        self.init_device_helper()
        self.initialized = True

    def deinit(self):
        self.stopping = True

    def is_add_event(self, event):
        return event["type"] in [
            "joy-device-added",
            "mouse-device-added",
            "keyboard-device-added",
        ]

    def is_remove_event(self, event):
        return event["type"] in [
            "joy-device-removed",
            "mouse-device-removed",
            "keyboard-device-removed",
        ]

    def get_next_event(self):
        try:
            event = self.events.get(False)
            return event
        except Empty:
            return None

    def run(self):
        try:
            self._run()
        except Exception:
            traceback.print_exc()
        try:
            self.process.kill()
        except Exception:
            traceback.print_exc()
        self.process = None

    def _run(self):
        print("[INPUT] EventHelper thread started")
        while not self.stopping:
            line = self.process.stdout.readline()
            line = line.decode("UTF-8", "replace")
            if not line:
                print("no line returned from device helper")
                break
            if line.startswith("#"):
                continue
            try:
                event = json.loads(line)
            except Exception:
                print("Problem loading JSON from line:", line)
                continue
            # print(event)
            self.events.put(event)
        print("[INPUT] EventHelper thread stopping")
        self.process.kill()
        atexit.unregister(self.kill_device_helper_on_exit)

    def init_device_helper(self):
        print("EventHelper.init_device_helper")
        try:
            self.process = FSUAEDeviceHelper.start_with_args(
                ["--events"], stdout=subprocess.PIPE
            )
        except Exception:
            print("exception while listing joysticks and devices")
            traceback.print_exc()
            return

        atexit.register(self.kill_device_helper_on_exit)
        self.start()

    def kill_device_helper_on_exit(self):
        print("[INPUT] Killing device helper process (on exit)")
        self.process.kill()
