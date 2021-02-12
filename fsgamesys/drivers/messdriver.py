import os
import shutil

from fsgamesys.drivers.mamedriver import MameDriver
from fsgamesys.saves import SaveHandler


class MessDriver(MameDriver):
    def __init__(self, fsgs, fsemu=False):
        super().__init__(fsgs, fsemu=fsemu)
        self.save_handler = MessSaveHandler(self.fsgc, options=self.options)

    def prepare(self):
        super().prepare()
        self.save_handler.prepare()
        self.create_mame_layout()

    def finish(self):
        super().finish()
        self.save_handler.finish()

    def is_pal(self):
        # return self.config.get("ntsc_mode") != "1"
        # return False
        refresh_rate = self.get_game_refresh_rate()
        if refresh_rate:
            return int(round(refresh_rate)) == 50

    def mame_emulator_name(self):
        return "mess"

    def mame_init_input(self):
        self.mess_init_input()

    def mess_init_input(self):
        pass

    def mame_romset(self):
        result = {}
        romset_name, files = self.mess_romset()
        for sha1, name in files.items():
            result[name] = sha1
        return romset_name, result

    def mess_romset(self):
        return self.get_mess_romset()

    def get_mess_romset(self):
        return "", {}

    # def mess_get_firmware_name(self):
    #     return self.context.game.platform + ' Firmware'

    def mame_prepare(self):
        pass
        # firmware_name = self.mess_get_firmware_name()
        # if firmware_name:
        #     self.mess_firmware_dir = self.prepare_firmware(firmware_name)
        # else:
        #     self.mess_firmware_dir = None

    def mame_configure(self):
        # self.add_arg(self.mess_romset()[0])
        # self.configure_mame()
        # with open(self.mednafen_cfg_path(), 'wb') as f:
        #     self._configure_emulator(f)
        # bios_dir = self.get_bios_dir()
        # if bios_dir:
        #     self.args.extend(['-rompath', bios_dir])
        # self.args.extend(['-joystick_deadzone', '0.15'])

        self.mess_configure()
        # self.mess_configure_media()

        if not self.mess_full_keyboard():
            # Start mess with UI keyboard keys enabled by default.
            # Full keyboard can be activated with INS / Scroll-Lock
            self.emulator.args.extend(["-ui_active"])

    def mess_full_keyboard(self):
        return False

    def mess_configure(self):
        """override in subclasses to provide custom configuration"""
        pass

    def mame_input_mapping(self, port):
        return self.mess_input_mapping(port)

    def mess_input_mapping(self, port):
        return self.get_mess_input_mapping(port)

    def get_mess_input_mapping(self, port):
        return None

    def mame_get_bios_dir(self):
        print("[DRIVER] MESS Firmware Dir:", self.mess_firmware_dir)
        return self.mess_firmware_dir

    def mess_offset_and_scale(self):
        return None

    def mame_offset_and_scale(self):
        result = self.mess_offset_and_scale()
        if result is not None:
            return result
        return super().mame_offset_and_scale()

    #    def mess_configure_media(self):
    #        pass

    def mess_configure_cartridge(self, slot="cart"):
        self.add_arg("-{0}".format(slot), self.get_game_file())

    def mess_configure_floppies(self, slots):
        # FIXME: this is a quick hack only..
        self.add_arg("-{0}".format(slots[0]), self.get_game_file())

    def inject_fake_input_string_list(self, delay, inject_string):
        self.set_env("FSGS_FAKE_INPUT_DELAY", str(delay))
        self.set_env("FSGS_FAKE_INPUT", "".join(inject_string))

    def inject_fake_input_string(self, delay, inject_string):
        def inject(inject_key_code):
            s.append("1{0:03d}".format(inject_key_code))
            s.append("0{0:03d}".format(inject_key_code))
            # we add some dummy events to slow down the keyboard entry

            # s.append("1000")
            s.append("0000")

        s = []
        for c in inject_string:
            if c == '"':
                # s.append("1304" + "1050" + "0050" + "0304")
                s.append("1225" + "1031" + "0031" + "0225")
            elif c in " ":
                # inject(32)
                inject(44)
            elif c in "\n":
                # inject(13)
                inject(40)
            elif c == "-":
                # inject(45)
                inject(45)
            elif c in "0123456789":
                # code = 48 + "0123456789".index(c)
                code = 30 + "1234567890".index(c)
                inject(code)
            elif c in "abcdefghijklmnopqrstuvwxyz":
                # code = 97 + "abcdefghijklmnopqrstuvwxyz".index(c)
                code = 4 + "abcdefghijklmnopqrstuvwxyz".index(c)
                inject(code)
            else:
                raise Exception(
                    "inject_fake_input_string cannot "
                    "handle '{0}' yet".format(c)
                )
        self.inject_fake_input_string_list(delay, s)


class MessSaveHandler(SaveHandler):
    def __init__(self, fsgc, options):
        super().__init__(fsgc, options, emulator="MAME")
        self._mame_driver = ""

    def prepare(self):
        # if self._emulator_specific:
        if self._mame_driver:
            # raise Exception("MAME driver not specified")
            self.copy_to_mame_dir()
        super().prepare()

    def finish(self):
        # if self._emulator_specific:
        if self._mame_driver:
            self.move_from_mame_dir()
        super().finish()

    def set_mame_driver(self, mame_driver):
        self._mame_driver = mame_driver

    def mame_save_dirs(self):
        save_dir = self.emulator_save_dir()
        mame_save_dir = os.path.join(save_dir, self._mame_driver)
        return save_dir, mame_save_dir

    def copy_to_mame_dir(self):
        save_dir, mame_save_dir = self.mame_save_dirs()
        if not os.path.exists(save_dir):
            return
        for full_name in os.listdir(save_dir):
            src = os.path.join(save_dir, full_name)
            if not os.path.isfile(src):
                continue
            name, ext = os.path.splitext(full_name)
            if ext not in [".srm"]:
                continue
            if not os.path.exists(mame_save_dir):
                os.makedirs(mame_save_dir)
            dst = os.path.join(mame_save_dir, name + ".nv")
            print("MessSaveHandler:", src, "->", dst)
            shutil.copy(src, dst)

    def move_from_mame_dir(self):
        save_dir, mame_save_dir = self.mame_save_dirs()
        if not os.path.exists(mame_save_dir):
            return
        for full_name in os.listdir(mame_save_dir):
            src = os.path.join(mame_save_dir, full_name)
            if not os.path.isfile(src):
                continue
            name, ext = os.path.splitext(full_name)
            if ext not in [".nv"]:
                print("MessSaveHandler: Removing", src)
                os.remove(src)
                continue
            dst = os.path.join(save_dir, name + ".srm")
            print("MessSaveHandler:", dst, "<-", src)
            shutil.copy(src, dst)
            os.remove(src)
        try:
            # FIXME: Maybe try to force removing this directory, at least
            # if we created it, and self._mame_driver is specified
            os.rmdir(mame_save_dir)
        except Exception:
            pass
