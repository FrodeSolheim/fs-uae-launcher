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
    def __init__(self, parent, drives):
        FloppiesGroup.__init__(
            self, parent, drives, removable_media=True)
        self.layout3 = fsui.HorizontalLayout()
        self.layout.add(self.layout3, fill=True)
        self.layout3.add_spacer(0, expand=True)
        self.cd_mode = False
        self.__platform = ""
        self.__amiga_model = ""
        self._c64_model = ""
        self._zxs_model = ""
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
