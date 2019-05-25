import fsui
from launcher.i18n import gettext
from launcher.setup.setupwizardpage import SetupWizardPage
from launcher.setup.wizardheader import WizardHeader


class SetupWelcomePage(SetupWizardPage):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = fsui.VerticalLayout()

        header = WizardHeader(
            self, fsui.Icon("fs-uae-launcher", "pkg:launcher"), "Welcome"
        )
        self.layout.add(header, fill=True, margin_bottom=20)

        v_layout = fsui.VerticalLayout()
        self.layout.add(v_layout, margin=20)

        label = fsui.MultiLineLabel(
            self,
            gettext("Welcome to the setup wizard for FS-UAE Launcher!"),
            SetupWizardPage.WIDTH,
        )
        v_layout.add(label, fill=True, margin_top=0)

        label = fsui.MultiLineLabel(
            self,
            gettext(
                "You can close this wizard at any time if you do not want to "
                "use it, and you can also run it again later."
            ),
            SetupWizardPage.WIDTH,
        )
        v_layout.add(label, fill=True, margin_top=20)
