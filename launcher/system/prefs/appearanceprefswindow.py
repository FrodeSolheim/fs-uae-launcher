from fsgamesys.options.option import Option
from fsui import (
    Color,
    Group,
    HorizontalLayout,
    Label,
    Panel,
    TextField,
    get_window,
)
from launcher.context import get_settings
from launcher.i18n import gettext
from launcher.system.prefs.baseprefspanel import BasePrefsPanel
from launcher.system.prefs.baseprefswindow import BasePrefsWindow
from launcher.system.prefs.defaultprefsbutton import DefaultPrefsButton
from launcher.ui.IconButton import IconButton


class AppearancePrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Appearance preferences"))
        self.panel = AppearancePrefsPanel(self)
        self.layout.add(self.panel, fill=True, expand=True)


class ColorSettingIndicator(Panel):
    def __init__(self, parent, option):
        super().__init__(parent)
        self.option = option
        self.set_min_size((40, 30))
        # FIXME: Filter on options?
        # get_settings(self).add_listener(self, [self.option])
        self.color = Color(0, 0, 0)
        self.bordercolor = Color(0x666666)
        # self.cornercolor = Color(0xff0000)
        self.on_setting(self.option, get_settings(self).get(self.option))
        get_settings(self).add_listener(self)

    def on_destroy(self):
        get_settings(self).remove_listener(self)
        super().on_destroy()

    def on_setting(self, option, value):
        if option == self.option:
            color = Color.from_hex(value)
            if color != self.color:
                self.color = color
                self.refresh()
                # self.set_background_color(color)

    def on_paint(self):
        ww, wh = self.size()
        dc = self.create_dc()
        dc.draw_rectangle(1, 1, ww - 2, wh - 2, self.color)
        dc.draw_line(0, 0, ww, 0, self.bordercolor)
        dc.draw_line(ww - 1, 0, ww - 1, wh, self.bordercolor)
        dc.draw_line(0, wh - 1, ww, wh - 1, self.bordercolor)
        dc.draw_line(0, 0, 0, wh, self.bordercolor)

        # dc.draw_line(1, 0, ww - 2, 0, self.bordercolor)
        # dc.draw_line(ww - 1, 1, ww - 1, wh - 2, self.bordercolor)
        # dc.draw_line(1, wh - 1, ww - 2, wh - 1, self.bordercolor)
        # dc.draw_line(0, 1, 0, wh - 2, self.bordercolor)

        # dc.draw_point(0, 0, 0, 0, self.cornercolor)


class ColorSettingButton(IconButton):
    def __init__(self, parent, option):
        super().__init__(parent, "16x16/information.png")
        self.option = option
        self.dialog = None

    def on_activate(self):
        if self.dialog is not None:
            self.dialog.raise_()
            self.dialog.activateWindow()
            return
        from fsui.qt import QColorDialog

        # FIXME: Use accessor funtion get_qwindow
        # print("Initial color", Color.from_hex(get_settings(self).get(self.option)))
        # dialog = QColorDialog(
        #     Color.from_hex(get_settings(self).get(self.option)),
        #     parent=get_window(self)._real_window,
        # )
        self.dialog = QColorDialog(parent=get_window(self)._qwidget)

        # dialog.setOption(QColorDialog.ShowAlphaChannel)
        self.dialog.setOption(QColorDialog.NoButtons)
        self.dialog.setOption(QColorDialog.DontUseNativeDialog)
        # Setting initial color only seems to work after setting options.
        # Calling this method earlier (or setting initial color in constructor)
        # seems to be ignored causing black color to be pre-selected.
        self.dialog.setCurrentColor(
            Color.from_hex(get_settings(self).get(self.option))
        )
        # dialog.colorSelected.connect(self.__color_selected)
        self.dialog.currentColorChanged.connect(self.__current_color_changed)
        self.dialog.destroyed.connect(self.__dialog_destroyed)

        # self.dialog.setAttribute(Qt.WA_DeleteOnClose)
        self.dialog.installEventFilter(self)
        self.dialog.show()

    def eventFilter(self, obj, event):
        if obj == self.dialog:
            # print("-")
            from fsui.qt import QEvent

            # print("eventFilter", obj, event, event.type(), QEvent.Close)
            if event.type() == QEvent.Close:
                print("----")
                print("Dialog Window closed")
                print("----")
                self.dialog.destroy()
                self.dialog = None
        return super().eventFilter(obj, event)

    def __dialog_destroyed(self):
        # FIXME: We don't get the destroyed event??
        print("QColorDialog was destroyed")
        self.dialog = None

    # def __color_selected(self, color):
    #     get_settings(self).set(self.option, Color(color).to_hex())

    def __current_color_changed(self, color):
        get_settings(self).set(self.option, Color(color).to_hex())


