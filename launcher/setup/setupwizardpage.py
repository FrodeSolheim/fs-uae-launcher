import fsui


class SetupWizardPage(fsui.Panel):

    WIDTH = 640
    HEIGHT = 400

    def __init__(self, parent):
        super().__init__(parent)
        self.set_min_width(SetupWizardPage.WIDTH)
        self.set_min_height(SetupWizardPage.HEIGHT)
