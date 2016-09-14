from fsbc.util import unused
import fsui
from fsgs.amiga.Amiga import Amiga
from ..launcher_config import LauncherConfig
from .FloppiesGroup import FloppiesGroup


class RemovableMediaGroup(FloppiesGroup):

    def __init__(self, parent, drives):
        FloppiesGroup.__init__(self, parent, drives)
        self.layout3 = fsui.HorizontalLayout()
        self.layout.add(self.layout3, fill=True)

        self.layout3.add_spacer(0, expand=True)

        self.cd_mode = False

        self.update_media_type()
        LauncherConfig.add_listener(self)

    def on_destroy(self):
        LauncherConfig.remove_listener(self)

    def on_config(self, key, value):
        unused(value)
        if key == "amiga_model":
            self.update_media_type()

    def update_media_type(self):
        self.set_cd_mode(Amiga.is_cd_based(LauncherConfig))

    def set_cd_mode(self, cd_mode):
        if self.cd_mode == cd_mode:
            return
        self.cd_mode = cd_mode
        for selector in self.selectors:
            selector.set_cd_mode(cd_mode)
        self.update_heading_label()
        self.selectors[1].enable(not self.cd_mode)
