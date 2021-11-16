from fswidgets.button import Button
from fswidgets.decorators import constructor
from fswidgets.flexcontainer import FlexContainer
from fswidgets.overrides import overrides
from fswidgets.style import Style
from fswidgets.text import Text
from fswidgets.widget import Widget
from launcher.context import useTranslation
from system.utilities.updater import Updater


class UpdatesAvailablePanel(FlexContainer):
    """Dismissable panel for displaying update notification.

    The panel automatically resizes itself and positions itself in the
    lower-right corner of the parent widget.
    """

    @constructor
    def __init__(self, parent: Widget):
        super().__init__(
            parent, style=Style(backgroundColor="#CCCC88", padding=20)
        )

        t = useTranslation()

        Text(t("Updates are available"))
        Button(
            t("Show"),
            onClick=self.onShowClicked,
            style=Style(marginLeft=20),
        )
        Button(
            t("Dismiss"),
            onClick=self.onDismissClicked,
            style=Style(marginLeft=10),
        )

        self.updatePositionAndSize()
        self.getParent().addResizeListener(self.onParentResized)

    @overrides
    def onDestroy(self):
        self.getParent().removeResizeListener(self.onParentResized)

    def onDismissClicked(self):
        self.hide()

    def onParentResized(self):
        self.updatePositionAndSize()

    def onShowClicked(self):
        Updater.openFrom(self.getWindow())

    def updatePositionAndSize(self):
        parentSize = self.getParent().getSize()
        size = self.getMinSize()
        self.setPositionAndSize(
            (parentSize[0] - size[0], parentSize[1] - size[1]), size
        )
