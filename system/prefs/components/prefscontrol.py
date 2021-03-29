from launcher.fswidgets2.flexcontainer import VerticalFlexContainer
from launcher.fswidgets2.parentstack import ParentStack
from launcher.fswidgets2.text import Text
from launcher.settings.option_ui import OptionUI


class PrefsControl(VerticalFlexContainer):
    def __init__(
        self,
        optionName: str,
        title: str = None,
        description: str = None,
        style=None,
    ):
        defaultStyle = {"padding": 10}
        if style is not None:
            defaultStyle.update(style)
        super().__init__(style=defaultStyle)
        parent = ParentStack.top()
        optionsOnPanel = None
        while parent and optionsOnPanel is None:
            parent = parent.getParent()
            optionsOnPanel = getattr(parent, "optionsOnPanel", None)
        if optionsOnPanel is not None:
            optionsOnPanel.add(optionName)
        with self:
            self.layout.add(
                OptionUI.create_group(
                    self,
                    optionName,
                    title,
                ),
            )
            if description is not None:
                Text(description, style={"marginTop": 10})
