from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import fsui
from ..common.group import Group


class IconHeader(Group):

    def __init__(self, parent, icon, title, subtitle=""):
        Group.__init__(self, parent)
        self.layout = fsui.HorizontalLayout()

        image = icon.image(48)
        self.image_view = fsui.ImageView(self, image)
        self.layout.add(self.image_view)
        self.layout.add_spacer(20)
        vert_layout = fsui.VerticalLayout()
        self.layout.add(
            vert_layout, expand=True, fill=False, valign=0.5)
        self.title_label = fsui.HeadingLabel(self, title)
        vert_layout.add(self.title_label)
        vert_layout.add_spacer(2)
        self.subtitle_label = fsui.Label(self, subtitle)
        vert_layout.add(self.subtitle_label, fill=True)
