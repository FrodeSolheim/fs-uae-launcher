import traceback

from arcade.glui.font import Font
from arcade.glui.input import InputHandler
from arcade.glui.menu import Menu
from arcade.glui.opengl import fs_emu_blending, fs_emu_texturing
from OpenGL import GL as gl
from arcade.glui.render import Render
from arcade.glui.state import State
from arcade.glui.texture import Texture
from arcade.glui.topmenu import GameCenterItem
from fsgs.drivers.gamedriver import GameDriver
from fsgs.input.devicemanager import DeviceManager
from fsgs.input.inputdevice import InputDevice

from .launchmenu import LaunchMenu


class InputDevices(object):
    device_list_version = None


class DeviceDataDict(dict):
    def __getitem__(self, item):
        return super().__getitem__(item.upper())

    def __setitem__(self, key, value):
        return super().__setitem__(key.upper(), value)


class InputMenu(Menu):
    def __init__(self, item, controller):
        Menu.__init__(self)
        # self.top_menu_transition = 0.0
        self.items.append(item)
        if self.use_game_center_item():
            self.top.left.append(GameCenterItem())
        # self.top.left.append(HomeItem())
        # self.top.left.append(MenuItem(item.title))
        self.top.set_selected_index(
            len(self.top.left) + len(self.top.right) - 1
        )

        self.controller = controller
        assert isinstance(self.controller, GameDriver)
        self.first_shown_at = 0

        # controller must now initialize input ports
        # self.controller.init_input()

        # for input in self.controller.inputs:
        #     input["device_id"] = None

        # get all available input devices
        # self.devices, info = InputDevice.get_input_devices(
        #     "", 0, 100, version=2)

        device_manager = InputHandler.get_device_manager()
        # self.devices = DeviceManager.instance().get_devices()
        self.devices = device_manager.get_devices()

        self.device_list_version = InputDevices.device_list_version
        self.device_data = DeviceDataDict()
        # [{"index": 0} for x in self.devices]
        for device in self.devices:
            self.device_data[device.id] = {"port": 0, "device": device}
            self.check_device(self.device_data[device.id])
        # FIXME: Make InputHandler / InputDevice set variables
        # etc and self detect when to reinit?
        # InputHandler.reinit_joysticks()

        # calling activate to try to set the active input device
        # to the first input port, if possible
        # self.activate()
        self.set_defaults()

    def set_defaults(self):
        print("[INPUT] InputMenu.set_defaults")
        devices = []
        for device in self.devices:
            score = 0
            if device.id == InputHandler.last_device:
                score = -1
            devices.append([score, device])
        devices = [x[1] for x in sorted(devices)]
        print("[INPUT] Devices:", devices)
        for i, input_ in enumerate(self.controller.ports):
            print("[INPUT] Input port {0}:".format(i))
            for device in devices:
                try:
                    device.configure(input_.mapping_name)
                except Exception:
                    traceback.print_exc()
                    pass
                else:
                    print("  -> device id", device.id)
                    input_.device_id = device.id
                    input_.device = device
                    devices.remove(device)
                    self.device_data[device.id]["ok"] = True
                    self.device_data[device.id]["port"] = i
                    break

    def go_left(self, count=1):
        # device_id = InputHandler.last_device
        # for i, device in enumerate(self.devices):
        #     if not device.name == device_name:
        #         continue
        try:
            device_data = self.device_data[InputHandler.last_device]
        except KeyError as e:
            print(repr(e))
            return
        if device_data["port"] > 0:
            device_data["port"] -= 1
            # device_data["port"] -= 1
            self.check_device(device_data)

    def go_right(self, count=1):
        try:
            device_data = self.device_data[InputHandler.last_device]
        except KeyError as e:
            print(InputHandler.last_device)
            print(self.device_data)
            print(repr(e))
            return
        if device_data["port"] < len(self.controller.ports) - 1:
            device_data["port"] += 1
            # device_data["port"] += 1
            self.check_device(device_data)

            # device_name = InputHandler.last_device
            # for i, device in enumerate(self.devices):
            #     if not device.id == device_name:
            #         continue
            #     index = self.device_column[i]
            #     if index < len(self.controller.inputs) - 1:
            #         index += 1
            #         self.device_column[i] = index
            #         self.check_device(device)
            #     break

    # noinspection PyMethodMayBeStatic
    def on_status(self, status):
        print("received status", status)

    def run_game(self):
        new_menu = LaunchMenu(self.items[0], self.controller)

        State.get().history.append(new_menu)
        # FIXME
        from arcade.glui.window import set_current_menu

        set_current_menu(new_menu)

        # print("run_game, controller = ", id(self.controller))
        #
        # # FIXME:
        # from game_center.glui.window import run_game
        # #run_game({"controller": self.controller})
        # run_game(self.controller, self.on_status)
        #
        # go_back_to_game_selection = True
        #
        # # FIXME:
        # from game_center.glui.window import go_back
        # if go_back_to_game_selection:
        #     go_back()
        #     go_back()
        # else:
        #     # recreate controller for game menu
        #     #State.get().history[-2].recreate_controller()
        #     go_back()

    def activate(self):
        if len(self.controller.ports) == 0:
            return self.run_game()
        # print(self.device_data)
        # print("InputHandler.last_device", InputHandler.last_device)
        try:
            device_data = self.device_data[InputHandler.last_device]
        except KeyError as e:
            print(repr(e))
            return
        # device_data = self.device_data[InputHandler.last_device]
        if not device_data["ok"]:
            return
        port = device_data["port"]
        device = device_data["device"]
        # print("activate", port, device)
        for i in range(len(self.controller.ports)):
            if i == port:
                if i == 0 and device.id == self.controller.ports[i].device_id:
                    return self.run_game()
                self.controller.ports[i].device_id = device.id
                self.controller.ports[i].device = device
            elif self.controller.ports[i].device_id:
                # remove this device from other ports

                # if self.controller.inputs[i]["device"].id == device.id:
                if self.controller.ports[i].device_id == device.id:
                    self.controller.ports[i].device_id = None
                    self.controller.ports[i].device = None

    def check_device(self, device_data):
        device = device_data["device"]
        port = device_data["port"]
        try:
            # print("configuring device", device, "for",
            # self.controller.ports[port].mapping_name)
            device.configure(self.controller.ports[port].mapping_name)
        except InputDevice.MissingPlatformSupportException:
            device_data["ok"] = False
        except Exception as e:
            print(repr(e))
            device_data["ok"] = False
        else:
            device_data["ok"] = True
            # print(device, index, self.controller.inputs[index]["type"], ok)

    def render(self):
        if self.first_shown_at == 0:
            self.first_shown_at = State.get().time
        # FIXME:
        # from .gamemenu import render_wall, render_screen
        # glClear(GL_DEPTH_BUFFER_BIT)
        # render_wall()
        # render_screen()

        Render.get().hd_perspective()
        fs_emu_texturing(True)
        fs_emu_blending(False)
        Texture.sidebar_background.render(
            0, 0, 1920, Texture.sidebar_background.h
        )

        if len(self.controller.ports) == 0:
            color = (1.0, 0.0, 0.0, 1.0)
            text = "No input configuration needed"
            Render.get().text(
                text, Font.main_path_font, 200, 730, 400, color=color, halign=0
            )
            text = "Press enter or primary key to start game"
            Render.get().text(
                text, Font.main_path_font, 200, 670, 400, color=color, halign=0
            )
            return

        if self.device_list_version != InputDevices.device_list_version:
            print(" -- device list version changed")
            # self.devices, info = InputDevice.get_input_devices("", 0, 100,
            # version=2)
            self.devices = DeviceManager.instance().get_devices()
            self.device_list_version = InputDevices.device_list_version
            # [{"index": 0} for x in self.devices]
            device_ids = set()
            for device in self.devices:
                device_ids.add(device.id)
                try:
                    self.device_data[device.id]["device"] = device
                except KeyError:
                    print(" -- add device info for", device.id)
                    self.device_data[device.id] = {"port": 0, "device": device}
                    self.check_device(self.device_data[device.id])
            for data_key in self.device_data.keys():
                if data_key not in device_ids:
                    print(" -- removing device_data for", data_key)
                    del self.device_data[data_key]
            for input_ in self.controller.ports:
                if not input_["device_id"] in device_ids:
                    print(" -- removing device from input", input_.device_id)
                    input_["device_id"] = None

        for port, input_ in enumerate(self.controller.ports):
            center_x = 400 + 400 * port

            text = input_.name.upper()
            color = (1.0, 0.0, 0.0, 1.0)
            Render.get().text(
                text,
                Font.main_path_font,
                center_x - 200,
                760,
                400,
                color=color,
                halign=0,
            )
            text = input_.description.upper()
            color = (1.0, 0.0, 0.0, 1.0)
            Render.get().text(
                text,
                Font.main_path_font,
                center_x - 200,
                730,
                400,
                color=color,
                halign=0,
            )
            if input_.device_id:
                device = self.device_data[input_.device_id]["device"]
                color = (1.0, 0.5, 0.5, 1.0)
                text = device.name.upper()
                Render.get().text(
                    text,
                    Font.main_path_font,
                    center_x - 200,
                    680,
                    400,
                    color=color,
                    halign=0,
                )

            for j, device in enumerate(self.devices):
                device_data = self.device_data[device.id]
                # print(1, repr(device))
                if device_data["port"] != port:
                    continue
                text = device.name.upper()
                if device_data["ok"]:
                    color = (1.0, 1.0, 1.0, 1.0)
                else:
                    color = (0.5, 0.5, 0.5, 1.0)
                Render.get().text(
                    text,
                    Font.main_path_font,
                    center_x - 200,
                    600 - j * 40,
                    400,
                    color=color,
                    halign=0,
                )

        fade = 1.0 - (State.get().time - self.first_shown_at) * 3.0
        if fade > 0.0:
            Render.get().dirty = True
            # fs_emu_blending(True)
            # fs_emu_texturing(False)
            gl.glDisable(gl.GL_DEPTH_TEST)
            Render.get().hd_perspective()
            # gl.glBegin(gl.GL_QUADS)
            # gl.glColor4f(0.0, 0.0, 0.0, fade)
            # gl.glVertex2f(0, 0)
            # gl.glVertex2f(1920, 0)
            # gl.glVertex2f(1920, 1080)
            # gl.glVertex2f(0, 1080)
            # gl.glEnd()
            Render.get().hd_perspective()
            fs_emu_texturing(True)
            fs_emu_blending(False)
            Texture.sidebar_background.render(
                0, 0, 1920, Texture.sidebar_background.h, opacity=fade
            )
            gl.glEnable(gl.GL_DEPTH_TEST)
