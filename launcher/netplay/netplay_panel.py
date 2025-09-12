import fsui
from launcher.i18n import gettext
from launcher.netplay.irc import LOBBY_CHANNEL
from launcher.netplay.irc_broadcaster import IRCBroadcaster
from launcher.netplay.netplay import Netplay
from launcher.ui.skin import Skin
from launcher.ui.InfoDialog import InfoDialog
from launcher.ui.IconButton import IconButton
from PyQt5.QtWidgets import QApplication
from fsgs.amiga.amiga import Amiga
import configparser
from fsui.qt.DrawingContext import Font
from launcher.sync_settings import SYNC_CONFIG_PATH
from launcher.sync_settings import sync_settings
from launcher.launcher_config import LauncherConfig
from PyQt5 import QtGui

def close_windows_by_title(window_title):
    for widget in QApplication.topLevelWidgets():
        if widget.windowTitle().startswith(window_title):
            widget.close()

class NetplayPanel(fsui.Panel):
    def __init__(self, parent, header=True):
        fsui.Panel.__init__(self, parent)
        Skin.set_background_color(self)
        self.layout = fsui.VerticalLayout()

        if header:
            hori_layout = fsui.HorizontalLayout()
            self.layout.add(hori_layout, fill=True)
            self.layout.add_spacer(0)

            label = fsui.HeadingLabel(self, gettext("Net Play"))
            hori_layout.add(label, margin=10)

            hori_layout.add_spacer(0, expand=True)


        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True, expand=True)
        

        ver_layout = fsui.VerticalLayout()
        hori_layout.add(ver_layout, fill=True)
        self.channel_list = fsui.ListView(self)
        self.channel_list.set_min_width(212)
        self.channel_list.on_select_item = self.on_select_channel
        ver_layout.add(self.channel_list, fill=True, expand=True, margin=10)
        self.nick_list = fsui.ListView(self)
        ver_layout.add(self.nick_list, fill=True, expand=True, margin=10)

        self.text_area = fsui.TextArea(self, font_family="monospace")
        hori_layout.add(
            self.text_area, fill=True, expand=True, margin=10, margin_left=0
        )

        self.netplay = Netplay()
        IRCBroadcaster.add_listener(self)

        self._build_netplay_game_inputs()
        self._manual_command_input()
        self._build_netplay_buttons()

        # This command is used to set the initial active channel and hide the action buttons
        self.active_channel = LOBBY_CHANNEL 
        self.input_field.focus()

    def _manual_command_input(self):
        self.layout.add(fsui.Label(self, gettext("Netplay Server Commands")), margin=10, margin_top=10)
        self.input_field = fsui.TextField(self)
        self.input_field.activated.connect(self.on_input)
        self.layout.add(self.input_field, fill=True, margin=10, margin_top=0)

    def _build_netplay_game_inputs(self):
        input_row = fsui.HorizontalLayout()
        self.layout.add(input_row, fill=True, margin=10, margin_top=0)

        self.port_label = fsui.Label(self, gettext("Port (default: 25101)"))
        input_row.add(self.port_label, margin_right=5)
        self.port_field = fsui.TextField(self)
        self.port_field.set_text("25101")
        self.netplay_port_validator = QtGui.QIntValidator(bottom=25100, top=25500)
        self.port_field.setValidator(self.netplay_port_validator)  # Set validator.
        self.port_field.set_min_width(75)
        input_row.add(self.port_field, fill=False, margin_right=15)

        self.player_count_label = fsui.Label(self, gettext("Number of Players"))
        input_row.add(self.player_count_label, margin_right=5)
        self.player_count_field = fsui.TextField(self)
        self.player_count_field.set_text("2")
        self.player_count_validator = QtGui.QIntValidator(bottom=2, top=6)
        self.player_count_field.setValidator(self.player_count_validator)  # Set validator.
        input_row.add(self.player_count_field, fill=False)
        # Add a spacer to push the info button to the far right
        input_row.add_spacer(0, expand=True)

        self.config_button = ConfigButton(self)
        input_row.add(self.config_button, margin_left=10)

        info_button = InfoButton(self)
        input_row.add(info_button, margin_left=10)

    def _build_netplay_buttons(self):
        button_layout = fsui.HorizontalLayout()
        self.layout.add(button_layout, fill=True, margin=10)
        self.join_channel_button = JoinChannelButton(self, self.netplay.irc)
        button_layout.add(self.join_channel_button, fill=True, margin_left=0)
 
         # Add a spacer before the Start Game button and store a reference
        self.action_spacer_pre = button_layout.add_spacer(0, expand=True)

        # Host Game button to host a game on the IRC channel (only shown in game channels)
        self.host_game_button = HostGameButton(self, self.netplay, self, self.netplay.irc)
        button_layout.add(self.host_game_button, fill=True, margin_left=10)
        # Send Config button to send the current config to other players (only shown in game channels)
        self.send_config_button = SendConfig(self, self.netplay, self.netplay.irc)
        button_layout.add(self.send_config_button, fill=True, margin_left=10)
        # Reset button to reset config (only shown in game channels)
        self.reset_button = Reset(self, self.netplay, self.netplay.irc)
        button_layout.add(self.reset_button, fill=True, margin_left=10)
        # Start Game button (only shown in game channels)
        self.start_button = StartGameButton(self, self.netplay, self.netplay.irc)
        button_layout.add(self.start_button, fill=True, margin_left=10)

        # Add a spacer before the Start Game button and store a reference
        self.action_spacer_post = button_layout.add_spacer(0, expand=True)

        # Ready button to indicate player is ready (only shown in game channels)
        self.ready_button = Ready(self, self.netplay, self.netplay.irc)
        button_layout.add(self.ready_button, fill=True, margin_left=10)

    def on_destroy(self):
        print("NetplayPanel.on_destroy")
        IRCBroadcaster.remove_listener(self)
        self.netplay.disconnect()
        close_windows_by_title("FS-UAE Netplay Server - Game ID:")
        close_windows_by_title("Netplay Info")

    def on_show(self):
        # FIXME: currently disabled
        # return
        if not self.netplay.is_connected():
            self.netplay.connect()
        self.input_field.focus()

    def on_select_channel(self, index):
        # index = self.channel_list.get_index()
        # if index == 0:
        #     channel = ""
        # else:
        # assert index is not None
        if index is None:
            return
        channel = self.channel_list.get_item(index)
        self.netplay.irc.set_active_channel_name(channel)
        self.input_field.focus()

    def on_input(self):
        command = self.input_field.get_text().strip()
        if not command:
            return
        if self.netplay.handle_command(command):
            pass
        else:
            self.netplay.irc.handle_command(command)
        self.input_field.set_text("")

    def set_active_channel(self, channel):
        if channel == self.active_channel:
            return
        self.text_area.set_text("")
        ch = self.netplay.irc.channel(channel)
        for i, line in enumerate(ch.lines):
            self.text_area.append_text(line, ch.colors[i])
        self.active_channel = channel
        self.update_nick_list()
        for i in range(self.channel_list.get_item_count()):
            if self.channel_list.get_item(i) == channel:
                self.channel_list.set_index(i)
        self.update_action_buttons_visibility()
        

    def update_channel_list(self):
        items = sorted(self.netplay.irc.channels.keys())
        # items[0] = "IRC ({0})".format(Settings.get_irc_server())
        # items[0] = Settings.get_irc_server()
        self.channel_list.set_items(items)

    def update_nick_list(self):
        items = self.netplay.irc.channel(self.active_channel).get_nick_list()
        self.nick_list.set_items(items)

    def update_action_buttons_visibility(self):
        in_game_channel = self.active_channel and self.active_channel.endswith('-game')
        is_op = self.netplay.is_op()

        # Master list of all action buttons
        all_buttons = [
            self.host_game_button,
            self.send_config_button,
            self.reset_button,
            self.start_button,
            self.player_count_field,
            self.player_count_label,
            self.port_field,            
            self.port_label,
            self.ready_button,
            self.config_button
        ]

        # Determine which buttons should be shown
        if in_game_channel and is_op:
            show_list = set(all_buttons) - {self.ready_button}
        elif in_game_channel and not is_op:
            show_list = {self.ready_button, self.config_button}
        else:
            show_list = set()

        # Show/hide buttons accordingly
        for btn in all_buttons:
            if btn in show_list:
                btn.show()
            else:
                btn.hide()


    def on_irc(self, key, args):
        if key == "active_channel":
            self.set_active_channel(args["channel"])
        elif key == "join":
            # Only switch to lobby if the local user joined
            if args["channel"] == LOBBY_CHANNEL and args["nick"] == self.netplay.irc.my_nick:
                self.set_active_channel(LOBBY_CHANNEL)
        elif key == "nick_list":
            if args["channel"] == self.active_channel:
                self.update_nick_list()
                # Update visibility when nick list changes (e.g., ops)
                self.update_action_buttons_visibility()
        elif key == "channel_list":
            self.update_channel_list()
        elif key == "message":
            if args["channel"] == self.active_channel:
                self.text_area.append_text(
                    args["message"], color=args["color"]
                )


