from typing import List

import fsui
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.ui.config.InputSelector import InputSelector


# FIXME: Superclass was Group, but changed to Panel due to not being able
# to disconnect from listening to config changes when closing window.
class InputGroup(fsui.Panel):
    def __init__(
        self,
        parent: Widget,
        autofire_button: bool = True,
        parallel_ports: bool = False,
        custom_ports: bool = False,
    ) -> None:
        super().__init__(parent)
        self.layout = fsui.VerticalLayout()

        if parallel_ports:
            heading = gettext("Parallel Port Joysticks")
        elif custom_ports:
            heading = gettext("Custom Joystick Port")
        else:
            heading = gettext("Joystick & Mouse Port")
            if False:
                # Keeping the old string here to keep the translations alive
                gettext("Joystick Ports")

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        heading_label = fsui.HeadingLabel(self, heading)
        hori_layout.add(heading_label, margin=10)
        hori_layout.add_spacer(0, expand=True)

        self.layout.add_spacer(0)

        self.selectors: List[InputSelector] = []
        offset = 0
        count = 2
        if parallel_ports:
            offset = 2
        elif custom_ports:
            offset = 4
            count = 1

        input_ports = [1, 0, 2, 3, 4]
        for i in input_ports[offset : offset + count]:
            # self.layout.add_spacer(10)
            selector = InputSelector(self, i, autofire_button=autofire_button)
            self.layout.add(selector, fill=True, margin=10)
