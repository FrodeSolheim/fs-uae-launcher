import fsui
from launcher.i18n import gettext
from launcher.netplay.irc import LOBBY_CHANNEL
from launcher.netplay.irc_broadcaster import IRCBroadcaster
from launcher.netplay.netplay import Netplay
from launcher.ui.skin import Skin
from launcher.ui.InfoDialog import InfoDialog
from launcher.ui.IconButton import IconButton
from PyQt5.QtWidgets import QApplication

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
        button_layout = fsui.HorizontalLayout()
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

        self._build_game_inputs()
        self._manual_command_input()

        
        self.netplay = Netplay()
        IRCBroadcaster.add_listener(self)
        # Create buttons for various actions
        # Join Channel button to join a game channel (shown in all channels)
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
        # This command is used to set the initial active channel and hide the action buttons
        self.active_channel = LOBBY_CHANNEL 
        self.input_field.focus()

    def _manual_command_input(self):
        self.layout.add(fsui.Label(self, gettext("Netplay Server Commands")), margin=10, margin_top=10)
        self.input_field = fsui.TextField(self)
        self.input_field.activated.connect(self.on_input)
        self.layout.add(self.input_field, fill=True, margin=10, margin_top=0)

    def _build_game_inputs(self):
        input_row = fsui.HorizontalLayout()
        self.layout.add(input_row, fill=True, margin=10, margin_top=0)

        self.port_label = fsui.Label(self, gettext("Port (default: 25101)"))
        input_row.add(self.port_label, margin_right=5)
        self.port_field = fsui.TextField(self)
        self.port_field.set_text("25101")
        self.port_field.set_min_width(75)
        input_row.add(self.port_field, fill=False, margin_right=15)

        self.player_count_label = fsui.Label(self, gettext("Number of Players"))
        input_row.add(self.player_count_label, margin_right=5)
        self.player_count_field = fsui.TextField(self)
        self.player_count_field.set_text("2")
        input_row.add(self.player_count_field, fill=False)
        # Add a spacer to push the info button to the far right
        input_row.add_spacer(0, expand=True)  
        info_button = InfoButton(self)
        input_row.add(info_button, margin_left=10)

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
            self.port_field,
            self.player_count_label,
            self.port_label,
            self.ready_button,
        ]

        # Determine which buttons should be shown
        if in_game_channel and is_op:
            show_list = set(all_buttons) - {self.ready_button}
        elif in_game_channel and not is_op:
            show_list = {self.ready_button}
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
        port = self.panel.port_field.get_text().strip() or "25101"
        player_count = self.panel.player_count_field.get_text().strip() or "2"
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
