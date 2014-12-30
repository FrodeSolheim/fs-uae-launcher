class Option(object):

    def __init__(self):
        self.priority = 0.0
        self.group = False
        self.title = "Option Title"
        self.subtitle = ""

    def activate(self):
        pass

    @classmethod
    def create_play_option(cls):
        return PlayOption()

    @classmethod
    def create_config_option(cls):
        return ConfigOption()

    @classmethod
    def create_screen_option(cls):
        return ScreenOption()

    @classmethod
    def create_aspect_option(cls):
        return AspectOption()

    @classmethod
    def create_group(cls, title, priority=0.0):
        option = Option()
        option.priority = priority
        option.title = title
        option.group = True
        return option


class PlayOption(Option):

    def __init__(self):
        Option.__init__(self)
        self.priority = -2.0
        self.title = "Play Game"
        self.subtitle = "Play Game"

    def activate(self):
        print("PlayItem.activate")
        return 'PLAY'


class ConfigOption(Option):

    def __init__(self):
        Option.__init__(self)
        self.priority = -1.0
        self.title = "CONFIGURATION NAME"
        self.subtitle = "Choose Configuration"

    def activate(self):
        print("ChooseConfigItem.activate")
        return [

        ]


class AspectOption(Option):

    def __init__(self):
        Option.__init__(self)
        self.priority = 98.0
        self.title = "FILL ENTIRE DISPLAY"
        self.subtitle = "Display Configuration"

    def activate(self):
        print("AspectItem.activate")
        return [

        ]


class ScreenOption(Option):

    def __init__(self):
        Option.__init__(self)
        self.priority = 99.9
        self.title = "FULL-SCREEN 50HZ V"
        self.subtitle = "Screen Configuration"

    def activate(self):
        print("DisplayItem.activate")
        return [

        ]
