from fsgs.mame.mame import MAMERunner


class MESSRunner(MAMERunner):

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
        return self.mess_romset()

    def mess_romset(self):
        pass

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
        self.add_arg(self.mess_romset()[0])
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
            # start mess with UI keyboard keys enabled by default,
            # full keyboard can be activated with INS / Scroll-Lock
            self.add_arg("-ui_active")

    def mess_full_keyboard(self):
        return False

    def mess_configure(self):
        """override in subclasses to provide custom configuration"""
        pass

    def run(self):
        # return self.start_emulator("fs-mess/mess")
        return self.start_emulator_from_plugin_resource("mess")

    def mame_input_mapping(self, port):
        return self.mess_input_mapping(port)

    def mess_input_mapping(self, port):
        pass

    def mame_get_bios_dir(self):
        print("xxxxxxxxx", self.mess_firmware_dir)
        return self.mess_firmware_dir

    def mess_offset_and_scale(self):
        raise NotImplementedError()

    def mame_offset_and_scale(self):
        try:
            return self.mess_offset_and_scale()
        except NotImplementedError:
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
                s.append("1304105000500304")
            elif c in " ":
                inject(32)
            elif c in "\n":
                inject(13)
            elif c == '-':
                inject(45)
            elif c in "0123456789":
                code = 48 + "0123456789".index(c)
                inject(code)
            elif c in "abcdefghijklmnopqrstuvwxyz":
                code = 97 + "abcdefghijklmnopqrstuvwxyz".index(c)
                inject(code)
            else:
                raise Exception("inject_fake_input_string cannot "
                                "handle '{0}' yet".format(c))

        self.inject_fake_input_string_list(delay, s)
