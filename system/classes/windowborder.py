from fsui import Color
from fswidgets.overrides import overrides
from fswidgets.panel import Panel
from fswidgets.widget import Widget


class WindowBorder(Panel):
    def __init__(self, parent: Widget):
        super().__init__(parent, forceRealParent=True)
        # self.set_background_color(Color(0xCCD6E4))
        # self.set_background_color(Color(0x888888))
        # self.set_background_color(Color(0x777777))
        # self.set_background_color(Color(0x55729c))
        # self.set_background_color(Color(0x516c94))
        # self.set_background_color(Color(0x4c668c))
        self.borderColor = Color(0x516C94)
        self.borderInactiveColor = Color(0x707070)
        self.updateBackgroundColor()

    @overrides
    def onWindowFocusChanged(self):
        # print("WindowBorder.onWindowFocusChanged")
        self.updateBackgroundColor()

    def updateBackgroundColor(self):
        if self.isWindowFocused():
            color = self.borderColor
        else:
            color = self.borderInactiveColor
        self.setBackgroundColor(color)
