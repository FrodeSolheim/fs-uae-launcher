import sys

# import traceback
from collections import defaultdict

from fsbc.settings import Settings
from fsgs.config.configevent import ConfigEvent
from fsgs.contextaware import ContextAware
from fsgs.options.option import Option


class Config(ContextAware):
    def __init__(self, context):
        ContextAware.__init__(self, context)
        self.values = {}
        self.log_config = (
            Settings.instance().get(Option.LAUNCHER_LOG_CONFIG) == "1"
        )
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self, event):
        for observer in self.observers:
            # An instance with an update function, or a plain function, can
            # both be observers. Also supports Old-style on_config method.
            if hasattr(observer, "on_config"):
                observer.on_config(event.key, event.value)
            elif hasattr(observer, "update"):
                observer.update(event)
            else:
                observer(event)

    # @deprecated
    def add_listener(self, listener):
        self.attach(listener)

    # @deprecated
    def remove_listener(self, listener):
        self.detach(listener)

    def add_behavior(self, instance, options):
        # FIXME: Move to fsgs
        from launcher.ui.behaviors.configbehavior import ConfigBehavior

        ConfigBehavior(instance, options)

    def copy(self):
        # Return a defaultdict so lookups for unset keys returns empty strings.
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

    @staticmethod
    def config_from_argv():
        config = []
        for arg in sys.argv:
            if arg.startswith("--config:"):
                arg = arg[9:]
                key, value = arg.split("=", 1)
                key = key.replace("-", "_")
                config.append((key, value))
        return config

    def add_from_argv(self):
        """Adds config parameters from argv to currently loaded configuration.
        :return: True if config parameters were used.
        """
        config_items = self.config_from_argv()
        for key, value in config_items:
            self.set(key, value)
        return len(config_items) > 0

    def load(self, values):
        self.clear()
        for key, value in list(values.items()):
            self.set(key, value)

    def load_from_file(self):
        pass

    def clear_and_set(self, values):
        new_config = {}
        for key, value in values:
            new_config[key] = value
        # First, check which options we need to clear.
        for key in self.values.keys():
            if key not in new_config:
                new_config[key] = ""
        # Now, set new config while simultaneously clearing old values.
        self.set(new_config.items())
        # Remove keys for empty values to avoid ever-growing set of keys. Not
        # really needed, but nice.
        for key, value in new_config.items():
            if not value:
                del self.values[key]

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
            if self.log_config:
                print(
                    "[CONFIG] set {0} to {1}".format(
                        changed_key, changed_value
                    )
                )
            # if changed_key == "__changed" and changed_value == "1":
            #     print("Stack trace for event causing __changed = 1:")
            #     traceback.print_stack()
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

                # FIXME: Deprecated
                self.context.signal.notify("config", (key, value))

                self.notify(ConfigEvent(key, value))

            # FIXME: reset __netplay_ready...
            # if "__netplay_ready" not in changed_keys:
            #     cls.set("__netplay_ready", "0")
            #
            # Settings.set("config_changed", "1")

    def set_multiple(self, values):
        self.set(values)
