import fsui


class PreferencesHeader(fsui.Group):

    def __init__(self, parent, icon, title, subtitle):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.HorizontalLayout()
        # self.layout.set_padding(0, 20, 0, 20)

        heading_layout = self.layout
        heading_layout.add(fsui.ImageView(self, icon), fill=-1)
        heading_layout.add_spacer(20)
        heading_layout_2 = fsui.VerticalLayout()
        heading_layout.add(
            heading_layout_2, expand=True, fill=False, valign=0.5)
        heading_layout_2.add(fsui.HeadingLabel(self, title))
        heading_layout_2.add_spacer(4)
        heading_layout_2.add(fsui.Label(self, subtitle))
