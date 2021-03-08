class Padding:
    def __init__(self):
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.left = 0


class Theme:
    def __init__(self):
        # self._titlebar_bgcolor = fsui.Color(0x888888)
        # self._titlebar_bgcolor_inactive = fsui.Color(0x999999)

        # self._titlebar_bgcolor = fsui.Color(0x6688BB)
        # self._titlebar_bgcolor_inactive = fsui.Color(0x888888)

        # self._titlebar_fgcolor = fsui.Color(0x000000)
        # self._titlebar_fgcolor_inactive = fsui.Color(0x222222)
        # self._titlebar_font = fsui.Font("Saira Condensed", 19, weight=600)

        self._window_bgcolor = None
        self._button_padding = None
        self._choice_padding = None
        self._textfield_padding = None

    def button_padding(self):
        return self._button_padding

    def choice_padding(self):
        return self._choice_padding

    def label_vertical_padding(self):
        return 4

    def textfield_padding(self):
        return self._textfield_padding

    # def titlebar_bgcolor(self):
    #     return self._titlebar_bgcolor

    # def titlebar_bgcolor_inactive(self):
    #     return self._titlebar_bgcolor_inactive

    # def titlebar_fgcolor(self):
    #     return self._titlebar_fgcolor

    # def titlebar_fgcolor_inactive(self):
    #     return self._titlebar_fgcolor_inactive

    # def titlebar_font(self):
    #     return self._titlebar_font

    # def titlebar_system(self):
    #     return False

    # def titlebar_uppercase(self):
    #     return True

    def window_bgcolor(self):
        return self._window_bgcolor
