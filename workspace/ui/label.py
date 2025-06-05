import fsui
from fsui.qt import QFont


class Label(fsui.Label):
    def __init__(self, parent, text="", font=None):
        super().__init__(parent, text)
        if font is not None:
            if isinstance(font, str):
                size, weight, family = font.split(" ", 3)
                assert size.endswith("px")
                font = QFont(family)
                font.setPixelSize(int(size[:-2]))
                weight = weight.lower()
                if weight == "regular":
                    font.setWeight(QFont.Weight.Normal)
                elif weight == "medium":
                    font.setWeight(QFont.Weight.DemiBold)
                elif weight == "bold":
                    font.setWeight(QFont.Weight.DemiBold)
                else:
                    raise Exception("Unknown weight")
                font = fsui.Font(font)

            self.set_font(font)


class MultiLineLabel(fsui.MultiLineLabel):
    pass
