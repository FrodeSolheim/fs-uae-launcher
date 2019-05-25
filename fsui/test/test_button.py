import fsui as fsui
from .WidgetTestCase import WidgetTestCase


class TestButton(WidgetTestCase):
    def test_button(self):
        self.setup_dialog()
        button = fsui.Button(self.dialog)
        button.disable()
        button.enable()
        button.enable(False)
        button.enable(True)
        self.run_dialog()

    def test_button_with_label(self):
        self.setup_dialog()
        fsui.Button(self.dialog, "With Label")
        self.run_dialog()
