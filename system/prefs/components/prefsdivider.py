from launcher.fswidgets2.panel import Panel


class PrefsDivider(Panel):
    def __init__(self):
        super().__init__(
            style={
                "backgroundColor": "#999999",
                "height": 1,
                "margin": 10,
            }
        )
