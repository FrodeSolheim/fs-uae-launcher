from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import time
import traceback

from fsbc.util import memoize
from fsgs.input.keyboard import Keyboard
from fsgs.input.inputdevice import InputDevice
from fsgs.input.manager import DeviceManager
from fsgs.input.eventlistener import EventListener
from game_center.resources import logger


REPEAT_THRESHOLD = 0.300
REPEAT_INTERVAL = 0.075


def get_controller_config(name, sdl_name, axes=0, hats=0, buttons=0, balls=0):
    try:
        # device id must end with #something (really a device number,
        # but can be anything
        device = InputDevice(
            "menu", name + " #MENU", [], sdl_name=sdl_name,
            version=2, axes=axes, hats=hats, buttons=buttons, balls=balls)
        config = device.get_config()
    except Exception:
        print("error initializing device " + repr(name) + " for menu")
        traceback.print_exc()
        #print(repr(e))
        return None
    #config_inv = []
    for key, val in list(config.items()):
        val = val.upper()
        config[key] = val
        config[val] = key
    return config


@memoize
def get_controller_instance(name):
    #print("get_controller_instance")
    #name = name.upper()
    #instances = {}
    #for ext in pyapp.ext.ExtensionHook(
    #        "exthook:no.fengestad.input/device"):
    #    klass = ext.object
    #    print(klass)
    #
    #    for ccname in ext.models:
    #        #print(name)
    #        if ccname.startswith("^"):
    #            #print("reg", ccname, "vs", name)
    #            if re.match(ccname, name) is not None:
    #                #print("match")
    #                #klass = cc
    #                break
    #        elif name == ccname:
    #            #klass = cc
    #            break
    #    else:
    #        #print("no input device class found")
    #        continue
    #    try:
    #        instance = klass("menu", "", [])
    #    except Exception:
    #        logger.exception("Could not initialize controller for menu")
    #        continue
    #    #for name in ext.models:
    #    #    ctrlclasses[name.upper()] = klass
    #    #instance = klass()
    #    #for name in ext.models:
    #    #    print(name)
    #    #    instances[name.upper()] = instance
    #    return instance
    #print("no input device class found")
    return None