class ColorTextField(TextField):
    def __init__(self, parent, option):
        text = get_settings(self).get(option)
        super().__init__(parent, text)
        self.option = option
        self.set_min_width(100)
        get_settings(self).add_listener(self)

    def on_destroy(self):
        get_settings(self).remove_listener(self)
        super().on_destroy()

    def on_setting(self, option, value):
        if option == self.option:
            if value != self.text():
                self.set_text(value)

    def on_changed(self):
        value = self.text().strip()
        get_settings(self).set(self.option, value)


class ColorSettingGroup(Group):
    def __init__(self, parent, option):
        super().__init__(parent)
        self.option = option
        self.layout = HorizontalLayout()
        self.layout.add(ColorSettingIndicator(self, option))
        self.layout.add(ColorTextField(self, option), margin_left=5)
        self.layout.add(ColorSettingButton(self, option), margin_left=5)


class AppearancePrefsPanel(BasePrefsPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.set_min_size((500, 400))
        self.layout.set_padding(20, 20, 20, 20)

        label = Label(self, "Titlebar font:")
        self.layout.add(label, fill=True)

        # FIXME: Text field is not updated when font changes (easy to check)
        # with reset to defaults function.
        # Same applies to Option UI stuff actually
        self.textfield = TextField(
            self,
            get_settings(self).get("launcher_titlebar_font"),
            # FIXME: Show real default text here!
            placeholder="Saira Condensed 16",
        )
        self.textfield.changed.connect(self.__titlebar_font_changed)
        self.layout.add(self.textfield, fill=True, margin_top=10)

        label = Label(self, "Titlebar foreground color:")
        self.layout.add(label, fill=True, margin_top=10)
        self.layout.add(
            ColorSettingGroup(self, "launcher_titlebar_fgcolor"), margin_top=10
        )

        label = Label(self, "Titlebar foreground color (inactive):")
        self.layout.add(label, fill=True, margin_top=10)
        self.layout.add(
            ColorSettingGroup(self, "launcher_titlebar_fgcolor_inactive"),
            margin_top=10,
        )

        label = Label(self, "Titlebar background color:")
        self.layout.add(label, fill=True, margin_top=10)
        self.layout.add(
            ColorSettingGroup(self, "launcher_titlebar_bgcolor"), margin_top=10
        )

        # self.layout.add(
        #     ColorSettingIndicator(self, "launcher_titlebar_bgcolor")
        # )
        # self.layout.add(ColorSettingButton(self, "launcher_titlebar_bgcolor"))

        label = Label(self, "Titlebar background (inactive):")
        self.layout.add(label, fill=True, margin_top=10)
        self.layout.add(
            ColorSettingGroup(self, "launcher_titlebar_bgcolor_inactive"),
            margin_top=10,
        )

        from launcher.settings.option_ui import OptionUI

        self.add_option(Option.LAUNCHER_WINDOW_TITLE)
        self.add_option(Option.LAUNCHER_TITLEBAR_HEIGHT)
        self.add_option(Option.LAUNCHER_TITLEBAR_UPPERCASE)

        # self.layout.add(
        #     OptionUI.create_group(self, Option.LAUNCHER_TITLEBAR_HEIGHT),
        #     fill=True,
        #     margin_top=10,
        # )
        # from launcher.settings.option_ui import OptionUI
        # self.layout.add(
        #     OptionUI.create_group(self, Option.LAUNCHER_TITLEBAR_UPPERCASE),
        #     fill=True,
        #     margin_top=10,
        # )

        # self.add_option(Option.LAUNCHER_THEME)
        # self.add_option(Option.LAUNCHER_FONT_SIZE)
        # self.add_option(Option.LAUNCHER_CLOSE_BUTTONS)

        self.layout.add(
            DefaultPrefsButton(
                self,
                options=[
                    "launcher_titlebar_bgcolor",
                    "launcher_titlebar_bgcolor_inactive",
                    "launcher_titlebar_fgcolor",
                    "launcher_titlebar_fgcolor_inactive",
                    "launcher_titlebar_font",
                    Option.LAUNCHER_TITLEBAR_HEIGHT,
                    Option.LAUNCHER_TITLEBAR_UPPERCASE,
                    "launcher_window_bgcolor",
                    Option.LAUNCHER_WINDOW_TITLE,
                ],
            ),
            margin_top=20,
        )

    def __titlebar_font_changed(self):
        get_settings(self).set(
            "launcher_titlebar_font", self.textfield.text().strip()
        )
        # get_settings(self).set(
        #     "launcher_titlebar_bgcolor", self.textfield.text().strip()
        # )
