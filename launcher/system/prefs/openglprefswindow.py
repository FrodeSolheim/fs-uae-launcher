from fsgamesys.options.option import Option
from fsui import MultiLineLabel
from launcher.i18n import gettext
from launcher.system.prefs.baseprefspanel import BasePrefsPanel
from launcher.system.prefs.baseprefswindow import BasePrefsWindow


class OpenGLPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("OpenGL preferences"))
        self.panel = OpenGLPrefsPanel(self)
        self.layout.add(self.panel, fill=True, expand=True)


class OpenGLPrefsPanel(BasePrefsPanel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(20, 0, 20, 20)

        self.add_option(Option.FSAA)
        self.add_option(Option.TEXTURE_FILTER)
        self.add_option(Option.TEXTURE_FORMAT)

        # self.add_section(gettext("Video Synchronization"))
        self.sync_method_label = MultiLineLabel(
            self,
            gettext(
                "Depending on your OS and OpenGL drivers, video synchronization "
                "can use needlessly much CPU (esp. applies to "
                "Linux). You can experiment with different sync methods "
                "to improve performance."
            ),
            640,
        )
        self.layout.add(self.sync_method_label, fill=True, margin_top=20)
        self.sync_method_group = self.add_option(Option.VIDEO_SYNC_METHOD)
