from fsui import Font, Panel


class IconWidget(Panel):
    ICON_WIDGET_WIDTH = 120
    ICON_WIDGET_HEIGHT = 100

    def __init__(
        self, parent, *, label, icon, selected_icon=None, textcolor=None
    ):
        super().__init__(parent)
        self.set_size(
            (IconWidget.ICON_WIDGET_WIDTH, IconWidget.ICON_WIDGET_HEIGHT)
        )

        self.label = label
        self.icon = icon
        self.selected_icon = selected_icon
        self._selected = False

        # self.labelwidget = fsui.Label(self, label=label)
        # font = fsui.Font("Saira Condensed", 30, weight=600)
        # self.labelwidget.set_font(font)

        # self.labelwidget.update()
        # self.labelwidget.updateGeometry()
        # w, h = self.labelwidget.get_size()
        # print(w, h)
        # self.labelwidget.set_position((self.width() - w) / 2, self.height() - h)

        # FIXME: Not sure if the semi-bold / medium weights are read?
        # Updated: Works if the font is manually added to QFontDatabase
        # FIXME: Get common font objectfrom theme?
        self.font = Font("Saira Condensed", 18, weight=500)
        self.textcolor = textcolor

    def set_selected(self, selected):
        self._selected = selected
        self.refresh()

    def on_left_down(self):
        self.set_selected(True)
        # FIXME: This object should not need to worry about parent-parent?
        self.parent().parent().clear_selection(exception=self)

    def on_paint(self):
        # print("paint")
        ww, wh = self.size()
        dc = self.create_dc()
        # FIXME: Not sure if the semi-bold / medium weights are read?
        # Updated: Works if the font is manually added to QFontDatabase
        dc.set_font(self.font)
        tw, th = dc.measure_text(self.label)
        # self.draw_background(dc)
        dc.set_text_color(self.textcolor)
        dc.draw_text(self.label, (ww - tw) / 2, wh - th)
        icon = self.icon
        if self._selected and self.selected_icon:
            icon = self.selected_icon
        iw, ih = icon.size
        dc.draw_image(icon, (ww - iw) / 2, 8 + (64 - ih) / 2)


class WSIconWidget(IconWidget):
    def on_left_dclick(self):
        print("on_left_dlick")
        if hasattr(self, "wsopen") and self.wsopen:
            from system.wsopen import wsopen

            wsopen(self.wsopen, window=self.window, parent=self.window)
