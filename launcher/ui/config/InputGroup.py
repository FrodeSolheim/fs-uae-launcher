import fsui
from .InputSelector import InputSelector
from ..IconButton import IconButton
from ...devicemanager import DeviceManager
from ...i18n import gettext


# FIXME: Superclass was Group, but changed to Panel due to not being able
# to disconnect from listening to config changes when closing window.
class InputGroup(fsui.Panel):
    def __init__(
        self,
        parent,
        autofire_button=True,
        refresh_button=False,
        parallel_ports=False,
        custom_ports=False,
    ):
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

        if refresh_button:
            self.refresh_button = IconButton(self, "refresh_button.png")
            self.refresh_button.set_tooltip(
                gettext("Refresh List of Connected Joystick Devices")
            )
            self.refresh_button.activated.connect(self.on_refresh_button)
            hori_layout.add(self.refresh_button, margin_right=10)

        self.layout.add_spacer(0)

        self.selectors = []
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

    # noinspection PyMethodMayBeStatic
    def on_refresh_button(self):
        DeviceManager.refresh()
