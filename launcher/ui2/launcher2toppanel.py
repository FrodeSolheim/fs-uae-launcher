from fsui import HorizontalLayout, Panel
from launcher.panels.additionalconfigpanel import CustomConfigButton
from launcher.ui2.openretroeditbutton import OpenRetroEditButton
from launcher.ui2.ratingchoice import RatingChoice
from launcher.ui2.variantchoice import VariantChoice


class Launcher2TopPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        horilayout = HorizontalLayout()
        self.layout.add(
            horilayout,
            fill=True,
            expand=True,
            margin_top=10,
            margin_right=20,
            margin_bottom=10,
            margin_left=10,
        )
        # self.set_background_color(Color(0xC0C0C0))

        horilayout.add(
            VariantChoice(self), fill=True, expand=True, margin_left=10
        )
        horilayout.add(RatingChoice(self), fill=True, margin_left=10)
        horilayout.add(OpenRetroEditButton(self), fill=True, margin_left=10)
        horilayout.add(CustomConfigButton(self), fill=True, margin_left=10)

        # horilayout.add_spacer(10)
        # horilayout.add_spacer(20)
        # horilayout.add_spacer(52)

        # horilayout.add(VolumeButton(self), fill=True, margin_left=10)
        # horilayout.add(MonitorButton(self), fill=True, margin_left=10)
        # horilayout.add(FullscreenToggleButton(self), fill=True, margin_left=10)
        # horilayout.add(
        #     StartButton(self, dialog=False), fill=True, margin_left=10
        # )
