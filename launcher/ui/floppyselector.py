import os

import fsui
from fsbc.paths import Paths
from fsgamesys.context import fsgs
from fsgamesys.options.option import Option
from fsgamesys.platforms import PLATFORM_ATARI
from launcher.context import get_config
from launcher.helpers.cdmanager import CDManager
from launcher.helpers.floppymanager import FloppyManager
from launcher.i18n import gettext
from launcher.ui.behaviors.platformbehavior import AMIGA_PLATFORMS
from launcher.ui.IconButton import IconButton
from launcher.ui.LauncherFilePicker import LauncherFilePicker


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

        self.text_field = fsui.TextField(self, "", read_only=True)

        self.browse_button = IconButton(self, "browse_folder_16.png")
        self.browse_button.set_tooltip(gettext("Browse for file"))
        self.browse_button.activated.connect(self.on_browse)

        self.eject_button = IconButton(self, "eject_button.png")
        # AmigaEnableBehavior(self.eject_button)
        self.eject_button.set_tooltip(gettext("Eject"))
        self.eject_button.activated.connect(self.on_eject)

        self.layout = fsui.HorizontalLayout()
        self.layout.add(self.text_field, expand=True)
        self.layout.add_spacer(5)
        self.layout.add(self.eject_button, fill=True)
        self.layout.add_spacer(5)
        self.layout.add(self.browse_button, fill=True)

        # Config.add_listener(self)
        #  fsgs.signal.connect(self.on_config,
        #          "fsgs:config:floppy_drive_{0}".format(self.drive),
        #          "fsgs:config:cdrom_drive_{0}".format(self.drive))

        # fsgs.signal.connect("config", self.on_config)
        get_config(self).attach(self.__on_config)
        self.on_config(Option.PLATFORM, fsgs.config.get(Option.PLATFORM))
        self.update_config_key()

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
            self.window,
            title,
            media_type,
            get_config(self).get(self.config_key),
        )

        if not dialog.show_modal():
            return
        path = dialog.get_path()

        if self.mode == self.CD_MODE:
            fsgs.amiga.insert_cd(self.drive, path)
        elif self.mode == self.FLOPPY_MODE:
            fsgs.amiga.insert_floppy(self.drive, path)
        else:
            fsgs.config.set(self.config_key, Paths.contract_path(path))

    def __on_config(self, event):
        self.on_config(event.key, event.value)

    def on_config(self, key, value):
        if key == self.config_key:
            self.text_field.set_text(value)
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
            self.eject_button.set_enabled(bool(value))
        elif key == self.config_key_implicit:
            self.config_value_implicit = value
            self.update_enable()
        elif key == Option.PLATFORM:
            self.__platform = value
            self.update_enable()

    def onDestroy(self):
        # fsgs.signal.disconnect(
        #     "fsgs:config:floppy_drive_{0}".format(self.drive),
        #     self.on_config_floppy_drive)
        # fsgs.signal.disconnect("config", self.on_config)
        get_config(self).detach(self.__on_config)
        super().onDestroy()

    def on_eject(self):
        config = get_config(self)
        if self.mode == self.CD_MODE:
            CDManager.eject(self.drive, config=config)
        elif self.mode == self.FLOPPY_MODE:
            FloppyManager.eject(self.drive, config=config)
        else:
            fsgs.config.set(self.config_key, "")

    def set_mode(self, mode):
        self.mode = mode
        self.update_config_key()

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
                    self.drive
                )
            self.config_key_implicit = "__implicit_cartridge_drive_count"
        else:
            self.config_key = "floppy_drive_{}".format(self.drive)
            self.config_key_sha1 = "x_floppy_drive_{}_sha1".format(self.drive)
            self.config_key_implicit = "__implicit_uae_floppy{}type".format(
                self.drive
            )
        config = get_config(self)
        self.on_config(self.config_key, config.get(self.config_key))
        self.on_config(
            self.config_key_implicit,
            config.get(self.config_key_implicit),
        )

    def update_enable(self):
        if self.__platform in AMIGA_PLATFORMS:
            if self.mode == self.CD_MODE:
                self.text_field.set_enabled(self.config_value_implicit != "0")
            elif self.mode == self.CARTRIDGE_MODE:
                pass
            else:
                self.text_field.set_enabled(self.config_value_implicit != "-1")
        else:
            if (
                self.__platform == PLATFORM_ATARI
                and self.mode == self.FLOPPY_MODE
            ):
                self.text_field.set_enabled(self.drive < 2)
            else:
                self.text_field.set_enabled(self.drive == 0)
