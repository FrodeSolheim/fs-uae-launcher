import fsui
from fsui import Color, Font
from fsui.qt import QColor, QFont, QPalette, QStyleFactory
from fsui.theme import Padding
from fsui.theme import Theme as BaseTheme
from launcher.launcher_settings import LauncherSettings


def set_colors(
    palette: QPalette, role, normal: QColor, disabled: QColor = None
):
    palette.setColor(role, QColor(normal))
    palette.setColor(QPalette.Disabled, role, QColor(disabled))


def initialize_qt_style(qapplication, theme):
    print("Available QT styles:", QStyleFactory.keys())
    qapplication.setStyle(QStyleFactory.create("Fusion"))

    pa = QPalette()
    # background = QColor("#f6f5f4")
    # color = fsui.Color(0xAEAEAE).lighten(0.065)
    color = fsui.Color(0xAEAEAE).lighten(0.05)
    background = QColor(color.to_hex())

    text = "#000000"
    text_disabled = "#777777"

    pa.setColor(QPalette.Window, background)
    pa.setColor(QPalette.AlternateBase, background)
    pa.setColor(QPalette.Button, background)

    pa.setColor(QPalette.Highlight, QColor(0x66, 0x88, 0xBB))

    set_colors(pa, QPalette.Base, "#E8E8E8", "#C0C0C0")

    set_colors(pa, QPalette.Text, text, text_disabled)
    set_colors(pa, QPalette.WindowText, text, text_disabled)
    set_colors(pa, QPalette.ButtonText, text, text_disabled)

    # pa.setColor(QPalette.Base, QColor(0xE8, 0xE8, 0xE8))
    # pa.setColor(QPalette.Disabled, QPalette.Base, QColor(0xC0, 0xC0, 0xC0))

    # pa.setColor(QPalette.Text, QColor(0xFF, 0x00, 0x00))
    # pa.setColor(QPalette.Disabled, QPalette.Text, QColor(0xFF, 0x00, 0x00))

    # Labels

    # pa.setColor(QPalette.WindowText, QColor(0x00, 0xFF, 0x00))
    # pa.setColor(
    #     QPalette.Disabled, QPalette.WindowText, QColor(0x00, 0x88, 0x00)
    # )

    # Buttons
    # pa.setColor(QPalette.ButtonText, QColor(0x00, 0xFF, 0x00))
    # pa.setColor(
    #     QPalette.Disabled, QPalette.ButtonText, QColor(0x00, 0x88, 0x00)
    # )

    # pa.setColor(QPalette.Base, QColor(0xEE, 0xEE, 0xEE))
    # pa.setColor(QPalette.Base, QColor(0xFF, 0xFF, 0xFF))
    # pa.setColor(QPalette.Disabled, QPalette.Text, QColor(0x66, 0x66, 0x66))

    # pa.setColor(QPalette.Mid, QColor(0xFF, 0x00, 0x00))

    # pa.setColor(QPalette.Window, QColor("#aeaeae"))
    # pa.setColor(QPalette.AlternateBase, QColor("#aeaeae"))
    # pa.setColor(QPalette.Button, QColor("#aeaeae"))

    qapplication.setPalette(pa)

    # pa.setColor(QPalette.Window, QColor(0x50, 0x50, 0x50))
    # pa.setColor(QPalette.WindowText, Qt.white)
    # pa.setColor(QPalette.Base, QColor(25, 25, 25))
    # pa.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    # pa.setColor(QPalette.ToolTipBase, Qt.white)
    # pa.setColor(QPalette.ToolTipText, Qt.white)
    # pa.setColor(QPalette.Text, Qt.white)
    # pa.setColor(QPalette.Button, QColor(0x58, 0x58, 0x58))
    # pa.setColor(QPalette.ButtonText, Qt.white)
    # pa.setColor(QPalette.BrightText, Qt.red)
    # pa.setColor(QPalette.Link, QColor(42, 130, 218))
    # pa.setColor(QPalette.Highlight, QColor(255, 0, 0))
    # pa.setColor(QPalette.HighlightedText, Qt.black)
    # qapplication.setPalette(pa)

    # Choice::
    #     QStandardItemModel::
    #     QComboBoxPrivateContainer::
    #         QBoxLayout::
    #         QComboBoxListView::
    #             QWidget::qt_scrollarea_viewport
    #             QWidget::qt_scrollarea_hcontainer
    #                 QScrollBar::
    #                 QBoxLayout::
    #             QWidget::qt_scrollarea_vcontainer
    #                 QScrollBar::
    #                 QBoxLayout::
    #             QItemSelectionModel::
    #             QComboMenuDelegate::
    #         QComboBoxPrivateScroller::
    #         QComboBoxPrivateScroller::

    # FIXME: Make stylesheet use scaling function for numbers

    qapplication.setStyleSheet(
        f"""
        QToolTip {{
            background-color: #efe4ab;
            border: 1px solid #958a62;
            padding-top: 4px;
            padding-right: 8px;
            padding-bottom: 4px;
            padding-left: 8px;
            padding: 0px;
            padding-top: 2px;
            padding-right: 4px;
            padding-bottom: 2px;
            padding-left: 4px;
/*
            color: #FFFFFF; background-color: #2A82DA;
            border: 1px solid white;
*/
        }}
        QPushButton {{
            padding-right: 12px;
            padding-left: 12px;
        }}
        QPushButton:disabled {{
            color: #777777;
        }}
        /*
        QLineEdit {{
            padding-top: {theme.textfield_padding().top}px;
            padding-right: {theme.textfield_padding().right}px;
            padding-left: {theme.textfield_padding().left}px;
            padding-bottom: {theme.textfield_padding().bottom}px;
        }}
        */
        /* Placeholder text. It will be made partially transparent by Qt */
        /* FIXME: This only works when initially showing the widget :( */
        /* TODO: Move color logic to fsui.TextField instead then... :( */
        /* DONE! */
        /*
        QLineEdit[text=""] {{
            color: #660000;
        }}
        QLineEdit[text!=""] {{
            color: #000000;
        }}
        */
        /*
        QSpinBox {{
            padding-top: 2px;
            padding-bottom: 2px;

            padding-right: 4px;
            padding-left: 4px;
        }}
        */
        QCheckBox {{
            spacing: 5px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        """
    )

    # try:
    #     launcher_font_size = int(
    #         Settings.instance().get("launcher_font_size")
    #     )
    # except ValueError:
    #     if fusion_variant == "fws":
    #         launcher_font_size = 13
    #     else:
    #         launcher_font_size = 0
    # if launcher_font_size:
    #     print("FONT: Override size {}".format(launcher_font_size))

    # font.setPointSize(launcher_font_size)
    # if fusion_variant == "fws":
    #     font = QFont("Roboto")
    #     font.setPointSizeF(10.5)
    #     font.setHintingPreference(QFont.PreferNoHinting)
    # font.setHintingPreference(QFont.PreferNoHinting)

    # font = QFont("Saira Condensed", 16, QFont.Medium)
    font = QFont("Roboto", 15, QFont.Normal)
    font.setPixelSize(15)
    qapplication.setFont(font)


