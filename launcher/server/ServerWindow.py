import traceback

import fsui


class ServerWindow(fsui.Window):
    def __init__(self, parent, server):
        fsui.Window.__init__(self, parent, "FS-UAE Net Play Server")
        self.layout = fsui.VerticalLayout()
        self.layout.padding_top = 50
        self.layout.padding_bottom = 50
        self.layout.padding_left = 50
        self.layout.padding_right = 50
        self.label = fsui.Label(self, "Close window to stop server")
        self.layout.add(self.label)
        self.server = server
        self.set_size(self.layout.get_min_size())

    def on_close(self):
        print("ServerWindow.on_close")
        try:
            self.server.kill()
        except Exception:
            traceback.print_exc()
