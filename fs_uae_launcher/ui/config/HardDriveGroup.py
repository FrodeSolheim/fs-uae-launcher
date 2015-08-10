import os
import traceback
from fsgs.ChecksumTool import ChecksumTool
import fsui as fsui
from fsgs.Archive import Archive
from ...Config import Config
from fsgs.FSGSDirectories import FSGSDirectories
from ...I18N import gettext
from ..IconButton import IconButton
from ..LauncherFilePicker import LauncherFilePicker


class HardDriveGroup(fsui.Group):

    def __init__(self, parent, index):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        self.index = index
        self.config_key = "hard_drive_{0}".format(index)
        self.config_key_sha1 = "x_hard_drive_{0}_sha1".format(index)

        if index == 0:
            # heading_label = fsui.HeadingLabel(self,
            #         _("Hard Drive {0}").format(index + 1))
            heading_label = fsui.HeadingLabel(self, gettext("Hard Drives"))
            self.layout.add(heading_label, margin_bottom=20)
            self.layout.add_spacer(0)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        self.eject_button = IconButton(self, "eject_button.png")
        self.eject_button.set_tooltip(gettext("Eject"))
        self.eject_button.activated.connect(self.on_eject_button)
        hori_layout.add(self.eject_button)

        self.text_field = fsui.TextField(self, "", read_only=True)
        hori_layout.add(self.text_field, expand=True, margin_left=10)

        self.browse_button = IconButton(self, "browse_folder_16.png")
        self.browse_button.set_tooltip(gettext("Browse for Folder"))
        self.browse_button.activated.connect(self.on_browse_folder_button)
        hori_layout.add(self.browse_button, margin_left=10)

        self.browse_button = IconButton(self, "browse_file_16.png")
        self.browse_button.set_tooltip(gettext("Browse for File"))
        self.browse_button.activated.connect(self.on_browse_file_button)
        hori_layout.add(self.browse_button, margin_left=10)

        self.initialize_from_config()
        self.set_config_handlers()

    def initialize_from_config(self):
        self.on_config(self.config_key, Config.get(self.config_key))

    def set_config_handlers(self):
        Config.add_listener(self)

    def on_destroy(self):
        Config.remove_listener(self)

    def on_config(self, key, value):
        if key != self.config_key:
            return
        dir, name = os.path.split(value)
        if dir:
            path = "{0} ({1})".format(name, dir)
        else:
            path = name
        self.text_field.set_text(path)

    def on_eject_button(self):
        Config.set_multiple([(self.config_key, ""),
                             (self.config_key_sha1, "")])

    def on_browse_folder_button(self):
        self.browse(dir_mode=True)

    def on_browse_file_button(self):
        self.browse(dir_mode=False)

    def browse(self, dir_mode):
        default_dir = FSGSDirectories.get_hard_drives_dir()
        dialog = LauncherFilePicker(
            self.get_window(), gettext("Choose Hard Drive"), "hd",
            Config.get(self.config_key), dir_mode=dir_mode)
        if not dialog.show_modal():
            dialog.destroy()
            return
        path = dialog.get_path()
        dialog.destroy()

        checksum_tool = ChecksumTool(self.get_window())
        sha1 = ""
        if dir_mode:
            print("not calculating HD checksums for directories")
        else:
            size = os.path.getsize(path)
            if size < 64 * 1024 * 1024:
                sha1 = checksum_tool.checksum(path)
            else:
                print("not calculating HD checksums HD files > 64MB")
        full_path = path

        # FIXME: use contract function
        dir, file = os.path.split(path)
        self.text_field.set_text(file)
        if os.path.normcase(os.path.normpath(dir)) == \
                os.path.normcase(os.path.normpath(default_dir)):
            path = file

        self.text_field.set_text(path)
        values = [(self.config_key, path),
                  (self.config_key_sha1, sha1)]
        if self.index == 0:
            # whdload_args = ""
            # dummy, ext = os.path.splitext(path)
            # if not dir_mode and ext.lower() in Archive.extensions:
            #     try:
            #         whdload_args = self.calculate_whdload_args(full_path)
            #     except Exception:
            #         traceback.print_exc()
            # values.append(("x_whdload_args", whdload_args))
            values.extend(self.generate_config_for_archive(
                full_path, model_config=False).items())
        Config.set_multiple(values)

    @classmethod
    def generate_config_for_archive(cls, path, model_config=True):
        values = {}
        whdload_args = ""
        dummy, ext = os.path.splitext(path)
        if ext.lower() in Archive.extensions:
            try:
                whdload_args = cls.calculate_whdload_args(path)
            except Exception:
                traceback.print_exc()
        values["x_whdload_args"] = whdload_args
        if whdload_args and model_config:
            values["amiga_model"] = "A600"
            values["fast_memory"] = "8192"
        return values

    @classmethod
    def calculate_whdload_args(cls, archive_path):
        archive = Archive(archive_path)
        slave = ""
        for path in archive.list_files():
            name = os.path.basename(path)
            name_lower = name.lower()
            if name_lower.endswith(".slave"):
                if slave:
                    print("already found one slave, don't know which "
                          "one to choose")
                    return ""
                slave = name
            elif name_lower == "startup-sequence":
                print("found startup-sequence, assuming non-whdload "
                      "archive")
        return slave
