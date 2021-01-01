from fsui import Button, HorizontalLayout, Label, TextField
from launcher.system.classes.window import Window
from launcher.system.classes.windowresizehandle import WindowResizeHandle


class CalculatorWindow(Window):
    def __init__(self, parent):
        super().__init__(parent, title="Calculator", maximizable=False)

        self.text_field = CalculatorTextField(self)
        self.layout.add(self.text_field, fill=True, margin=20)

        hori_layout = HorizontalLayout()
        self.layout.add(
            hori_layout,
            fill=True,
            margin_top=0,
            margin_right=20,
            margin_left=10,
            margin_bottom=10,
        )
        button = CalculatorButton(self, "7")
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "8")
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "7")
        hori_layout.add(button, margin_left=10)
        # CA and CE buttons use a smaller font on purpose, to make them look
        # more like symbols.
        button = CalculatorButton(self, "CA", letters=True)
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "CE", letters=True)
        hori_layout.add(button, margin_left=10)

        hori_layout = HorizontalLayout()
        self.layout.add(
            hori_layout,
            fill=True,
            margin_top=0,
            margin_right=20,
            margin_left=10,
            margin_bottom=10,
        )
        button = CalculatorButton(self, "4")
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "5")
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "6")
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "×", symbol=True)
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "÷", symbol=True)
        hori_layout.add(button, margin_left=10)

        hori_layout = HorizontalLayout()
        self.layout.add(
            hori_layout,
            fill=True,
            margin_top=0,
            margin_right=20,
            margin_left=10,
            margin_bottom=10,
        )
        button = CalculatorButton(self, "1")
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "2")
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "3")
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "+", symbol=True)
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "\u2212", symbol=True)  # Minus sign
        hori_layout.add(button, margin_left=10)

        hori_layout = HorizontalLayout()
        self.layout.add(
            hori_layout,
            fill=True,
            margin_top=0,
            margin_right=20,
            margin_left=10,
            margin_bottom=10,
        )
        button = CalculatorButton(self, "0")
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, ".")
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "«", symbol=True)
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "±", symbol=True)
        hori_layout.add(button, margin_left=10)
        button = CalculatorButton(self, "=", symbol=True)
        hori_layout.add(button, margin_left=10)

        self.layout.add_spacer(10)

        # WindowResizeHandle(self)


class CalculatorButton(Button):
    def __init__(self, parent, text, letters=False, symbol=False):
        super().__init__(parent, text)
        self.set_min_width(48)
        self.set_min_height(32)
        if letters:
            font_size = 15
        elif symbol:
            font_size = 20
        else:
            font_size = 18
        if font_size is not None:
            self.set_font(self.font().set_size(font_size))
        # FIXME: Fixed-width font for button labels?
        # self.set_font(self.font().set_size(font_size))


class CalculatorTextField(TextField):
    def __init__(self, parent):
        super().__init__(parent, text="Not implemented yet!", read_only=True)
        # FIXME: Right-align text
        # FIXME: Fixed-width font
        # self.set_font(self.font().set_size(20))
