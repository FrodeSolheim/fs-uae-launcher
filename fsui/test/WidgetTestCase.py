import unittest
import fsui as fsui


class WidgetTestCase(unittest.TestCase):

    # noinspection PyPep8Naming
    def __init__(self, methodName="runTest"):
        unittest.TestCase.__init__(self, methodName=methodName)
        self.dialog = None

    def setup_dialog(self):
        self.dialog = fsui.LegacyDialog()

    def run_dialog(self):
        def run_in_dialog():
            self.dialog.end_modal(True)

        fsui.call_after(run_in_dialog)
        self.dialog.show_modal()
        self.dialog.destroy()