class SimpleTextInputDialog(fsui.Dialog):
    def __init__(self, parent, title, label_text):
        super().__init__(parent, title)
        self.layout = fsui.VerticalLayout()
        self.label = fsui.Label(self, label_text)
        self.layout.add(self.label, margin=10)
        self.text_field = fsui.TextField(self)
        self.text_field.set_text("new")
        self.text_field.select_all()
        self.layout.add(self.text_field, fill=True, margin=10)
        button_row = fsui.HorizontalLayout()
        self.ok_button = fsui.Button(self, gettext("OK"))
        self.ok_button.activated.connect(self.on_ok)
        button_row.add(self.ok_button, fill=True, margin_right=10)
        self.cancel_button = fsui.Button(self, gettext("Cancel"))
        self.cancel_button.activated.connect(self.reject)
        button_row.add(self.cancel_button, fill=True)
        self.layout.add(button_row, margin=10)
        self.text_field.activated.connect(self.on_ok)
        self.result_text = None

    def on_ok(self):
        self.result_text = self.text_field.get_text()
        self.accept()

    @staticmethod
    def get_text(parent, title, label_text):
        dialog = SimpleTextInputDialog(parent, title, label_text)
        if dialog.exec_():
            return dialog.result_text
        return None

class JoinChannelButton(fsui.Button):
    def __init__(self, parent, irc):
        super().__init__(parent, gettext("Join Game Channel"))
        self.irc = irc

    def on_activated(self):
        game_name = SimpleTextInputDialog.get_text(self, gettext("Enter Game Name"), gettext("Game Name:"))
        if game_name:
            game_name = game_name.replace(" ", "-").lower()
            # Broadcast the command as a message in the IRC channel
            self.irc.handle_command(f"/me ran the following command:")
            self.irc.handle_command(f"/me /join #{game_name}-game")
            self.irc.handle_command(f"/join #{game_name}-game")

