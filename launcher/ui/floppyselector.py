import os

import fsui
from fsbc.paths import Paths
from fsgs.context import fsgs
from fsgs.option import Option
from fsgs.platforms import PLATFORM_ATARI
from launcher.cd_manager import CDManager
from launcher.floppy_manager import FloppyManager
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.ui.IconButton import IconButton
from launcher.ui.LauncherFilePicker import LauncherFilePicker
from launcher.ui.behaviors.platformbehavior import AMIGA_PLATFORMS


class FloppySelector(fsui.Panel):
    FLOPPY_MODE = 0
    CD_MODE = 1
    TAPE_MODE = 2
    CARTRIDGE_MODE = 3

    def __init__(self, parent, drive, show_path=True):
        fsui.Panel.__init__(self, parent)
        self.mode = FloppySelector.FLOPPY_MODE
        self.show_path = show_path
        self.drive = drive
        self.config_key = ""
        self.config_key_sha1 = ""
        self.config_key_implicit = ""
        self.config_value_implicit = ""
        self.__platform = ""

        self.eject_button = IconButton(self, "eject_button.png")
        # AmigaEnableBehavior(self.eject_button)
        self.eject_button.set_tooltip(gettext("Eject"))
        self.eject_button.activated.connect(self.on_eject)

        self.text_field = fsui.TextField(self, "", read_only=True)

        self.browse_button = IconButton(self, "browse_file_16.png")
        self.browse_button.set_tooltip(gettext("Browse for File"))
        self.browse_button.activated.connect(self.on_browse)
        # AmigaEnableBehavior(self.browse_button)

        self.layout = fsui.HorizontalLayout()
        self.layout.add(self.eject_button)
        self.layout.add_spacer(10)
        self.layout.add(self.text_field, expand=True)
        self.layout.add_spacer(10)
        self.layout.add(self.browse_button)

        # Config.add_listener(self)
        #  fsgs.signal.connect(self.on_config,
        #          "fsgs:config:floppy_drive_{0}".format(self.drive),
        #          "fsgs:config:cdrom_drive_{0}".format(self.drive))
        fsgs.signal.connect("config", self.on_config)
        self.on_config(Option.PLATFORM, fsgs.config.get(Option.PLATFORM))
        self.update_config_key()

    def on_destroy(self):
        # fsgs.signal.disconnect(
        #     "fsgs:config:floppy_drive_{0}".format(self.drive),
        #     self.on_config_floppy_drive)
        fsgs.signal.disconnect("config", self.on_config)

    # def enable(self, enable=True):
    #     self.text_field.enable(enable)
    #     self.browse_button.enable(enable)
    #     self.eject_button.enable(enable)

    def on_config(self, key, value):
        if key == self.config_key:
            dir_path, name = os.path.split(value)
            if dir_path:
                if self.show_path:
                    path = "{0} ({1})".format(name, dir_path)
                else:
                    path = name
            else:
                path = name
            self.text_field.set_text(path)
            self.text_field.set_cursor_position(0)
            self.eject_button.enable(bool(value))
        elif key == self.config_key_implicit:
            self.config_value_implicit = value
            self.update_enable()
        elif key == Option.PLATFORM:
            self.__platform = value
            self.update_enable()

    def update_enable(self):
        if self.__platform in AMIGA_PLATFORMS:
            if self.mode == self.CD_MODE:
                self.text_field.enable(self.config_value_implicit != "0")
            elif self.mode == self.CARTRIDGE_MODE:
                pass
            else:
                self.text_field.enable(self.config_value_implicit != "-1")
        else:
            if self.__platform == PLATFORM_ATARI and \
                            self.mode == self.FLOPPY_MODE:
                self.text_field.enable(self.drive < 2)
            else:
                self.text_field.enable(self.drive == 0)

    def update_config_key(self):
        if self.mode == self.CD_MODE:
            self.config_key = "cdrom_drive_{}".format(self.drive)
            self.config_key_sha1 = "x_cdrom_drive_{}_sha1".format(self.drive)
            self.config_key_implicit = "__implicit_cdrom_drive_count"
        elif self.mode == self.TAPE_MODE:
            self.config_key = "tape_drive_{}".format(self.drive)
            self.config_key_sha1 = "x_tape_drive_{}_sha1".format(self.drive)
            self.config_key_implicit = "__implicit_tape_drive_count"
        elif self.mode == self.CARTRIDGE_MODE:
            if self.drive == 0:
                self.config_key = Option.CARTRIDGE_SLOT
                self.config_key_sha1 = "x_cartridge_slot_sha1"
            else:
                self.config_key = "cartridge_drive_{}".format(self.drive)
                self.config_key_sha1 = "x_cartridge_drive_{}_sha1".format(
                    self.drive)
            self.config_key_implicit = "__implicit_cartridge_drive_count"
        else:
            self.config_key = "floppy_drive_{}".format(self.drive)
            self.config_key_sha1 = "x_floppy_drive_{}_sha1".format(self.drive)
            self.config_key_implicit = \
                "__implicit_uae_floppy{}type".format(self.drive)
        self.on_config(self.config_key, LauncherConfig.get(self.config_key))
        self.on_config(self.config_key_implicit,
                       LauncherConfig.get(self.config_key_implicit))

    def set_mode(self, mode):
        self.mode = mode
        self.update_config_key()

    def on_eject(self):
        if self.mode == self.CD_MODE:
            CDManager.eject(self.drive)
        elif self.mode == self.FLOPPY_MODE:
            FloppyManager.eject(self.drive)
        else:
            fsgs.config.set(self.config_key, "")

    def on_browse(self):
        if self.mode == self.CD_MODE:
            title = gettext("Choose CD-ROM Image")
            # default_dir = FSGSDirectories.get_cdroms_dir()
            media_type = "cd"
        elif self.mode == self.TAPE_MODE:
            title = gettext("Choose Tape Image")
            media_type = "tape"
        elif self.mode == self.CARTRIDGE_MODE:
            title = gettext("Choose Cartridge Image")
            media_type = "cartridge"
        else:
            title = gettext("Choose Floppy Image")
            # default_dir = FSGSDirectories.get_floppies_dir()
            media_type = "floppy"
        dialog = LauncherFilePicker(
            self.window, title, media_type, LauncherConfig.get(self.config_key))

        if not dialog.show_modal():
            return
        path = dialog.get_path()

        if self.mode == self.CD_MODE:
            fsgs.amiga.insert_cd(self.drive, path)
        elif self.mode == self.FLOPPY_MODE:
            fsgs.amiga.insert_floppy(self.drive, path)
        else:
            fsgs.config.set(self.config_key, Paths.contract_path(path))
