import fsui
from fsgamesys.amiga.amiga import Amiga
from fsgamesys.options.option import Option
from fsgamesys.platforms.platform import Platform
from fsgamesys.platforms.commodore64 import C64_MODEL_C64C_1541_II
from fsgamesys.platforms.cpc.cpcconstants import CPC_MODEL_464
from fsgamesys.platforms.spectrum import SPECTRUM_MODEL_PLUS3
from launcher.context import get_config
from launcher.i18n import gettext
from launcher.ui.behaviors.configbehavior import ConfigBehavior
from launcher.ui.behaviors.platformbehavior import AMIGA_PLATFORMS
from launcher.ui.floppiesgroup import FloppiesGroup


class RemovableMediaGroup(FloppiesGroup):
    def __init__(self, parent, drives, main=False):
        super().__init__(parent, drives, removable_media=True)
        self.layout3 = fsui.HorizontalLayout()
        self.layout.add(self.layout3, fill=True)
        self.layout3.add_spacer(0, expand=True)
        self.cd_mode = False
        self.__platform = ""
        self.__amiga_model = ""
        self._main = main
        self._c64_model = ""
        self._cpc_model = ""
        self._spectrum_model = ""

        self._ines_header_widget = INesHeaderWidget(self)
        self._ines_header_widget.hide()
        self.layout.add(self._ines_header_widget, fill=True)
        self._a78_header_widget = A78HeaderWidget(self)
        self._a78_header_widget.hide()
        self.layout.add(self._a78_header_widget, fill=True)
        self._command_widget = CommandWidget(self)
        self._command_widget.hide()
        self.layout.add(self._command_widget, fill=True)

        self.update_media_type()

        ConfigBehavior(
            self,
            [
                Option.PLATFORM,
                Option.AMIGA_MODEL,
                Option.C64_MODEL,
                Option.CPC_MODEL,
                Option.SPECTRUM_MODEL,
            ],
        )

    def on_platform_config(self, value):
        self.__platform = value
        self.update_media_type()

    def on_amiga_model_config(self, value):
        self.__amiga_model = value
        self.update_media_type()

    def on_c64_model_config(self, value):
        self._c64_model = value
        self.update_media_type()

    def on_cpc_model_config(self, value):
        self._cpc_model = value
        self.update_media_type()

    def on_spectrum_model_config(self, value):
        self._spectrum_model = value
        self.update_media_type()

    def update_media_type(self):
        if self.__platform in AMIGA_PLATFORMS:
            self.set_cd_mode(Amiga.is_cd_based(get_config(self)))
        elif self.__platform in [Platform.C64]:
            if self._c64_model == C64_MODEL_C64C_1541_II:
                self.set_mode(self.FLOPPY_MODE)
            else:
                self.set_mode(self.TAPE_MODE)
        elif self.__platform in [Platform.CPC]:
            if self._cpc_model == CPC_MODEL_464:
                self.set_mode(self.TAPE_MODE)
            else:
                self.set_mode(self.FLOPPY_MODE)
        elif self.__platform in [Platform.DOS]:
            self.set_mode(self.FLOPPY_MODE)
        elif self.__platform in [Platform.PSX]:
            self.set_mode(self.CD_MODE)
        elif self.__platform in [Platform.ST]:
            self.set_mode(self.FLOPPY_MODE)
        elif self.__platform in [Platform.SPECTRUM]:
            if self._spectrum_model == SPECTRUM_MODEL_PLUS3:
                self.set_mode(self.FLOPPY_MODE)
            else:
                self.set_mode(self.TAPE_MODE)
        else:
            self.set_mode(self.CARTRIDGE_MODE)

        if self._main:
            if self.__platform == Platform.A7800:
                self.selectors[1].hide()
                self._a78_header_widget.show()
                self._command_widget.hide()
                self._ines_header_widget.hide()
            elif self.__platform in [
                Platform.CPC,
                Platform.DOS,
                Platform.SPECTRUM,
            ]:
                self.selectors[1].hide()
                self._a78_header_widget.hide()
                self._command_widget.show()
                self._ines_header_widget.hide()
            elif self.__platform == Platform.NES:
                # if self.selectors[1].is_visible():
                self.selectors[1].hide()
                self._a78_header_widget.hide()
                self._command_widget.hide()
                self._ines_header_widget.show()
            else:
                # if not self.selectors[1].is_visible():
                self.selectors[1].show()
                self._command_widget.hide()
                self._a78_header_widget.hide()
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
        # self.selectors[1].set_enabled(not self.cd_mode)

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
        self.layout.add(hori_layout, fill=True, margin=10, margin_bottom=0)

        self.text_field = fsui.TextField(self, "")
        self.text_field.on_changed = self.on_text_changed
        self.text_field.set_enabled(False)
        hori_layout.add(self.text_field, expand=True)

        # self.help_button = HelpButton(
        #     self, "https://fs-uae.net/docs/options/nes-ines-header")
        # hori_layout.add(self.help_button, margin_left=10)

        ConfigBehavior(self, [Option.NES_INES_HEADER])

    def on_nes_ines_header_config(self, value):
        if value != self.text_field.text():
            value = "iNES Header: " + value
            self.text_field.set_text(value)

    def on_text_changed(self):
        # LauncherConfig.set("nes_ines_header", self.text_field.text())
        pass


class A78HeaderWidget(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True, margin=10, margin_bottom=0)

        self.text_field = fsui.TextField(self, "")
        self.text_field.on_changed = self.on_text_changed
        self.text_field.set_enabled(False)
        hori_layout.add(self.text_field, expand=True)

        # self.help_button = HelpButton(
        #     self, "https://fs-uae.net/docs/options/nes-ines-header")
        # hori_layout.add(self.help_button, margin_left=10)

        ConfigBehavior(self, [Option.A7800_A78_HEADER])

    def on_a7800_a78_header_config(self, value):
        if value != self.text_field.text():
            value = "A78 Header: " + value
            self.text_field.set_text(value)

    def on_text_changed(self):
        # LauncherConfig.set("nes_ines_header", self.text_field.text())
        pass


class CommandWidget(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True, margin=10, margin_bottom=0)

        label = fsui.Label(self, gettext("Command:"))
        hori_layout.add(label, fill=True, margin_right=10)

        self.text_field = fsui.TextField(self, "")
        self.text_field.on_changed = self.on_text_changed
        # self.text_field.set_enabled(False)
        hori_layout.add(self.text_field, expand=True)

        # self.help_button = HelpButton(
        #     self, "https://fs-uae.net/docs/options/nes-ines-header")
        # hori_layout.add(self.help_button, margin_left=10)

        ConfigBehavior(self, [Option.COMMAND])

    def on_command_config(self, value):
        if value != self.text_field.text():
            self.text_field.set_text(value)

    def on_text_changed(self):
        get_config(self).set("command", self.text_field.text())
