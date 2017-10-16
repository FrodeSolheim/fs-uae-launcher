import fsui
from fsgs.amiga.amiga import Amiga
from fsgs.option import Option
from fsgs.platform import Platform
from fsgs.platforms.c64 import C64_MODEL_C64C_1541_II
from fsgs.platforms.zxs.spectrumplatform import ZXS_MODEL_PLUS3
from launcher.launcher_config import LauncherConfig
from launcher.ui.behaviors.configbehavior import ConfigBehavior
from launcher.ui.behaviors.platformbehavior import AMIGA_PLATFORMS
from launcher.ui.floppiesgroup import FloppiesGroup


class RemovableMediaGroup(FloppiesGroup):
    def __init__(self, parent, drives, main=False):
        FloppiesGroup.__init__(
            self, parent, drives, removable_media=True)
        self.layout3 = fsui.HorizontalLayout()
        self.layout.add(self.layout3, fill=True)
        self.layout3.add_spacer(0, expand=True)
        self.cd_mode = False
        self.__platform = ""
        self.__amiga_model = ""
        self._main = main
        self._c64_model = ""
        self._zxs_model = ""

        self._ines_header_widget = INesHeaderWidget(self)
        self._ines_header_widget.hide()
        self.layout.add(self._ines_header_widget, fill=True)

        self.update_media_type()

        ConfigBehavior(
            self, [Option.PLATFORM, Option.AMIGA_MODEL,
                   Option.C64_MODEL, Option.ZXS_MODEL])

    def on_platform_config(self, value):
        self.__platform = value
        self.update_media_type()

    def on_amiga_model_config(self, value):
        self.__amiga_model = value
        self.update_media_type()

    def on_c64_model_config(self, value):
        self._c64_model = value
        self.update_media_type()

    def on_zxs_model_config(self, value):
        self._zxs_model = value
        self.update_media_type()

    def update_media_type(self):
        if self.__platform in AMIGA_PLATFORMS:
            self.set_cd_mode(Amiga.is_cd_based(LauncherConfig))
        elif self.__platform in [Platform.ATARI]:
            self.set_mode(self.FLOPPY_MODE)
        elif self.__platform in [Platform.C64]:
            if self._c64_model == C64_MODEL_C64C_1541_II:
                self.set_mode(self.FLOPPY_MODE)
            else:
                self.set_mode(self.TAPE_MODE)
        elif self.__platform in [Platform.CPC]:
            self.set_mode(self.TAPE_MODE)
        elif self.__platform in [Platform.DOS]:
            self.set_mode(self.FLOPPY_MODE)
        elif self.__platform in [Platform.PSX]:
            self.set_mode(self.CD_MODE)
        elif self.__platform in [Platform.ZXS]:
            if self._zxs_model == ZXS_MODEL_PLUS3:
                self.set_mode(self.FLOPPY_MODE)
            else:
                self.set_mode(self.TAPE_MODE)
        else:
            self.set_mode(self.CARTRIDGE_MODE)

        if self._main:
            if self.__platform == Platform.NES:
                # if self.selectors[1].is_visible():
                self.selectors[1].hide()
                self._ines_header_widget.show()
            else:
                # if not self.selectors[1].is_visible():
                self.selectors[1].show()
                self._ines_header_widget.hide()
            self.layout.update()

    def set_mode(self, mode):
        if self.mode == mode:
            return
        self.mode = mode
        self.cd_mode = mode == self.CD_MODE
        for selector in self.selectors:
            # selector.set_cd_mode(self.cd_mode)
            selector.set_mode(self.mode)
        self.update_heading_label()
        # self.selectors[1].enable(not self.cd_mode)

    def set_cd_mode(self, cd_mode):
        if cd_mode:
            self.set_mode(self.CD_MODE)
        else:
            self.set_mode(self.FLOPPY_MODE)


class INesHeaderWidget(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True, margin=10)

        self.text_field = fsui.TextField(self, "")
        self.text_field.on_changed = self.on_text_changed
        self.text_field.disable()
        hori_layout.add(self.text_field, expand=True)

        # self.help_button = HelpButton(
        #     self, "https://fs-uae.net/docs/options/nes-ines-header")
        # hori_layout.add(self.help_button, margin_left=10)

        ConfigBehavior(self, [Option.NES_INES_HEADER])

    def on_nes_ines_header_config(self, value):
        if value != self.text_field.get_text():
            value = "iNES Header: " + value
            self.text_field.set_text(value)

    def on_text_changed(self):
        # LauncherConfig.set("nes_ines_header", self.text_field.get_text())
        pass
