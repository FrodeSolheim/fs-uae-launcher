from fs_uae_launcher.Config import Config
from fs_uae_launcher.DeviceManager import DeviceManager
from fs_uae_launcher.I18N import gettext
from fs_uae_launcher.UpdateManager import UpdateManager
from fs_uae_launcher.ui.SetupDialog import SetupDialog
from fs_uae_launcher.ui.behaviors.configbehavior import ConfigBehavior
from fs_uae_launcher.ui.behaviors.settingsbehavior import SettingsBehavior
from fs_uae_launcher.ui.statusbar.StatusElement import StatusElement
from fsgs.amiga.Amiga import Amiga
from fsui import Image
import fsui

ERROR_LEVEL = 0
WARNING_LEVEL = 1
NOTICE_LEVEL = 2
JOYSTICK_KEYS = ["joystick_port_0", "joystick_port_1", "joystick_port_2",
                 "joystick_port_3", "joystick_port_0_mode",
                 "joystick_port_1_mode", "joystick_port_2_mode",
                 "joystick_port_3_mode"]


class WarningsElement(StatusElement):

    def __init__(self, parent):
        StatusElement.__init__(self, parent)
        self.error_icon = Image("fs_uae_launcher:res/16/error.png")
        self.warning_icon = Image("fs_uae_launcher:res/16/warning_2.png")
        self.notice_icon = Image("fs_uae_launcher:res/16/information.png")
        self.icons = [
            self.error_icon,
            self.warning_icon,
            self.notice_icon,
        ]
        self.coordinates = []
        self.warnings = []

        self.game_notice = ""
        self.variant_notice = ""
        self.variant_warning = ""
        self.variant_error = ""
        self.joy_emu_conflict = ""
        self.using_joy_emu = False
        self.update_available = ""
        self.kickstart_file = ""
        self.x_kickstart_file_sha1 = ""

        ConfigBehavior(self, ["x_game_notice", "x_variant_notice",
                              "x_variant_warning", "x_variant_error",
                              "x_joy_emu_conflict", "amiga_model",
                              "x_kickstart_file_sha1", "kickstart_file"])
        SettingsBehavior(self, ["__update_available"])

        self.on_config("joystick_port_0", Config.get("joystick_port_0"))
        Config.add_listener(self)

    def on_destroy(self):
        Config.remove_listener(self)

    def rebuild_warnings(self):
        self.warnings = []
        if self.using_joy_emu and self.joy_emu_conflict:
            self.warnings.append((WARNING_LEVEL, self.joy_emu_conflict, ""))
        for name in ["variant_notice", "game_notice"]:
            value = getattr(self, name)
            if not value:
                continue
            if value.startswith("WARNING: "):
                level = WARNING_LEVEL
                message = value[9:]
            else:
                level = NOTICE_LEVEL
                message = value
            self.warnings.append((level, message, ""))
        if self.variant_warning:
            self.warnings.append((WARNING_LEVEL, self.variant_warning, ""))
        if self.variant_error:
            self.warnings.append((ERROR_LEVEL, self.variant_error, ""))
        if self.update_available:
            text = gettext("Update Available: {version}").format(
                version=self.update_available)
            self.warnings.append((NOTICE_LEVEL, text, "on_update"))
        if self.x_kickstart_file_sha1 == Amiga.INTERNAL_ROM_SHA1 and \
                self.kickstart_file != "internal":
            text = gettext("Compatibility Issue")
            self.warnings.append((ERROR_LEVEL, text, "on_kickstart_warning"))
            text = gettext("Using Kickstart ROM Replacement")
            self.warnings.append((WARNING_LEVEL, text, "on_kickstart_warning"))
            text = gettext("Click to Import Kickstart ROMs")
            self.warnings.append((NOTICE_LEVEL, text, "on_import_kickstarts"))
        self.warnings.sort()

    def rebuild_warnings_and_refresh(self):
        self.rebuild_warnings()
        self.refresh()

    def on_amiga_model_config(self, value):
        Config.update_kickstart()

    def on_kickstart_file_config(self, value):
        if value != self.kickstart_file:
            self.kickstart_file = value
            self.rebuild_warnings_and_refresh()

    def on_x_kickstart_file_sha1_config(self, value):
        if value != self.x_kickstart_file_sha1:
            self.x_kickstart_file_sha1 = value
            self.rebuild_warnings_and_refresh()

    def on_x_game_notice_config(self, value):
        if value != self.game_notice:
            self.game_notice = value
            self.rebuild_warnings_and_refresh()

    def on_x_variant_notice_config(self, value):
        if value != self.variant_notice:
            self.variant_notice = value
            self.rebuild_warnings_and_refresh()

    def on_x_variant_warning_config(self, value):
        if value != self.variant_warning:
            self.variant_warning = value
            self.rebuild_warnings_and_refresh()

    def on_x_variant_error_config(self, value):
        if value != self.variant_error:
            self.variant_error = value
            self.rebuild_warnings_and_refresh()

    def on_x_joy_emu_conflict_config(self, value):
        print("\n\n\nGOT x_joy_emu_conflict\n\n\n")
        if value != self.joy_emu_conflict:
            self.joy_emu_conflict = value
            self.rebuild_warnings_and_refresh()

    def on_config(self, key, value):
        if key in JOYSTICK_KEYS:
            prev_value = self.using_joy_emu
            devices = DeviceManager.get_devices_for_ports(Config)
            for device in devices:
                if device.id == "keyboard":
                    self.using_joy_emu = True
                    break
            else:
                self.using_joy_emu = False
            if prev_value != self.using_joy_emu:
                self.rebuild_warnings_and_refresh()

    def on___update_available_setting(self, value):
        if value != self.update_available:
            self.update_available = value
            self.rebuild_warnings_and_refresh()

    def paint_element(self, dc):
        self.coordinates.clear()
        dc.set_font(dc.get_font())
        x = 6
        w, h = self.size
        for level, warning, handler in self.warnings:
            icon = self.icons[level]
            start = x
            dc.draw_image(icon, x, 6)
            x += 16 + 6
            tw, th = dc.measure_text(warning)
            dc.draw_text(warning, x, (h - th) / 2)
            x += tw + 6 + 16
            stop = x
            self.coordinates.append((start, stop, handler))

    def on_left_down(self):
        from fsui.qt import QCursor
        p = self.mapFromGlobal(QCursor.pos())
        for start, stop, handler in self.coordinates:
            if start <= p.x() < stop:
                print(start, stop, handler)
                getattr(self, handler)()

    def on_update(self):
        UpdateManager.start_update(self.update_available)

    def on_kickstart_warning(self):
        text = ("The Kickstart ROM for the chosen Amiga model was not found "
                "on your system.\n\n"
                "A replacement Kickstart ROM from the AROS project is used "
                "instead. Compatibility will be lower than if you use an "
                "original Kickstart ROM.\n\n"
                "You can use the file database scan function or the import "
                "wizards if you own the Kickstart ROM.\n\n"
                "Original Kickstart ROMs can be purchased online as part "
                "of Cloanto's Amiga Forever package, or you can extract "
                "a Kickstart from a real Amiga.\n\n"
                "If you want to use the replacement Kickstart, you can "
                "ignore this warning, or explicitly change the Kickstart "
                "to \"Internal\" to dismiss this warning.")
        fsui.show_warning(text, gettext("Using Kickstart ROM Replacement"))

    def on_import_kickstarts(self):
        SetupDialog(self.get_window()).show()
