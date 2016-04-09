import sys
from collections import defaultdict

from .ContextAware import ContextAware


class Config(ContextAware):

    def __init__(self, context):
        ContextAware.__init__(self, context)
        self.values = {}

    def add_behavior(self, instance, options):
        # FIXME: Move to fsgs
        from launcher.ui.behaviors.configbehavior import ConfigBehavior
        ConfigBehavior(instance, options)

    def copy(self):
        # return a defaultdict so lookups for unset keys return an empty string
        return defaultdict(str, self.values)

    def get(self, key, default=""):
        return self.values.get(key, default)

    def items(self):
        return self.values.items()

    def clear(self):
        for key in list(self.values.keys()):
            value = self.values[key]
            if value:
                self.set(key, "")
        # for key in self.values.keys():
        #     del self.values[key]

    def add_from_argv(self):
        for arg in sys.argv:
            if arg.startswith("--config:"):
                arg = arg[9:]
                key, value = arg.split("=", 1)
                key = key.replace("-", "_")
                self.set(key, value)

    def load(self, values):
        self.clear()
        for key, value in list(values.items()):
            self.set(key, value)

    def set(self, *values):
        if len(values) == 1:
            # Config.set_multiple(*values)
            items = list(values[0])
        elif len(values) == 2:
            items = [(values[0], values[1])]
        else:
            raise Exception("Invalid number of parameters to set_config")

        item_keys = [x[0] for x in items]
        changed_keys = set()

        def add_changed_key(added_key):
            # try:
            #     added_priority = cls.key_order.index(added_key)
            # except ValueError:
            #     added_priority = 1000
            added_priority = 0
            # FIXME: re-introduce support for key priority if necessary
            changed_keys.add((added_priority, added_key))

        def change(changed_key, changed_value):
            # print("change", changed_key, changed_value)
            # if key == "joystick_port_1_mode":
            #     pass
            if old_config.get(changed_key, None) == changed_value:
                # if changed_value:
                #     print("config set {0} to {1} (no change)".format(
                #         changed_key, changed_value))
                return
            print("config set {0} to {1}".format(changed_key, changed_value))
            add_changed_key(changed_key)
            self.values[changed_key] = changed_value

        old_config = self.values.copy()
        for key, value in items:
            change(key, value)
            # we now reset x_key_sha1 keys, so if a file option was set without
            # simultaneously specifying the _sha1 key, that key will be reset.
            reset_key = "x_" + key + "_sha1"
            if reset_key not in item_keys:
                if reset_key in self.values:
                    change(reset_key, "")

        # and now broadcast all changed keys at once
        changed_key_list = [x[1] for x in changed_keys]

        if len(changed_keys) > 0:
            if "__ready" not in changed_key_list:
                change("__ready", "0")
            for key in changed_key_list:
                if not key.startswith("__implicit_"):
                    change("__changed", "1")
                    break
            for priority, key in sorted(changed_keys):
                # for listener in cls.config_listeners:
                #     listener.on_config(key, cls.get(key))

                value = self.get(key)
                # Signal.broadcast("config", key, value)
                self.context.signal.notify("config", (key, value))

            # FIXME: reset __netplay_ready...
            # if "__netplay_ready" not in changed_keys:
            #     cls.set("__netplay_ready", "0")
            #
            # Settings.set("config_changed", "1")
