import time
import threading
import traceback
from uuid import uuid4
from fsgs.input.enumeratehelper import EnumerateHelper
from fsgs.platform import PlatformHandler


class Instance:

    STATE_INITIALIZED = "INITIALIZED"
    STATE_PREPARING = "PREPARING"
    STATE_READY = "READY"
    STATE_RUNNING = "RUNNING"
    STATE_STOPPED = "STOPPED"
    STATE_FINALIZING = "FINALIZING"
    STATE_FINALIZED = "FINALIZED"

    def __init__(self, fsgs, instance_uuid):
        self.fsgs = fsgs
        self.uuid = instance_uuid
        self.thread = None
        self.runner = None
        self._state = self.STATE_INITIALIZED

    def get_state(self):
        return self._state

    def set_state(self, state):
        self._state = state

    state = property(get_state, set_state)

    def start(self):
        assert self.thread is None

        platform_handler = PlatformHandler.create(self.fsgs.game.platform.id)
        self.runner = platform_handler.get_runner(self.fsgs)

        device_helper = EnumerateHelper()
        device_helper.default_port_selection(self.runner.ports)

        self.thread = threading.Thread(target=self._thread)
        self.thread.start()

    def _thread(self):
        try:
            while self.state == self.STATE_INITIALIZED:
                time.sleep(0.1)
            assert self.state == self.STATE_PREPARING

            self.runner.prepare()
            self.state = self.STATE_READY

            while self.state == self.STATE_READY:
                time.sleep(0.1)
            assert self.state == self.STATE_RUNNING

            process = self.runner.run()
            process.wait()
            self.state = self.STATE_STOPPED

            while self.state == self.STATE_STOPPED:
                time.sleep(0.1)
            assert self.state == self.STATE_FINALIZING

            self.runner.finish()
            self.state = self.STATE_FINALIZED
        except Exception:
            print("EXCEPTION IN Instance.thread")
            traceback.print_exc()

    def destroy(self):
        print("Instance.destroy")


class Session:
    def __init__(self, fsgs):
        self.fsgs = fsgs

    def create_instance(self):
        assert self.fsgs.game.uuid
        assert self.fsgs.game.variant.uuid

        instance = Instance(self.fsgs, str(uuid4()))
        return instance