class InputHandler(object):

    last_device = ""
    joystick_hash = None
    last_joystick_check = 0
    current_button = None
    repeat_info = None
    repeatable_buttons = ["UP", "DOWN", "LEFT", "RIGHT", "BACK"]
    #last_joystick_count = 0
    joysticks = []
    axis_status = {}
    first_init = True
    device_sdl_names = {}
    key_table = {}
    event_listener = None
    event_queue = []

    @classmethod
    def get_virtual_button(cls, event):
        # print("get_virtual_button", event)
        assert isinstance(event, dict)
        if event["type"] in ["key-down", "key-up"]:
            try:
                key = Keyboard.key(event)
            except Exception:
                traceback.print_exc()
                #print(repr(e))
                return None, None
            try:
                button, device_id = cls.key_table[key.name]
            except Exception:
                traceback.print_exc()
                return None, None

            #if button:
            #    #cls.last_device = "KEYBOARD #1"
            #    cls.last_device = device_id
            #print("get_virtual_button", button, cls.last_device)
            return button, device_id
        elif event["type"] in ["joy-button-down", "joy-button-up",
                               "joy-axis-motion", "joy-hat-motion"]:
            if event["type"] == "joy-axis-motion":
                # print(event)
                #if event.value > -0.5 and event.value < 0.5:
                #    return None
                #sign = "-" if event.value < 0 else "+"
                sign = "neg" if event["state"] < 0 else "pos"
                cfg_name = "axis_{0}_{1}".format(event["axis"], sign)
            elif event["type"] == "joy-hat-motion":
                print(event)
                if event["state"] & 8:
                    value = "left"
                elif event["state"] & 2:
                    value = "right"
                elif event["state"] & 4:
                    value = "down"
                elif event["state"] & 1:
                    value = "up"
                else:
                    value = "0"
                cfg_name = "hat_{0}_{1}".format(event["hat"], value)
            else:
                cfg_name = "button_{0}".format(event["button"])

            #try:
            #    joystick = cls.joysticks[event["device"]]
            #except IndexError:
            #    return None, None
            #print(joystick)
            #controller = get_controller_instance(joystick.name)
            #if controller is None:
            #    return None
            ##klass.get_
            #config = controller.get_config()
            #config_inv = controller.get_config_inverted()

            config = cls.get_controller_config(event["device"])
            if config is None:
                return None, None

            joystick = cls.joysticks[event["device"]]
            try:
                button = config[cfg_name]
            except KeyError:
                return None, None

            #print(button)
            if button == "START":
                combine = "SELECT"
            elif button == "SELECT":
                combine = "START"
            else:
                combine = None
            # if combine:
            #     try:
            #         menu = False
            #         #back = False
            #         skip_left = False
            #         skip_right = False
            #         b = config[combine]
            #         if b.startswith("button_"):
            #             b = int(b[7:])
            #             if joystick.joy_object.get_button(b):
            #                 menu = True
            #         b = config["SKIP_LEFT"]
            #         if b.startswith("button_"):
            #             b = int(b[7:])
            #             if joystick.joy_object.get_button(b):
            #                 skip_left = True
            #         b = config["SKIP_RIGHT"]
            #         if b.startswith("button_"):
            #             b = int(b[7:])
            #             if joystick.joy_object.get_button(b):
            #                 skip_right = True
            #         if menu:
            #             if skip_left and skip_right:
            #                 print("ABORT")
            #                 return "ABORT", joystick.id
            #             print("MENU")
            #             return "MENU", joystick.id
            #     except KeyError:
            #         pass

            # if button:
            #     print("setting last device to", joystick.id, "event", event)
            #     cls.last_device = joystick.id

            return button, joystick["id"]

    @classmethod
    @memoize
    def get_controller_config(cls, index):
        try:
            joystick = cls.joysticks[index]
        except IndexError:
            print("no joystick at index", index)
            return None

        return get_controller_config(
            joystick["name"], joystick["name"], axes=joystick["axes"],
            hats=joystick["hats"], buttons=joystick["buttons"],
            balls=joystick["balls"])

    # @classmethod
    # def handle_keydown_event(cls, event):
    #     #global current_button
    #
    #     if event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
    #         cls.current_button = "LEFT"
    #     elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
    #         cls.current_button = "RIGHT"
    #     elif event.key == pygame.K_PAGEUP or event.key == pygame.K_LSHIFT:
    #         cls.current_button = "FLEFT"
    #     elif event.key == pygame.K_PAGEDOWN or event.key == pygame.K_RSHIFT:
    #         cls.current_button = "FRIGHT"
    #     elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
    #         cls.current_button = "OK"
    #     elif event.key == pygame.K_BACKSPACE:
    #         cls.current_button = "BACK"
    #     elif event.key == pygame.K_ESCAPE:
    #         cls.current_button = "QUIT"

    @classmethod
    def handle_device_event(cls, event):
        if event["type"] == "joy-device-added":
            print("ADDED device", event)
            cls.joysticks.append(event)

    @classmethod
    def handle_event(cls, event):
        assert isinstance(event, dict)
        down_event = False
        up_event = False
        if event["type"] == "key-down" or event["type"] == "joy-button-down":
            virtual_button, device_id = cls.get_virtual_button(event)
            down_event = True
        elif event["type"] == "key-up" or event["type"] == "joy-button-up":
            virtual_button, device_id = cls.get_virtual_button(event)
            up_event = True
        elif event["type"] == "joy-hat-motion":
            axis_name = "%d_%d" % (event["device"], 1000 + event["hat"])
            try:
                if cls.axis_status[axis_name] != event["state"]:
                    up_event = True
                    cls.repeat_info = None
            except KeyError:
                pass
            cls.axis_status[axis_name] = event["state"]
            virtual_button, device_id = cls.get_virtual_button(event)
            if virtual_button:
                down_event = True
        elif event["type"] == "joy-axis-motion":
            virtual_button, device_id = cls.get_virtual_button(event)
            axis_name = "%d_%d" % (event["device"], event["axis"])
            #if event.axis == 6:
            #    print(axis_name, virtual_button, event.value)
            if event["state"] < -0.66 * 32768:
                if cls.axis_status.setdefault(axis_name, 0) != -1:
                    cls.axis_status[axis_name] = -1
                    down_event = True
            elif event["state"] > 0.66 * 32768:
                if cls.axis_status.setdefault(axis_name, 0) != 1:
                    cls.axis_status[axis_name] = 1
                    down_event = True
            elif -0.33 * 32768 < event["state"] < 0.33 * 32768:
                if cls.axis_status.setdefault(axis_name, 0) != 0:
                    #print("axis status", cls.axis_status[axis_name])
                    cls.axis_status[axis_name] = 0
                    up_event = True
        elif event["type"] == "joy-device-added":
            return cls.handle_device_event(event)
        else:
            return
        if down_event:
            if virtual_button:
                #print(virtual_button, down_event, up_event)
                cls.current_button = virtual_button
                if virtual_button in cls.repeatable_buttons:
                    t = time.time()
                    cls.repeat_info = [virtual_button, t, t]
                #cls.last_device_id = device_id
                cls.last_device = device_id
                # print("last device is", device_id)
        elif up_event:
            if virtual_button:
                #print("up event", event)
                cls.repeat_info = None

    @classmethod
    def update(cls):
        cls.update_joysticks()
        cls.update_repeat()

    @classmethod
    def update_repeat(cls):
        t = time.time()
        if cls.repeat_info:
            if t - cls.repeat_info[1] > REPEAT_THRESHOLD:
                if t - cls.repeat_info[2] > REPEAT_INTERVAL:
                    cls.current_button = cls.repeat_info[0]
                    cls.repeat_info[2] = t

    @classmethod
    def update_joysticks(cls):
        if cls.event_listener is None:
            return
        while True:
            event = cls.event_listener.get_next_event()
            if not event:
                break
            InputHandler.handle_event(event)

    @classmethod
    def add_event(cls, event):
        #if event["type"] == "text":
        #    cls.text_events.append(event)
        cls.event_queue.append(event)

    @classmethod
    def pop_event(cls):
        return cls.event_queue.pop()

    @classmethod
    def pop_all_events(cls):
        events = cls.event_queue[:]
        cls.event_queue.clear()
        return events

    @classmethod
    def peek_button(cls):
        button = cls.current_button
        return button

    @classmethod
    def get_button(cls):
        button = cls.current_button
        cls.current_button = None
        return button

    @classmethod
    def clear_current_button(cls):
        cls.current_button = None
        cls.repeat_info = None

    @classmethod
    def close(cls):
        cls._close_joysticks()

    @classmethod
    def open(cls):
        cls._open_joysticks()
        if cls.event_listener is None:
            cls.event_listener = EventListener()

    @classmethod
    def get_device_manager(cls):
        return cls.event_listener.manager

    @classmethod
    def reinit_joysticks(cls):
        print("\n" + "-" * 79 + "\n" + "INPUTHANDLER REINIT JOYSTICKS")
        print("reinit_joysticks")
        cls.axis_status = {}

        # for joystick in cls.joysticks:
        #     print("    uninitialize", joystick)
        #     joystick.joy_object.quit()

        # FIXME: stop using the Device Manager instance here?

        device_manager = DeviceManager.instance()
        devices = device_manager.get_devices()

        cls.key_table = {}
        for device in devices:
            print("device")
            if device.is_keyboard():
                print("is keyboard device")
            else:
                continue
            config = get_controller_config(
                device.name, device.sdl_name,
                axes=device.axes, hats=device.hats,
                buttons=device.buttons, balls=device.balls)
            print(config)
            if not config:
                continue
            for key, value in config.items():
                if key.startswith("key_"):
                    cls.key_table["SDLK_" + key[4:].upper()] = \
                        (value.upper(), device.id)

    @classmethod
    def _open_joysticks(cls):
        logger.debug("InputHandler._open_joysticks")
        cls.reinit_joysticks()

    @classmethod
    def _close_joysticks(cls):
        pass
