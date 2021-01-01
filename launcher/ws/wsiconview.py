import os

from fsui import Color, Image, Panel, ScrollArea
from launcher.ws.shell import shell_basename, shell_dirname, shell_icon
from launcher.ws.wsiconwidget import WSIconWidget


class IconViewIconHolder:
    def __init__(self, widget):
        self.widget = widget


class WSIconView(ScrollArea):
    def __init__(self, parent, *, vertical_layout=False, textcolor=None):
        super().__init__(parent)
        # self.set_background_color(fsui.Color(0x006699))
        self.vertical_layout = vertical_layout

        # self.set_background_color(fsui.Color(0x808080))
        self.panel = Panel(self)
        # self.panel.set_background_color(fsui.Color(0x009900))
        # self.panel.set_background_color(None)

        # FIXME: Why is it necessary to set a transparent color here? Shouldn't
        # it be sufficient to let the panel have its autoFillBackground set
        # to False (default)?
        self.panel.set_background_color(Color(0, 0, 0, 0))
        # self.panel._widget.setAutoFillBackground(False)

        self.icons = []
        if textcolor:
            self.textcolor = textcolor
        else:
            self.textcolor = Color(0x000000)

        # FIXME: Fix fsui.ScrollArea / Panel constructor so this isn't
        # necessary? (Child calls method on parent when parenting)
        self.set_child(self.panel)
        # self.panel.set_size((1400, 200))

        # self._qwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self._qwidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # # Base: 9999

        # g1 = "#858585"
        # g2 = "#8A8A8A"
        # g3 = "#909090"

        # # Handle gradient
        # hg1 = "#AAAAAA"
        # hg2 = "#999999"

        # # Handle hover gradient
        # hhg1 = "#B2B2B2"
        # hhg2 = "#A0A0A0"

        # # Handle pressed color
        # hpc = "#777777"

        # Base: AEAEAE

        g1 = "#959595"
        g2 = "#9A9A9A"
        g3 = "#A0A0A0"

        # Handle gradient
        hg1 = "#BBBBBB"
        hg2 = "#AEAEAE"

        # Handle hover gradient
        hhg1 = "#BEBEBE"
        hhg2 = "#B4B4B4"

        # Handle pressed color
        hpc = "#8C8C8C"

        scrollbar_stylesheet = f"""
            QScrollBar:vertical {{
                border: 0px;
                background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 {g1}, stop: {1 / (16 - 1)} {g2} stop: 1 {g3});
                width: 16px;
                margin: 0 0 0 0;
            }}

            QScrollBar:horizontal {{
                border: 0px;
                background-color: qlineargradient(x1: 0, y1: 0 x2: 0, y2: 1, stop: 0 {g1}, stop: {1 / (16 - 1)} {g2} stop: 1 {g3});
                height: 16px;
                margin: 0 0 0 0;
            }}

            QScrollBar::handle:vertical {{
                /* background: #999999; */
                background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 {hg1} stop: 1 {hg2});
                min-height: 60px;
            }}

            QScrollBar::handle:horizontal {{
                background-color: qlineargradient(x1: 0, y1: 0 x2: 0, y2: 1, stop: 0 {hg1} stop: 1 {hg2});
                min-height: 60px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 {hhg1} stop: 1 {hhg2});
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: qlineargradient(x1: 0, y1: 0 x2: 1, y2: 0, stop: 0 {hhg1} stop: 1 {hhg2});
            }}

            QScrollBar::handle:vertical:pressed {{
                background: {hpc};
            }}

            QScrollBar::handle:horizontal:pressed {{
                background: {hpc};
            }}

            QScrollBar::add-line:vertical {{
                border: none;
                background: none;
                width: 0;
                height: 0;
            }}

            QScrollBar::add-line:horizontal {{
                border: none;
                background: none;
                width: 0;
                height: 0;
            }}

            QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                width: 0;
                height: 0;
            }}

            QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                width: 0;
                height: 0;
            }}
            """
        self._qwidget.horizontalScrollBar().setStyleSheet(scrollbar_stylesheet)
        self._qwidget.verticalScrollBar().setStyleSheet(scrollbar_stylesheet)

    def clear_selection(self, exception=None):
        for icon in self.icons:
            if icon.widget == exception:
                pass
            else:
                icon.widget.set_selected(False)

    def _add_icon(self, path, normal_image, selected_image, *, label=None):
        if label is None:
            label = self._label_for_path(path)
        # label = shell_basename(path)
        # if label.endswith(":"):
        #     # Hack for volumes
        #     label = label[:-1]
        wsopen = path

        widget = WSIconWidget(
            self.panel,
            label=label,
            icon=normal_image,
            selected_icon=selected_image,
            textcolor=self.textcolor,
        )
        widget.set_position((0, 0))
        widget.wsopen = wsopen
        self.icons.append(IconViewIconHolder(widget))
        self.layout_icons()

    def add_shell_icon(self, path):
        print("add_shell_icon", path)

        # normal_image = Image.create_blank(1, 1)
        # selected_image = Image.create_blank(1, 1)

        info_path = path
        # path = info_path[:-5]
        name = shell_basename(path)
        if name.lower().endswith(".info"):
            label = name[:-5]
        else:
            label = name

        icon = shell_icon(info_path)
        normal_image = icon.normal_image()
        selected_image = icon.selected_image()

        self._add_icon(path, normal_image, selected_image, label=label)

    def _label_for_path(self, path):
        label = shell_basename(path)
        if label.endswith(":"):
            # Hack for volumes
            label = label[:-1]
        return label

    def add_launcher_icon(self, path):
        print("add_launcher_icon", path)

        label = self._label_for_path(path)
        # label = shell_basename(path)
        # if label.endswith(":"):
        #     # Hack for volumes
        #     label = label[:-1]
        # wsopen = path

        icon_dir = os.path.join(
            "data", "Icons", shell_dirname(path).replace(":", "/")
        )
        print(icon_dir, label)
        normal_image = Image(os.path.join(icon_dir, label + ".png"))
        selected_image = Image(os.path.join(icon_dir, label + "_Selected.png"))

        # # FIXME
        # icon = Image(
        #     os.path.join("data", "Icons")
        #     os.path.expanduser(
        #         "~/openretro/icons/Prefs/" + label + "_Normal.png"
        #     )
        # )
        # try:
        #     # icon = Image(
        #     #     os.path.expanduser("~/openretro/icons/Prefs/" + label + "/" + label + "_Normal.png")
        #     # )
        #     icon = Image(
        #         os.path.expanduser(
        #             "~/openretro/icons/Prefs/" + label + "_Normal.png"
        #         )
        #     )
        # except Exception:
        #     icon = Image(
        #         os.path.expanduser("~/openretro/icons/Prefs/Help_Normal.png")
        #     )

        # try:
        #     # selected_icon = Image(
        #     #     os.path.expanduser("~/openretro/icons/Prefs/" + label + "/" + label + "_Selected.png")
        #     # )
        #     selected_icon = Image(
        #         os.path.expanduser(
        #             "~/openretro/icons/Prefs/" + label + "_Selected.png"
        #         )
        #     )
        # except Exception:
        #     selected_icon = Image(
        #         os.path.expanduser("~/openretro/icons/Prefs/Help_Selected.png")
        #     )

        # try:
        #     selected_icon = Image(
        #         os.path.expanduser("~/openretro/icons/Prefs/" + label + "/" + label + "_Selected.png")
        #     )
        # except Exception:
        #     try:
        #         selected_icon = Image(
        #             os.path.expanduser(
        #                 "~/openretro/icons/Prefs/" + label + "_Selected.png"
        #             )
        #         )
        #     except Exception:
        #         selected_icon = None
        #         selected_icon = icon.copy()
        #         selected_icon.invert()
        self._add_icon(path, normal_image, selected_image, label=label)

    def layout_icons(self):
        if self.vertical_layout:
            w, h = self.layout_icons_vertically()
        else:
            w, h = self.layout_icons_horizontally()
        self.panel.set_size((w, h))
        # self.panel.set_size((1000, 500))

    def layout_icons_horizontally(self):
        print(" --- layout_icons", self.width())
        x = 10
        y = 10
        w = 0
        h = 0
        for icon in self.icons:
            icon.widget.set_position((x, y))
            x += WSIconWidget.ICON_WIDGET_WIDTH
            if x > w:
                w = x
            if y + WSIconWidget.ICON_WIDGET_HEIGHT > y:
                h = y + WSIconWidget.ICON_WIDGET_HEIGHT
            if x + WSIconWidget.ICON_WIDGET_WIDTH > self.width():
                x = 10
                y += WSIconWidget.ICON_WIDGET_HEIGHT
        return w, h

    def layout_icons_vertically(self):
        padding_y = 30
        x = 10
        y = padding_y
        w = 0
        h = 0
        for icon in self.icons:
            icon.widget.set_position((x, y))
            y += WSIconWidget.ICON_WIDGET_WIDTH
            if y > h:
                h = y
            if x + WSIconWidget.ICON_WIDGET_WIDTH > x:
                w = x + WSIconWidget.ICON_WIDGET_WIDTH
            if y + WSIconWidget.ICON_WIDGET_HEIGHT > self.height():
                y = padding_y
                x += WSIconWidget.ICON_WIDGET_WIDTH
        return w, h

    def on_resize(self):
        # print("resize?")
        super().on_resize()
        self.layout_icons()
