import os

import fsui
from fsbc.paths import Paths
from fsgamesys.amiga.amiga import Amiga
from fsgamesys.checksumtool import ChecksumTool
from fsgamesys.context import fsgs
from fsgamesys.FSGSDirectories import FSGSDirectories
from launcher.context import get_config
from launcher.helpers.cdmanager import CDManager
from launcher.helpers.floppymanager import FloppyManager
from launcher.i18n import gettext

# from launcher.launcher_config import LauncherConfig
from launcher.option import Option
from launcher.ui.behaviors.configbehavior import ConfigBehavior
from launcher.ui.behaviors.platformbehavior import (
    AMIGA_PLATFORMS,
    PlatformEnableBehavior,
)
from launcher.ui.IconButton import IconButton
from launcher.ui.LauncherFilePicker import LauncherFilePicker


# FIXME: Superclass was Group, but changed to Panel due to not being able
# to disconnect from listening to config changes when closing window.
class MediaListGroup(fsui.Panel):
    def __init__(self, parent, cd_mode):
        super().__init__(parent)
        self.layout = fsui.VerticalLayout()

        self.cd_mode = cd_mode
        if self.cd_mode:
            self.file_key_prefix = "cdrom_image_"
            self.file_key = "cdrom_image_{0}"
            self.sha1_key = "x_cdrom_image_{0}_sha1"
            platforms = AMIGA_PLATFORMS
        else:
            self.file_key_prefix = "floppy_image_"
            self.file_key = "floppy_image_{0}"
            self.sha1_key = "x_floppy_image_{0}_sha1"
            platforms = AMIGA_PLATFORMS

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, expand=False, fill=True)
        self.heading_label = fsui.HeadingLabel(
            self, gettext("Media Swap List")
        )
        hori_layout.add(
            self.heading_label, margin=10, margin_top=20, margin_bottom=20
        )
        hori_layout.add_spacer(0, expand=True)

        if not self.cd_mode:
            save_disk_check_box = SaveDiskCheckBox(self)
            hori_layout.add(save_disk_check_box, margin_right=20)
            PlatformEnableBehavior(save_disk_check_box, platforms=platforms)

        clear_button = IconButton(self, "clear_button.png")
        clear_button.set_tooltip(gettext("Clear List"))
        clear_button.activated.connect(self.on_clear_list)
        PlatformEnableBehavior(clear_button, platforms=platforms)
        hori_layout.add(clear_button, margin_right=10)
        remove_button = IconButton(self, "remove_button.png")
        remove_button.set_tooltip(gettext("Remove Selected Files"))
        remove_button.activated.connect(self.on_remove_button)
        PlatformEnableBehavior(remove_button, platforms=platforms)
        hori_layout.add(remove_button, margin_right=10)
        add_button = IconButton(self, "add_button.png")
        add_button.set_tooltip(gettext("Add Files to List"))
        add_button.activated.connect(self.on_add_button)
        PlatformEnableBehavior(add_button, platforms=platforms)
        hori_layout.add(add_button, margin_right=10)

        # hori_layout = fsui.HorizontalLayout()
        # self.layout.add(hori_layout, expand=True, fill=True)
        self.list_view = fsui.ListView(self)
        PlatformEnableBehavior(self.list_view, platforms=platforms)
        self.list_view.on_activate_item = self.on_activate_item
        if self.cd_mode:
            self.default_icon = fsui.Image("launcher:/data/cdrom_16.png")
        else:
            self.default_icon = fsui.Image("launcher:/data/floppy_16.png")
        # hori_layout.add(self.list_view, expand=True, fill=True, margin=10)
        self.layout.add(
            self.list_view, expand=True, fill=True, margin=10, margin_top=0
        )

        # vert_layout = fsui.VerticalLayout()
        # hori_layout.add(vert_layout, fill=True)

        # add_button = IconButton(self, "add_button.png")
        # add_button.set_tooltip(gettext("Add Files to List"))
        # add_button.activated.connect(self.on_add_button)
        # vert_layout.add(add_button, margin=10)
        #
        # remove_button = IconButton(self, "remove_button.png")
        # remove_button.set_tooltip(gettext("Remove Selected Files"))
        # remove_button.activated.connect(self.on_remove_button)
        # vert_layout.add(remove_button, margin=10)
        #
        # clear_button = IconButton(self, "clear_button.png")
        # clear_button.set_tooltip(gettext("Clear List"))
        # clear_button.activated.connect(self.on_clear_list)
        # vert_layout.add(clear_button, margin=10)

        self.update_list()
        config = get_config(self)
        config.add_listener(self)

    def onDestroy(self):
        config = get_config(self)
        config.remove_listener(self)
        super().onDestroy()

    def on_config(self, key, _):
        if key.startswith(self.file_key_prefix):
            self.update_list()

    def on_activate_item(self, item):
        config = get_config(self)
        path = config.get(self.file_key.format(item))
        sha1 = config.get(self.sha1_key.format(item))
        if self.cd_mode:
            pass
        else:
            fsgs.amiga.insert_floppy_in_free_drive(path, sha1=sha1)

    def create_list(self):
        config = get_config(self)
        items = []
        if self.cd_mode:
            max_items = Amiga.MAX_CDROM_IMAGES
        else:
            max_items = Amiga.MAX_FLOPPY_IMAGES
        for i in range(max_items):
            path = config.get(self.file_key.format(i))
            sha1 = config.get(self.sha1_key.format(i))
            if not path:
                continue
            items.append((path, sha1))
        return items

    def update_list(self):
        # items = []
        self.list_view.clear()
        for path, sha1 in self.create_list():
            dir_path, name = os.path.split(path)
            if dir_path:
                label = "{0} ({1})".format(name, dir_path)
            else:
                label = path
            self.list_view.add_item(label, self.default_icon)
            # self.list_view.set_items(items)

    def on_clear_list(self):
        config = get_config(self)
        if self.cd_mode:
            CDManager.clear_cdrom_list(config=config)
        else:
            FloppyManager.clear_floppy_list(config=config)

    def on_remove_button(self):
        index = self.list_view.index()
        existing_items = self.create_list()
        if 0 <= index < len(existing_items):
            del existing_items[index]
            self.set_new_config(existing_items)

    def on_add_button(self):
        existing_items = self.create_list()

        default_dir = FSGSDirectories.get_floppies_dir()
        if self.cd_mode:
            dialog = LauncherFilePicker(
                self.get_window(),
                gettext("Select Multiple CD-ROMs"),
                "cd",
                multiple=True,
            )
        else:
            dialog = LauncherFilePicker(
                self.get_window(),
                gettext("Select Multiple Floppies"),
                "floppy",
                multiple=True,
            )
        if not dialog.show_modal():
            print("dialog.show returned false")
            return
        print("dialog.show returned true")
        paths = dialog.get_paths()
        paths.sort()
        print(paths)

        checksum_tool = ChecksumTool(self.get_window())
        for i, path in enumerate(paths):
            sha1 = checksum_tool.checksum(path)
            path = Paths.contract_path(path, default_dir)

            dir_path, file = os.path.split(path)
            if os.path.normcase(
                os.path.normpath(dir_path)
            ) == os.path.normcase(os.path.normpath(default_dir)):
                path = file

            existing_items.append((path, sha1))
        self.set_new_config(existing_items)

    def set_new_config(self, items):
        if self.cd_mode:
            max_items = Amiga.MAX_CDROM_IMAGES
        else:
            max_items = Amiga.MAX_FLOPPY_IMAGES
        set_list = []
        for i in range(max(max_items, len(items))):
            if i >= max_items:
                break
            elif i >= len(items):
                path, sha1 = "", ""
            else:
                path, sha1 = items[i]
            set_list.append((self.file_key.format(i), path))
            set_list.append((self.sha1_key.format(i), sha1))
        config = get_config(self)
        config.set_multiple(set_list)


class SaveDiskCheckBox(fsui.CheckBox):
    def __init__(self, parent):
        super().__init__(parent, gettext("Include Save Disk"))
        self.set_tooltip(
            gettext(
                "When checked, include a save disk in FS-UAE's floppy swap list"
            )
        )
        ConfigBehavior(self, [Option.SAVE_DISK])

    def on_changed(self):
        config = get_config(self)
        config.set(Option.SAVE_DISK, "" if self.checked() else "0")

    def on_save_disk_config(self, value: str):
        self.setChecked(value != "0")
