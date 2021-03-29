from launcher.fswidgets2.button import Button
from launcher.fswidgets2.flexcontainer import (
    FlexContainer,
    Style,
    VerticalFlexContainer,
)
from launcher.fswidgets2.flexlayout import FlexLayout
from launcher.fswidgets2.parentstack import ParentStack
from launcher.fswidgets2.window import Window
from launcher.i18n import gettext
from system.classes.windowresizehandle import WindowResizeHandle


class FlexboxTestWindow(Window):
    def __init__(self, parent=None):
        ParentStack.push(self)

        super().__init__(
            title=gettext("Flexbox test window"), style={"display": "flex"}
        )

        # OpenRetroPrefsPanel()
        # with VerticalFlexContainer():
        #     OpenRetroPrefsPanel()

        # with VerticalFlexContainer(self):

        with FlexContainer(
            style={
                "backgroundColor": "#ffcccc",
                "flexDirection": "column",
                "padding": 10,
                "width": 640,
                # "height": 480,
            }
        ):
            Button(label="A", style={"alignSelf": "flex-start"})
            Button(label="B", style={"alignSelf": "center"})
            Button(label="C", style={"alignSelf": "flex-end"})

        # with FlexContainer(style={
        #     "backgroundColor": "#ffcccc",
        #     "paddingLeft": 10,
        #     "paddingRight": 10,
        # }):
        #     Button(label="A")
        #     Button(label="B")

        # with FlexContainer(style={
        #     "backgroundColor": "#ffcccc",
        #     "paddingLeft": 10,
        #     "paddingRight": 10,
        # }):
        #     Button(label="A")
        #     Button(label="B")
        #     Button(label="C")

        # with FlexContainer(style={
        #     "paddingLeft": 10,
        # }):
        #     Button(label="A")
        #     Button(label="B")
        #     Button(label="C")
        #     Button(label="D")

        with VerticalFlexContainer(
            style={
                "backgroundColor": "#ccffcc",
                "padding": 10,
            }
        ):
            Button(
                label="D is a button with a really long label",
                style={"marginBottom": 10},
            )
            Button(
                label="E",
                style={
                    "marginBottom": 10,
                    "marginLeft": 20,
                    "marginRight": 10,
                },
            )
            Button(label="F")
            # Button(label="C", style={"flexGrow": 1})

        with FlexContainer(
            style={
                "backgroundColor": "#ccccff",
                "flexGrow": 1,
                "padding": 10,
            }
        ):
            Button(label="G", style={"flexGrow": 1})
            Button(
                label="H is much longer than both G and I",
                style={"flexGrow": 1},
            )
            Button(label="I")

        with FlexContainer(
            style={
                "backgroundColor": "#ffcccc",
                "padding": 10,
            }
        ):
            Button(
                label="J has a really long label, let's see what happens if we try to cut it off",
                style={"flexGrow": 1, "maxWidth": 200},
            )
            Button(label="K (longer)", style={"flexGrow": 1})
            Button(label="L", style={"flexGrow": 1})

        with FlexContainer(
            style={
                "backgroundColor": "#ccffcc",
                "padding": 10,
            }
        ):
            Button(label="M", style={"height": 100})
            Button(label="N")
            Button(label="O", style={"maxHeight": 50})
            with VerticalFlexContainer(
                style={
                    "backgroundColor": "#ccffcc",
                    "padding": 10,
                }
            ):
                Button(
                    label="D is a button with a really long label",
                    style={"marginBottom": 10},
                )
                Button(
                    label="E",
                    style={
                        "marginBottom": 10,
                        "marginLeft": 20,
                        "marginRight": 10,
                    },
                )
                Button(label="F")
            Button(
                label="Big",
                style={"flexGrow": 1, "margin": -10, "marginLeft": 0},
            )

        with FlexContainer(
            style={
                "backgroundColor": "#ccccff",
                "padding": 10,
            }
        ):
            Button(label="P", style={"margin": 10})
            Button(label="Q", style={"margin": 20})
            Button(label="R", style={"margin": 30})
            Button(label="P", style={"height": 30, "margin": 10})
            Button(label="Q", style={"height": 30, "margin": 20})
            Button(label="R", style={"height": 30, "margin": 30})

        # with FlexContainer(style={
        #     "backgroundColor": "#ccccff",
        #     "padding": 10,
        # }):

        with FlexContainer(
            style={
                "backgroundColor": "#ffcccc",
            }
        ):
            Button(
                label="S", style={"flexGrow": 1, "height": 30, "margin": 10}
            )
            Button(
                label="T", style={"flexGrow": 1, "height": 30, "margin": 20}
            )
            Button(
                label="U", style={"flexGrow": 1, "height": 30, "margin": 30}
            )

        with FlexContainer(
            style={
                "alignItems": "center",
                "backgroundColor": "#ccffcc",
                "height": 100,
                "padding": 10,
            }
        ):
            Button(
                label="v", style={"flexGrow": 1, "height": 30, "margin": 10}
            )
            Button(
                label="W",
                style={
                    "flexGrow": 1,
                    "height": 30,
                    "margin": 10,
                    "marginBottom": 60,
                },
            )
            Button(
                label="X",
                style={
                    "flexGrow": 1,
                    "height": 30,
                    "margin": 10,
                    "marginRight": 150,
                    "marginBottom": 110,
                },
            )
            pass

        # with VerticalFlexContainer(style={
        #     "backgroundColor": "#00ff00",
        #     "paddingLeft": 10,
        #     "paddingRight": 10,
        # }):
        #     Button(label="D")
        #     Button(label="E", style={
        #         "alignSelf": "flex-start"
        #     })
        #     Button(label="E", style={
        #         "alignSelf": "center"
        #     })
        #     Button(label="F", style={
        #         "alignSelf": "flex-end"
        #     })

        with InsertWidgetTest():
            Button(label="B")

        assert ParentStack.pop() == self

        WindowResizeHandle(self)


class InsertWidgetTest(FlexContainer):
    def __init__(self):
        super().__init__()
        ParentStack.push(self)
        Button(label="A")
        Button(label="C")
        # Allow next item(s) to be inserted between A and C
        self.layout.insert_index = 1
        assert ParentStack.pop() == self
