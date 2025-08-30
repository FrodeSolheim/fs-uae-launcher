import traceback
import fsui
from launcher.i18n import gettext


class ServerWindow(fsui.Window):
    def __init__(self, parent, server, game_id, port, channel):
        fsui.Window.__init__(self, parent, f"FS-UAE Netplay Server - Game ID: {game_id}, Port: {port}, Channel: {channel}")
        self.layout = fsui.VerticalLayout()
        self.layout.padding_top = 50
        self.layout.padding_bottom = 50
        self.layout.padding_left = 50
        self.layout.padding_right = 50
        self.label = fsui.MultiLineLabel(
            self,
            "",
            400,
        )
        self.label.set_text('Close window to stop server<br>'+
        'Game ID: '+game_id+'<br>'+
        'Game Port: '+str(port)+'<br>'+
        'Channel: '+channel)
        self.layout.add(self.label)
        self.server = server
        self.set_size(self.layout.get_min_size())

    def on_close(self):
        print("ServerWindow.on_close")
        try:
            self.server.kill()
        except Exception:
            traceback.print_exc()
