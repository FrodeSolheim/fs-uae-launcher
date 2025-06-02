import os

import fsui
from fsgs.checksumtool import ChecksumTool
from fsgs.FSGSDirectories import FSGSDirectories
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.option import Option
from launcher.ui.behaviors.platformbehavior import AmigaEnableBehavior
from launcher.ui.config.configpanel import ConfigPanel
from launcher.ui.IconButton import IconButton
from launcher.ui.LauncherFilePicker import LauncherFilePicker
from launcher.ui.options import ConfigWidgetFactory


class RomRamPanel(ConfigPanel):
    def __init__(self, parent):
        ConfigPanel.__init__(self, parent)
        heading_label = fsui.HeadingLabel(self, gettext("ROM & RAM"))
        self.layout.add(heading_label, margin=10)
        self.layout.add_spacer(0)

        self.kickstart_group = KickstartGroup(self)
        self.layout.add(self.kickstart_group, fill=True)
        self.layout.add_spacer(10)
        self.memory_group = MemoryGroup(self)
        self.layout.add(self.memory_group, fill=True)


class KickstartGroup(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        AmigaEnableBehavior(self)
        self.layout = fsui.VerticalLayout()

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        label = fsui.Label(self, gettext("Kickstart ROM") + ":")
        hori_layout.add(label, margin_left=10, margin_right=10)

        kickstart_types = [
            gettext("Default"),
            gettext("Custom"),
            gettext("Internal"),
        ]
        self.kickstart_type_choice = fsui.Choice(self, kickstart_types)
        hori_layout.add(self.kickstart_type_choice, margin=10)

        self.text_field = fsui.TextField(self, "", read_only=True)
        hori_layout.add(self.text_field, expand=True, margin=10)

        self.browse_button = IconButton(self, "browse_file_16.png")
        self.browse_button.set_tooltip(gettext("Browse for File"))
        self.browse_button.activated.connect(self.on_browse_button)
        hori_layout.add(self.browse_button, margin=10)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        label = fsui.Label(self, gettext("Extended ROM") + ":")
        hori_layout.add(label, margin_left=10, margin_right=10)
        # self.layout.add_spacer(0)

        kickstart_types = [gettext("Default"), gettext("Custom")]
        self.ext_rom_type_choice = fsui.Choice(self, kickstart_types)
        hori_layout.add(self.ext_rom_type_choice, margin_right=10)

        self.ext_text_field = fsui.TextField(self, "", read_only=True)
        hori_layout.add(self.ext_text_field, expand=True, margin_right=10)

        self.ext_browse_button = IconButton(self, "browse_file_16.png")
        self.ext_browse_button.set_tooltip(gettext("Browse for File"))
        self.ext_browse_button.activated.connect(self.on_ext_browse_button)
        hori_layout.add(self.ext_browse_button, margin_right=10)

        self.initialize_from_config()
        self.set_config_handlers()

    def initialize_from_config(self):
        self.on_config("kickstart_file", LauncherConfig.get("kickstart_file"))
        self.on_config(
            "kickstart_ext_file", LauncherConfig.get("kickstart_ext_file")
        )

    def set_config_handlers(self):
        self.kickstart_type_choice.on_changed = self.on_kickstart_type_changed
        self.ext_rom_type_choice.on_changed = self.on_ext_rom_type_changed
        LauncherConfig.add_listener(self)

    def on_destroy(self):
        print("on_destroy")
        LauncherConfig.remove_listener(self)

    def on_kickstart_type_changed(self):
        index = self.kickstart_type_choice.get_index()
        if index == 0:
            if LauncherConfig.get("kickstart_file") == "":
                return
            LauncherConfig.set("kickstart_file", "")
        elif index == 2:
            if LauncherConfig.get("kickstart_file") == "internal":
                return
            LauncherConfig.set("kickstart_file", "internal")
        else:
            LauncherConfig.set(
                "kickstart_file", LauncherConfig.get("x_kickstart_file")
            )
        LauncherConfig.update_kickstart()

    def on_ext_rom_type_changed(self):
        index = self.ext_rom_type_choice.get_index()
        if index == 0:
            if LauncherConfig.get("kickstart_ext_file") == "":
                return
            LauncherConfig.set("kickstart_ext_file", "")
        else:
            LauncherConfig.set(
                "kickstart_ext_file",
                LauncherConfig.get("x_kickstart_ext_file"),
            )
        LauncherConfig.update_kickstart()

    def on_browse_button(self, extended=False):
        default_dir = FSGSDirectories.get_kickstarts_dir()
        if extended:
            title = gettext("Choose Extended ROM")
            key = "kickstart_ext_file"
        else:
            title = gettext("Choose Kickstart ROM")
            key = "kickstart_file"
        dialog = LauncherFilePicker(
            self.get_window(), title, "rom", LauncherConfig.get(key)
        )
        if not dialog.show_modal():
            return
        path = dialog.get_path()

        checksum_tool = ChecksumTool(self.get_window())
        sha1 = checksum_tool.checksum_rom(path)

        dir_path, file = os.path.split(path)
        if extended:
            self.ext_text_field.set_text(file)
        else:
            self.text_field.set_text(file)
        if os.path.normcase(os.path.normpath(dir_path)) == os.path.normcase(
            os.path.normpath(default_dir)
        ):
            path = file

        if extended:
            LauncherConfig.set_multiple(
                [
                    ("kickstart_ext_file", path),
                    ("x_kickstart_ext_file", path),
                    ("x_kickstart_ext_file_sha1", sha1),
                ]
            )
        else:
            LauncherConfig.set_multiple(
                [
                    ("kickstart_file", path),
                    ("x_kickstart_file", path),
                    ("x_kickstart_file_sha1", sha1),
                ]
            )

    def on_ext_browse_button(self):
        return self.on_browse_button(extended=True)

    def on_config(self, key, value):
        if key == "kickstart_file":
            if value == "internal":
                self.text_field.set_text("")
                self.kickstart_type_choice.set_index(2)
            elif value:
                _, file = os.path.split(value)
                self.text_field.set_text(file)
                self.kickstart_type_choice.set_index(1)
            else:
                self.text_field.set_text("")
                self.kickstart_type_choice.set_index(0)
        elif key == "kickstart_ext_file":
            if value:
                _, file = os.path.split(value)
                self.ext_text_field.set_text(file)
                self.ext_rom_type_choice.set_index(1)
            else:
                self.ext_text_field.set_text("")
                self.ext_rom_type_choice.set_index(0)


class MemoryGroup(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        AmigaEnableBehavior(self)
        self.layout = fsui.VerticalLayout()
        self.hori_layout = None
        self.hori_counter = 0
        config_widget_factory = ConfigWidgetFactory()
        self.add_widget(config_widget_factory.create(self, Option.CHIP_MEMORY))
        self.add_widget(
            config_widget_factory.create(self, Option.MOTHERBOARD_RAM)
        )
        self.add_widget(config_widget_factory.create(self, Option.SLOW_MEMORY))
        self.add_widget(
            config_widget_factory.create(self, Option.ZORRO_III_MEMORY)
        )
        self.add_widget(config_widget_factory.create(self, Option.FAST_MEMORY))
        self.add_widget(
            config_widget_factory.create(self, Option.ACCELERATOR_MEMORY)
        )
        self.add_widget(fsui.Label(self, ""))
        self.add_widget(
            config_widget_factory.create(self, Option.GRAPHICS_MEMORY)
        )

    def add_widget(self, widget):
        if self.hori_counter % 2 == 0:
            self.hori_layout = fsui.HorizontalLayout()
            self.layout.add(self.hori_layout, fill=True)
        self.hori_layout.add(
            widget, fill=True, expand=-1, margin=10, margin_bottom=0
        )
        if self.hori_counter % 2 == 0:
            self.hori_layout.add_spacer(10)
        self.hori_counter += 1