class Theme(BaseTheme):
    def __init__(self):
        super().__init__()

        # self._titlebar_bgcolor = fsui.Color(0x888888)
        # self._titlebar_bgcolor_inactive = fsui.Color(0x999999)

        # self.__titlebar_bgcolor_text = "0x6688BB"
        # self._titlebar_bgcolor = Color.from_hex(
        #     self._default_titlebar_bgcolor_text
        # )

        # self._default_titlebar_bgcolor_inactive = fsui.Color(0x888888)

        black = Color(0, 0, 0)

        self._titlebar_bgcolor_default_str = "#6688BB"
        self._titlebar_bgcolor_inactive_default_str = "#888888"
        self._titlebar_fgcolor_default_str = "#000000"
        self._titlebar_fgcolor_inactive_default_str = "#444444"
        # self._window_bgcolor_default_str = "#AEAEAE"
        self._window_bgcolor_default_str = "#AAAAAA"

        self._titlebar_bgcolor = black
        self._titlebar_bgcolor_inactive = black
        self._titlebar_fgcolor = black
        self._titlebar_fgcolor_inactive = black
        self._window_bgcolor = black

        # self._titlebar_bgcolor = fsui.Color(0x6688BB)
        # self._titlebar_bgcolor_inactive = fsui.Color(0x888888)

        self._titlebar_font_default_str = "Saira Condensed Semi-Bold 19"
        # FIXME: Just set some default font here?
        self._titlebar_font = fsui.Font(
            **Font.parse("self._titlebar_font_default_str")
        )

        self._titlebar_height_default_str = "40"
        self._titlebar_height = 40

        self._titlebar_uppercase_default_str = "1"
        self._titlebar_uppercase = True

        self._button_padding = Padding()
        self._button_padding.top = 3
        self._button_padding.bottom = 3
        self._choice_padding = Padding()
        self._choice_padding.top = 3
        self._choice_padding.bottom = 3
        self._textfield_padding = Padding()
        self._textfield_padding.top = 3
        self._textfield_padding.right = 4
        self._textfield_padding.bottom = 3
        self._textfield_padding.left = 4

        self.settings = LauncherSettings
        self.settings.add_listener(self)
        for option in (
            "launcher_titlebar_bgcolor",
            "launcher_titlebar_bgcolor_inactive",
            "launcher_titlebar_fgcolor",
            "launcher_titlebar_fgcolor_inactive",
            "launcher_titlebar_font",
            "launcher_titlebar_height",
            "launcher_titlebar_uppercase",
            "launcher_window_bgcolor",
        ):
            self.on_setting(option, self.settings.get(option))

    def button_padding(self):
        return self._button_padding

    def choice_padding(self):
        return self._choice_padding

    def textfield_padding(self):
        return self._textfield_padding

    def titlebar_bgcolor(self):
        return self._titlebar_bgcolor

    def titlebar_bgcolor_inactive(self):
        return self._titlebar_bgcolor_inactive

    def titlebar_fgcolor(self):
        return self._titlebar_fgcolor

    def titlebar_fgcolor_inactive(self):
        return self._titlebar_fgcolor_inactive

    def titlebar_font(self):
        return self._titlebar_font

    def titlebar_height(self):
        return self._titlebar_height

    def titlebar_system(self):
        return False

    def titlebar_uppercase(self):
        return self._titlebar_uppercase

    def window_bgcolor(self):
        return self._window_bgcolor

    def _update_color(self, name, value):
        # if name == "window_bgcolor"
        # print("_")
        color = None
        if value and value != "#00000000":
            try:
                color = Color.from_hex(value)
            except Exception:
                pass
        if color is None:
            color = Color.from_hex(getattr(self, f"_{name}_default_str"))
        print("Setting", name, "->", color)
        setattr(self, f"_{name}", color)

    def _update_font(self, name, value):
        font = None
        if value:
            font_values = Font.parse(value)
            try:
                font = Font(**font_values)
            except Exception:  # FIXME: Less broad exception
                print("Not a valid font")
        if font is None:
            value = getattr(self, f"_{name}_default_str")
            font_values = Font.parse(value)
            font = Font(**font_values)
        print("Setting", name, "->", font)
        # FIXME: Compare font once more?
        setattr(self, f"_{name}", font)

        # if not value:
        #     font_values = Font.parse()
        # else:
        #     font_values = Font.parse(value)
        # if font_values != getattr(self, name).describe():
        #     setattr(self, name, font)
        #     print("Font changed, setting new font", font_values)

    def on_setting(self, option, value):
        if option == "launcher_titlebar_bgcolor":
            self._update_color("titlebar_bgcolor", value)

        elif option == "launcher_titlebar_bgcolor_inactive":
            print("- Theme << launcher_titlebar_bgcolor_inactive")
            self._update_color("titlebar_bgcolor_inactive", value)

        elif option == "launcher_titlebar_fgcolor":
            self._update_color("titlebar_fgcolor", value)

        elif option == "launcher_titlebar_fgcolor_inactive":
            self._update_color("titlebar_fgcolor_inactive", value)

        elif option == "launcher_titlebar_font":
            self._update_font("titlebar_font", value)

        elif option == "launcher_titlebar_height":
            try:
                height = int(value)
            except ValueError:
                height = 0
            if not height:
                height = int(self._titlebar_height_default_str)
            if height != self._titlebar_height:
                self._titlebar_height = height

        elif option == "launcher_titlebar_uppercase":
            if not value:
                value = self._titlebar_uppercase_default_str
            if value.lower() in ["0", "false"]:
                uppercase = False
            else:
                uppercase = True
            if uppercase != self._titlebar_uppercase:
                self._titlebar_uppercase = uppercase

        elif option == "launcher_window_bgcolor":
            self._update_color("window_bgcolor", value)