class HostGameButton(fsui.Button):
    def __init__(self, parent, netplay, panel, irc):
        super().__init__(parent, gettext("Host Game"))
        self.netplay = netplay
        self.panel = panel
        self.irc = irc
        self.set_tooltip(gettext("Host a game on the IRC channel."))

    def on_activated(self):
        port = self.panel.port_field.get_text().strip()
        p_result, *_ = self.panel.netplay_port_validator.validate(port, 0)
        if p_result != QtGui.QValidator.State.Acceptable:
            self.irc.warning(
                f"netplay port must have a value between "
                f"{self.panel.netplay_port_validator.bottom()}-"
                f"{self.panel.netplay_port_validator.top()}, got {port}"
            )
            return
        player_count = self.panel.player_count_field.get_text().strip()
        pc_result, *_ = self.panel.player_count_validator.validate(player_count, 0)
        if pc_result != QtGui.QValidator.State.Acceptable:
            self.irc.warning(
                f"player count must have a value between "
                f"{self.panel.player_count_validator.bottom()}-"
                f"{self.panel.player_count_validator.top()}, got {player_count}"
            )
            return
        command = f"/hostgame {self.netplay.irc.client.host}:{port} {player_count}"
        # Broadcast the command as a message in the IRC channel
        self.irc.handle_command(f"/me ran the following command:")
        self.irc.handle_command(f"/me {command}")
        self.netplay.handle_command(command)

