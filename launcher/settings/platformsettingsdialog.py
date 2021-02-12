import fsui
from fsgamesys.platforms.platform import Platform
from launcher.option import Option
from launcher.settings.option_ui import OptionUI


class PlatformSettingsDialog(fsui.Window):
    @classmethod
    def open(cls, parent, platform):
        # return fsui.open_window_instance(cls, parent)
        dialog = cls(parent, platform)
        dialog.show()
        return dialog

    def __init__(self, parent, platform):
        title = "Platform Settings: " + platform.upper()
        super().__init__(parent, title)
        # self.layout = fsui.VerticalLayout()
        buttons, layout = fsui.DialogButtons.create_with_layout(self)
        # if self.window().theme.has_close_buttons:
        # buttons.create_close_button()

        # self.layout.padding = 10

        for option in self.option_list_for_platform(platform):
            self.add_option(layout, option)

        self.set_size((600, 400))

    def add_option(self, layout, option, platforms=None, text=""):
        panel = fsui.Panel(self)
        panel.layout = fsui.VerticalLayout()
        panel.layout.add(
            OptionUI.create_group(
                panel, option, text, thin=False, help_button=True
            ),
            fill=True,
        )
        layout.add(panel, fill=True, margin_bottom=10)

    @staticmethod
    def option_list_for_platform(platform):
        options = []
        if platform in [Platform.AMIGA, Platform.CD32, Platform.CDTV]:
            options.append(Option.AMIGA_EMULATOR)
        elif platform == Platform.ARCADE:
            # options.append(Option.ARCADE_DATABASE)
            options.append(Option.ARCADE_EMULATOR)
            options.append(Option.MAME_ARTWORK)
            options.extend(mame_options)
        elif platform == Platform.C64:
            # options.append(Option.C64_DATABASE)
            options.append(Option.C64_PALETTE)
            options.append(Option.VICE_AUDIO_DRIVER)
        elif platform == Platform.CPC:
            # options.append(Option.CPC_DATABASE)
            options.append(Option.CPC_EMULATOR)
        elif platform == Platform.GBA:
            # options.append(Option.NES_DATABASE)
            # options.append(Option.GBA_EMULATOR)
            options.append(Option.GBA_GAMMA)
            options.extend(mednafen_options)
        elif platform == Platform.N64:
            # options.append(Option.N64_DATABASE)
            options.append(Option.N64_EMULATOR)
            # options.extend(mednafen_options)
            options.extend(retroarch_options)
        elif platform == Platform.NDS:
            # options.append(Option.NDS_DATABASE)
            options.append(Option.NDS_EMULATOR)
            options.append(Option.DESMUME_PATH)
            options.append(Option.MELONDS_PATH)
            options.extend(mame_options)
        elif platform == Platform.NEOGEO:
            # options.append(Option.NEOGEO_DATABASE)
            options.extend(mame_options)
        elif platform == Platform.NES:
            # options.append(Option.NES_DATABASE)
            options.append(Option.NES_EMULATOR)
            options.extend(mednafen_options)
            options.extend(retroarch_options)
        elif platform == Platform.PSX:
            # options.append(Option.PSX_DATABASE)
            options.append(Option.PSX_PRELOAD)
            options.extend(mednafen_options)
            options.append(Option.MEDNAFEN_DEINTERLACER)
            options.append(Option.MEDNAFEN_TEMPORAL_BLUR)
        elif platform == Platform.SMD:
            # options.append(Option.SMD_DATABASE)
            options.append(Option.SMD_EMULATOR)
            options.extend(mednafen_options)
            options.extend(retroarch_options)
        elif platform == Platform.SNES:
            # options.append(Option.SNES_DATABASE)
            options.append(Option.SNES_EMULATOR)
            options.extend(mednafen_options)
        elif platform == Platform.ST:
            # options.append(Option.ST_DATABASE)
            options.append(Option.ST_EMULATOR)
        elif platform == Platform.ZXS:
            # options.append(Option.ZXS_DATABASE)
            options.append(Option.ZXS_EMULATOR)
        return options


mame_options = []

mednafen_options = [Option.MEDNAFEN_AUDIO_DRIVER, Option.MEDNAFEN_AUDIO_BUFFER]

retroarch_options = [Option.RETROARCH_AUDIO_BUFFER]
