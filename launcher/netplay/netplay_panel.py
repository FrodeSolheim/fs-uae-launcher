import fsui
from launcher.i18n import gettext
from launcher.netplay.irc import LOBBY_CHANNEL
from launcher.netplay.irc_broadcaster import IRCBroadcaster
from launcher.netplay.netplay import Netplay
from launcher.ui.skin import Skin


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

        # label = fsui.Label(self, "Netplay is currently disabled in the "
        #                          "development versions.")
        # self.layout.add(label, margin=10)
        # label = fsui.Label(self, "Please use the stable FS-UAE series for "
        #                          "netplay in the meantime.")
        # self.layout.add(label, margin=10)
        # return

        # TODO
        gettext("Nick:")
        gettext("Connect")
        gettext("Disconnect")

        # self.nick_label = fsui.Label(self, _("Nick:"))
        # hori_layout.add(self.nick_label,
        #         margin=10, margin_top=0, margin_bottom=0)
        #
        # self.nick_field = fsui.TextField(self, Settings.get("irc_nick"))
        # self.nick_field.set_min_width(130)
        # hori_layout.add(self.nick_field, margin_right=10)
        # #self.nick_field.on_changed = self.on_nick_change
        #
        # self.connect_button = fsui.Button(self, _("Connect"))
        # hori_layout.add(self.connect_button, margin_right=10)
        # #self.connect_button.activated.connect(self.on_connect_button)
        #
        # self.disconnect_button = fsui.Button(self, _("Disconnect"))
        # hori_layout.add(self.disconnect_button, margin_right=10)
        # #self.disconnect_button.activated.connect(self.on_disconnect_button)

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

        self.input_field = fsui.TextField(self)
        self.input_field.activated.connect(self.on_input)
        self.layout.add(self.input_field, fill=True, margin=10, margin_top=0)

        self.active_channel = LOBBY_CHANNEL

        self.input_field.focus()

        self.netplay = Netplay()
        IRCBroadcaster.add_listener(self)

    def on_destroy(self):
        print("NetplayPanel.on_destroy")
        IRCBroadcaster.remove_listener(self)
        self.netplay.disconnect()

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
        # self.text_area.append_text(IRC.channel(channel).get_text())
        ch = self.netplay.irc.channel(channel)
        for i, line in enumerate(ch.lines):
            self.text_area.append_text(line, ch.colors[i])
        self.active_channel = channel
        self.update_nick_list()
        for i in range(self.channel_list.get_item_count()):
            if self.channel_list.get_item(i) == channel:
                self.channel_list.set_index(i)

    def update_channel_list(self):
        items = sorted(self.netplay.irc.channels.keys())
        # items[0] = "IRC ({0})".format(Settings.get_irc_server())
        # items[0] = Settings.get_irc_server()
        self.channel_list.set_items(items)

    def update_nick_list(self):
        items = self.netplay.irc.channel(self.active_channel).get_nick_list()
        self.nick_list.set_items(items)

    def on_irc(self, key, args):
        if key == "active_channel":
            self.set_active_channel(args["channel"])
        elif key == "nick_list":
            if args["channel"] == self.active_channel:
                self.update_nick_list()
        elif key == "channel_list":
            self.update_channel_list()
        elif key == "message":
            if args["channel"] == self.active_channel:
                self.text_area.append_text(
                    args["message"], color=args["color"]
                )
            self.window.alert()
