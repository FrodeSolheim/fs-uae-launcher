import fsgs
import fsui
from fsui.extra.iconheader import IconHeader
from fsbc.application import app
from launcher.i18n import gettext
from launcher.ui.skin import LauncherTheme
from launcher.ui.widgets import CloseButton

class InfoDialog(fsui.Window):
    def __init__(self, parent):
        app_name = "Netplay Info"
        title = f"{app_name}"
        super().__init__(parent, title, minimizable=False, maximizable=False)
        self.theme = LauncherTheme.get()
        self.layout = fsui.VerticalLayout()
        self.layout.set_padding(20)

        self.icon_header = IconHeader(
            self,
            fsui.Icon("fs-uae-launcher", "pkg:launcher"),
            f"{app_name}",
            "Copyright © 2012-2017 Frode Solheim",
        )
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        self.text_area = fsui.TextArea(
            self, info_message, read_only=True, font_family="monospace"
        )
        self.text_area.scroll_to_start()
        self.text_area.set_min_width(760)
        self.text_area.set_min_height(340)
        self.layout.add(self.text_area, fill=True, expand=True)

        CloseButton.add_to_layout(self, self.layout, margin_top=20)


info_message = """\n
How to Use Netplay:

1. Join or create a game channel using the 'Join Game Channel' button.
2. Enter the port and number of players if you are hosting.
3. Use the 'Host Game' button to start hosting.
4. Use the 'Ready' button to indicate you are ready to play.
5. Use the 'Send Config' button to send your configuration to other players (optional).
6. Once all players are ready, you can start the game in FS-UAE.

If required, you can use the netplay command box to enter manual IRC or netplay commands.

You can also use IRC commands directly in the command box as follows:
(Replace text within <> as appropriate)

Create a game channel (make sure the -game is appended):
/join #<game-name>-game
Once in the channel, host a game using the FQDN to allow players to either 
use public DNS resolution or a static host file entry.
To start the game with a specific number of players (in this case 2) use the following command:
/hostgame <host.domain.com>:<port> <players>

Once both players are in the channel and the hostgame command has been run, enter the following:
/ready
You can now start the game in FS-UAE.

Other commands:

/sendconfig
/resetconfig
/verify
check amiga_model

More info @ https://fs-uae.net/launcher-net-play
"""
