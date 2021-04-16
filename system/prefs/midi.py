import subprocess
from typing import List

from fsgamesys.plugins.pluginexecutablefinder import PluginExecutableFinder
from fsui import Panel
from launcher.fswidgets2.flexcontainer import VerticalFlexContainer
from launcher.fswidgets2.textarea import TextArea
from launcher.translation import t
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefswindow import BasePrefsWindow2


@shellObject
class MIDI:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(MidiPrefsWindow, **kwargs)


class MidiPrefsWindow(BasePrefsWindow2):
    def __init__(self):
        super().__init__(t("MIDI preferences"), MidiPrefsPanel)


class MidiPrefsPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((640, 400))

        lines: List[str] = []
        lines.append(
            "For now, this preferences window only list portmidi device "
            "names. In the future, there should be GUI options here to "
            "choose the desired device. For now, these device names can be "
            "used with FS-UAE's serial port option to enable MIDI output."
        )
        lines.append("")
        executable = PluginExecutableFinder().find_executable(
            "fs-uae-device-helper"
        )
        if executable:
            p = subprocess.run(
                [executable, "list-portmidi-devices"], stdout=subprocess.PIPE
            )
            for line in p.stdout.splitlines():
                lines.append(line.decode("UTF-8"))
            if p.returncode != 0:
                lines.append(f"Process exited with error {p.returncode}")
            else:
                lines.append("")
                lines.append(
                    "(Device names are the text between the quotation marks)"
                )
        else:
            lines.append("Could not find fs-uae-device-helper")
        with VerticalFlexContainer(self, style={"padding": 20}):
            TextArea(text="\n".join(lines), style={"flexGrow": 1})