class SendConfig(fsui.Button):
    def __init__(self, parent, netplay, irc):
        super().__init__(parent, gettext("Send Config"))
        self.irc = irc
        self.netplay = netplay

    def on_activated(self):
        command = "/sendconfig"
        self.irc.handle_command(f"/me ran the following command:")
        self.irc.handle_command(f"/me {command}")
        self.netplay.handle_command(command)

class Ready(fsui.Button):
    def __init__(self, parent, netplay, irc):
        super().__init__(parent, gettext("Ready"))
        self.irc = irc
        self.netplay = netplay

    def on_activated(self):
        command = "/ready"
        self.irc.handle_command(f"/me ran the following command:")
        self.irc.handle_command(f"/me {command}")
        self.netplay.handle_command(command)

class Reset(fsui.Button):
    def __init__(self, parent, netplay, irc):
        super().__init__(parent, gettext("Reset"))
        self.irc = irc
        self.netplay = netplay

    def on_activated(self):
        command = "/reset"
        self.irc.handle_command(f"/me ran the following command:")
        self.irc.handle_command(f"/me {command}")
        self.netplay.handle_command(command)

class StartGameButton(fsui.Button):
    def __init__(self, parent, netplay, irc):
        super().__init__(parent, "Start Game")
        self.irc = irc
        self.netplay = netplay

    def on_activated(self):
        self.irc.handle_command(f"/me attempts to start the game.")
        from launcher.launcherapp import LauncherApp 
        LauncherApp.start_game()

class InfoButton(IconButton):
    def __init__(self, parent):
        super().__init__(parent, "info.png")
        self.set_tooltip(gettext("Show instructions for Netplay"))
        self.parent = parent
        self.set_size((32, 32))

    def on_activated(self):
        # Check if an InfoDialog is already open by window title
        for widget in QApplication.topLevelWidgets():
            if widget.windowTitle() == "Netplay Info":
                widget.raise_()
                widget.activateWindow()
                return
        # If not open, create and show it
        info_dialog = InfoDialog(self.parent)
        info_dialog.show()

class ConfigButton(IconButton):
    def __init__(self, parent):
        super().__init__(parent, "32/settings.png")  # Corrected path
        self.set_tooltip(gettext("Sync Config Settings"))
        self.parent = parent
        self.set_size((32, 32))

    def on_activated(self):
        # Check if a Sync Config dialog is already open by window title
        for widget in QApplication.topLevelWidgets():
            if widget.windowTitle() == "Sync Config":
                widget.raise_()
                widget.activateWindow()
                return
        # If not open, create and show it
        dlg = SyncConfigDialog(self.parent)
        dlg.show()
