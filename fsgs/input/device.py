from fsbc.system import windows, linux, macosx


class Device(object):

    TYPE_KEYBOARD = "keyboard"
    TYPE_JOYSTICK = "joystick"
    TYPE_MOUSE = "mouse"

    def __init__(self):
        self.id = ""
        self.name = ""
        self.type = ""
        # self.port = None
        # self.cmp_id = create_cmp_id(id)

        self.index = 0
        self.balls = 0
        self.hats = 0
        self.axes = 0
        self.buttons = 0

    def __lt__(self, other):
        if self.index < other.index:
            return True
        return self.name < other.name

    @property
    def sdl_name(self):
        # FIXME: check sdl_name usage
        return self.name

    def is_keyboard(self):
        # print("id:", self.id)
        # print("name:", self.name)
        # print("type:", self.type)
        return self.type == self.TYPE_KEYBOARD

    def get_config_name(self):
        name = self.name.rsplit("#", 1)[0]
        name_lower = name.lower()
        name = ""
        for c in name_lower:
            if c in "abcdefghijklmnopqrstuvwxyz0123456789":
                name += c
            else:
                if not name.endswith("_"):
                    name += "_"
        name = name.strip("_")

        if windows:
            host_platform = "windows"
        elif macosx:
            host_platform = "macos"
        elif linux:
            host_platform = "linux"
        else:
            host_platform = "other"

        config_name = "{0}_{1}_{2}_{3}_{4}_{5}".format(
            name, self.buttons, self.axes, self.hats, self.balls,
            host_platform)
        return config_name

    def configure(self, system):
        name = self.name.rsplit("#", 1)[0]
        from fsgs.input.inputdevice import InputDevice
        try:
            # device id must end with #something (really a device number,
            # but can be anything
            device = InputDevice(
                system, name + " #DUMMY", [], version=2, axes=self.axes,
                hats=self.hats, buttons=self.buttons, balls=self.balls)
            config = device.get_config()
        except Exception as e:
            print("error initializing device {0} for {1}".format(
                self.name, system))
            print(repr(e))
            # return {}
            raise e
        # config_inv = []
        for key, val in list(config.items()):
            val = val.upper()
            config[key] = val
            config[val] = key
        return config

    def __repr__(self):
        return "<Device '{0}'>".format(self.id)
