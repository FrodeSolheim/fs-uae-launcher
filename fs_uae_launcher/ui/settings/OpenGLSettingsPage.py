import fsui as fsui
from ...I18N import gettext
from .OptionUI import OptionUI


class OpenGLSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        label = fsui.HeadingLabel(self, gettext("OpenGL Settings"))
        self.layout.add(label, margin=10, margin_bottom=20)

        def add_option(name):
            self.layout.add(OptionUI.create_group(self, name), fill=True,
                            margin_top=10, margin_bottom=10)

        add_option("fsaa")
        add_option("texture_filter")
        add_option("video_sync_method")
        add_option("texture_format")