class SyncConfigDialog(fsui.Window):
    def __init__(self, parent):
        super().__init__(parent, "Sync Config", minimizable=False, maximizable=False)
        layout = fsui.VerticalLayout()
        layout.set_padding(20)

        self.fields = {}
        self.defaults = {
            "Max Floppy Drives": str(Amiga.MAX_FLOPPY_DRIVES),
            "Max Floppy Images": str(Amiga.MAX_FLOPPY_IMAGES),
            "Max CDROM Drives": str(Amiga.MAX_CDROM_DRIVES),
            "Max CDROM Images": str(Amiga.MAX_CDROM_IMAGES),
            "Max Hard Drives": str(Amiga.MAX_HARD_DRIVES),
        }
        self.fast_values = {
            "Max Floppy Drives": "4",
            "Max Floppy Images": "4",
            "Max CDROM Drives": "0",
            "Max CDROM Images": "0",
            "Max Hard Drives": "0",
        }
        LABEL_WIDTH = 160

        # Load saved config if it exists
        self.config = configparser.ConfigParser()
        self.config.read(SYNC_CONFIG_PATH)
        saved = self.config["sync"] if "sync" in self.config else {}

        for label, default in self.defaults.items():
            row = fsui.HorizontalLayout()
            label_widget = fsui.Label(self, label)
            label_widget.set_min_width(LABEL_WIDTH)
            row.add(label_widget, expand=True, margin_right=10)

            field = fsui.ComboBox(self)
            field.setEditable(False)  # Only allow selection, no manual entry
            allowed_values = [str(i) for i in range(0, 21)]
            field.set_items(allowed_values)
            # Set current value if present, else default
            current_value = saved.get(label, default)
            index = field.findText(current_value)
            if index != -1:
                field.setCurrentIndex(index)
            else:
                field.setCurrentIndex(0)  # fallback to first item
            field.set_min_width(40)
            field.setEnabled(False)  # Initially read-only
            self.fields[label] = field
            row.add(field, fill=False, expand=False)
            layout.add(row, margin_bottom=5)

        layout.add_spacer(0, expand=True)

        # Stack option buttons vertically
        mode_col = fsui.VerticalLayout()
        self.default_button = fsui.Button(self, "Default")
        self.fast_button = fsui.Button(self, "Fast")
        self.custom_button = fsui.Button(self, "Custom")
        mode_col.add(self.default_button, fill=True, margin_bottom=5)
        mode_col.add(self.fast_button, fill=True, margin_bottom=5)
        mode_col.add(self.custom_button, fill=True)
        layout.add(mode_col, fill=True, margin_bottom=10)

        self.default_button.on_activated = self.on_default
        self.fast_button.on_activated = self.on_fast
        self.custom_button.on_activated = self.on_custom

        # OK (left) and Cancel (right) row
        button_row = fsui.HorizontalLayout()
        self.ok_button = fsui.Button(self, "OK")
        self.cancel_button = fsui.Button(self, "Cancel")
        button_row.add(self.ok_button, fill=False)
        button_row.add_spacer(0, expand=True)
        button_row.add(self.cancel_button, fill=False)
        layout.add(button_row, fill=True)

        self.ok_button.on_activated = self.on_ok
        self.cancel_button.on_activated = self.close

        self.layout = layout
        self.set_size((260, 360))

        self.selected_mode = saved.get("mode", "default")

        # Simulate clicking the correct button (this sets fields and highlights)
        if self.selected_mode == "fast":
            self.fast_button.on_activated()
        elif self.selected_mode == "custom":
            self.custom_button.on_activated()
        else:
            self.default_button.on_activated()

    def set_fields(self, values=None, read_only=True, numbers_only=False):
        for label, field in self.fields.items():
            if values is not None:
                value = values[label]
                index = field.findText(value)
                if index != -1:
                    field.setCurrentIndex(index)
            field.setEnabled(not read_only)

    def on_ok(self):
        # Save current settings to sync_config.ini
        self.config["sync"] = {label: field.currentText() for label, field in self.fields.items()}
        self.config["sync"]["mode"] = self.selected_mode
        with open(SYNC_CONFIG_PATH, "w") as f:
            self.config.write(f)
        sync_settings.update()
        LauncherConfig.refresh_keys() 
        self.close()

    def on_default(self):
        self.set_fields(self.defaults, read_only=True, numbers_only=False)
        self.selected_mode = "default"
        self.highlight_mode_button("default")

    def on_fast(self):
        self.set_fields(self.fast_values, read_only=True, numbers_only=False)
        self.selected_mode = "fast"
        self.highlight_mode_button("fast")

    def on_custom(self):
        # Get saved values from config file, or current field values if not present
        saved = self.config["sync"] if "sync" in self.config else {}
        saved_values = {label: saved.get(label, self.fields[label].currentText()) for label in self.defaults}

        # If saved values do not match default or fast, use them
        if not (self._values_match(saved_values, self.defaults) or self._values_match(saved_values, self.fast_values)):
            self.set_fields(saved_values, read_only=False, numbers_only=True)
        else:
            # Otherwise, keep current values editable
            self.set_fields(values=None, read_only=False, numbers_only=True)

        self.selected_mode = "custom"
        self.highlight_mode_button("custom")

    def highlight_mode_button(self, selected):
        for mode, btn in [
            ("default", self.default_button),
            ("fast", self.fast_button),
            ("custom", self.custom_button),
        ]:
            current_font = btn.font()
            font_obj = Font(current_font.font)
            font_obj.font.setBold(mode == selected)
            btn.set_font(font_obj)

    def _values_match(self, a, b):
        return all(str(a[k]) == str(b[k]) for k in a)
