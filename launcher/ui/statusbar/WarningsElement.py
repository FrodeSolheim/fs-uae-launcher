from operator import itemgetter

from fsgs.plugins.plugin_manager import PluginManager

from launcher.launcher_config import LauncherConfig
from launcher.device_manager import DeviceManager
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.ui.config.ConfigDialog import ConfigDialog
from launcher.ui.settings.settings_dialog import SettingsDialog
from launcher.update_manager import UpdateManager
from launcher.ui.setup import SetupDialog
from launcher.ui.behaviors.configbehavior import ConfigBehavior
from launcher.ui.behaviors.settingsbehavior import SettingsBehavior
from launcher.ui.download import DownloadGameWindow
from launcher.ui.statusbar.StatusElement import StatusElement
from fsgs.amiga.Amiga import Amiga
from fsgs.context import fsgs
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
        self.error_icon = Image("launcher:res/16/error.png")
        self.warning_icon = Image("launcher:res/16/warning_3.png")
        self.notice_icon = Image("launcher:res/16/information.png")
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
        self.kickstart_file = ""
        self.x_kickstart_file_sha1 = ""
        self.update_available = ""
        self.__error = ""
        self.x_missing_files = ""
        self.download_page = ""
        self.download_file = ""
        self.amiga_model = ""
        self.amiga_model_calculated = ""
        self.chip_memory = ""
        self.chip_memory_calculated = 0
        self.outdated_plugins = []
        self.custom_config = set()
        self.custom_uae_config = set()
        self.settings_config_keys = set()

        plugin_manager = PluginManager.instance()
        for plugin in plugin_manager.plugins():
            if plugin.outdated:
                self.outdated_plugins.append(plugin.name)

        ConfigBehavior(self, [
            "x_game_notice", "x_variant_notice", "x_variant_warning",
            "x_variant_error", "x_joy_emu_conflict", "amiga_model",
            "x_kickstart_file_sha1", "kickstart_file", "download_page",
            "download_file", "x_missing_files", "__error",
            "chip_memory", "jit_compiler"])
        SettingsBehavior(self, ["__update_available"])

        LauncherConfig.add_listener(self)
        for key in JOYSTICK_KEYS:
            self.on_config(key, LauncherConfig.get(key))
        for key in LauncherConfig.keys():
            if LauncherConfig.is_custom_uae_option(key):
                self.on_config(key, LauncherConfig.get(key))
            elif LauncherConfig.is_custom_option(key):
                self.on_config(key, LauncherConfig.get(key))

        LauncherSettings.add_listener(self)
        for key in LauncherSettings.keys():
            if LauncherConfig.is_config_only_option(key):
                self.on_setting(key, LauncherSettings.get(key))

    def on_destroy(self):
        LauncherConfig.remove_listener(self)
        LauncherSettings.remove_listener(self)

    def on_amiga_model_config(self, value):
        LauncherConfig.update_kickstart()
        if value != self.amiga_model:
            self.amiga_model = value
            self.amiga_model_calculated = value.split("/")[0]
            self.rebuild_warnings_and_refresh()

    def on_chip_memory_config(self, value):
        if value != self.chip_memory:
            self.chip_memory = value
            try:
                self.chip_memory_calculated = int(value or "0")
            except Exception:
                self.chip_memory_calculated = -1
            self.rebuild_warnings_and_refresh()

    def on___error_config(self, value):
        if value != self.__error:
            self.__error = value
            self.rebuild_warnings_and_refresh()

    def on_x_missing_files_config(self, value):
        if value != self.x_missing_files:
            self.x_missing_files = value
            self.rebuild_warnings_and_refresh()

    def on_download_page_config(self, value):
        if value != self.download_page:
            self.download_page = value
            self.rebuild_warnings_and_refresh()

    def on_download_file_config(self, value):
        if value != self.download_file:
            self.download_file = value
            self.rebuild_warnings_and_refresh()

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

    def on_jit_compiler_config(self, _):
        self.rebuild_warnings_and_refresh()

    def on_config(self, key, value):
        if key in JOYSTICK_KEYS:
            prev_value = self.using_joy_emu
            devices = DeviceManager.get_devices_for_ports(LauncherConfig)
            for device in devices:
                if device.id == "keyboard":
                    self.using_joy_emu = True
                    break
            else:
                self.using_joy_emu = False
            if prev_value != self.using_joy_emu:
                self.rebuild_warnings_and_refresh()
        elif key.startswith("__"):
            pass
        # elif LauncherConfig.is_implicit_option(key):
        #     pass
        elif LauncherConfig.is_custom_uae_option(key):
            changed = False
            if value:
                if key not in self.custom_uae_config:
                    self.custom_uae_config.add(key)
                    changed = True
            else:
                if key in self.custom_uae_config:
                    self.custom_uae_config.remove(key)
                    changed = True
            if changed:
                self.rebuild_warnings_and_refresh()
        elif LauncherConfig.is_custom_option(key):
            changed = False
            if value:
                if key not in self.custom_config:
                    self.custom_config.add(key)
                    changed = True
            else:
                if key in self.custom_config:
                    self.custom_config.remove(key)
                    changed = True
            if changed:
                self.rebuild_warnings_and_refresh()

    def on_setting(self, key, value):
        if LauncherConfig.is_config_only_option(key):
            changed = False
            if value:
                if key not in self.settings_config_keys:
                    self.settings_config_keys.add(key)
                    changed = True
            else:
                if key in self.settings_config_keys:
                    self.settings_config_keys.remove(key)
                    changed = True
            if changed:
                self.rebuild_warnings_and_refresh()

    def on___update_available_setting(self, value):
        if value != self.update_available:
            self.update_available = value
            self.rebuild_warnings_and_refresh()

    def paint_element(self, dc):
        self.coordinates.clear()
        dc.set_font(dc.get_font())
        x = 6
        w, h = self.size()
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

    def rebuild_warnings(self):
        self.warnings = []

        if self.using_joy_emu and self.joy_emu_conflict:
            self.warnings.append((WARNING_LEVEL, self.joy_emu_conflict, ""))

        self.add_option_warnings()
        self.add_game_warnings()

        if self.update_available:
            text = gettext("Update available: {version}").format(
                version=self.update_available)
            self.warnings.append((NOTICE_LEVEL, text, "on_update"))

        if self.outdated_plugins:
            text = gettext("Outdated plugins: {0}".format(
                ", ".join(self.outdated_plugins)))
            self.warnings.append((ERROR_LEVEL, text, "on_outdated_plugins"))

        if self.x_kickstart_file_sha1 == Amiga.INTERNAL_ROM_SHA1 and \
                self.kickstart_file != "internal":
            # text = gettext("Compatibility Issue")
            # self.warnings.append((ERROR_LEVEL, text, "on_kickstart_warning"))
            text = gettext("Using Kickstart ROM replacement")
            self.warnings.append((WARNING_LEVEL, text, "on_kickstart_warning"))
            text = gettext("Click to import Kickstart ROMs")
            self.warnings.append((NOTICE_LEVEL, text, "on_import_kickstarts"))

        if self.__error:
            self.warnings.append((ERROR_LEVEL, self.__error, ""))

        self.add_config_warnings()
        self.warnings.sort(key=itemgetter(0))

    def add_option_warnings(self):
        if len(self.settings_config_keys):
            if len(self.settings_config_keys) == 1:
                text = gettext("Config in Settings: {name}".format(
                    name=list(self.settings_config_keys)[0]))
            else:
                text = gettext("Config Options in Settings")
            self.warnings.append((ERROR_LEVEL, text, "on_advanced_settings"))
        if len(self.custom_uae_config):
            if len(self.custom_uae_config) == 1:
                text = gettext("Custom Option: {name}".format(
                    name=list(self.custom_uae_config)[0]))
            else:
                text = gettext("Custom uae_ Options")
            self.warnings.append((WARNING_LEVEL, text, "on_uae_config"))
        if len(self.custom_config):
            if len(self.custom_config) == 1:
                text = gettext("Custom Option: {name}".format(
                    name=list(self.custom_config)[0]))
            else:
                text = gettext("Custom Options")
            self.warnings.append((NOTICE_LEVEL, text, "on_uae_config"))

    def add_game_warnings(self):
        if is_warning(self.x_missing_files):
            if self.download_file:
                text = gettext("Auto-Download")
                self.warnings.append((NOTICE_LEVEL, text, ""))
            elif self.download_page:
                text = gettext("Download Game")
                self.warnings.append((WARNING_LEVEL, text, "on_download_page"))
            else:
                text = gettext("Missing Game Files")
                self.warnings.append((ERROR_LEVEL, text, ""))

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

    def add_config_warnings(self):
        # FIXME: move such warnings to config model code instead
        if self.chip_memory_calculated and \
                        self.chip_memory_calculated < 2048 and \
                        self.amiga_model_calculated in ["A1200", "A4000"]:
            text = gettext("{amiga_model} with < 2 MB chip memory").format(
                amiga_model=self.amiga_model)
            self.warnings.append((WARNING_LEVEL, text, ""))
        if LauncherConfig.get("amiga_model") == "A4000/OS4":
            if LauncherConfig.get("jit_compiler") == "1":
                text = gettext(
                    "JIT compiler with a PPC-only OS is not recommended")
                self.warnings.append((WARNING_LEVEL, text, ""))

    def rebuild_warnings_and_refresh(self):
        self.rebuild_warnings()
        self.refresh()

    def on_left_down(self):
        from fsui.qt import QCursor
        # noinspection PyArgumentList
        # FIXME: Remove direct Qt dependency
        p = self._widget.mapFromGlobal(QCursor.pos())
        for start, stop, handler in self.coordinates:
            if start <= p.x() < stop and handler:
                # print(start, stop, handler)
                getattr(self, handler)()

    def on_update(self):
        UpdateManager.start_update(self.update_available)

    def on_outdated_plugins(self):
        dialog = SettingsDialog.open(self.get_window())
        # FIXME: Move code to settings dialog, so we can open the page with
        # a method/constant or method instead of a name.
        dialog.set_page_by_title(gettext("Plugins"))

    # noinspection PyMethodMayBeStatic
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

    def on_download_page(self):
        DownloadGameWindow(self.get_window(), fsgs).show()

    def on_uae_config(self):
        print("Custom config keys:", self.custom_config)
        print("Custom uae config keys:", self.custom_uae_config)
        ConfigDialog.run(self.get_window())

    def on_advanced_settings(self):
        dialog = SettingsDialog.open(self.get_window())
        # FIXME: Move code to settings dialog, so we can open the page with
        # a method/constant or method instead of a name.
        print("Config keys in settings:", self.settings_config_keys)
        dialog.set_page_by_title(gettext("Advanced Settings"))


def is_warning(w):
    if w is None:
        return False
    if isinstance(w, str):
        return bool(w)
    if isinstance(w, bool):
        return w
    return w[0] or w[1]
