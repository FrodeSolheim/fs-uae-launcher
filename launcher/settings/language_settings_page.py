import fsui
from fswidgets.widget import Widget
from launcher.launcher_settings import LauncherSettings
from launcher.res import gettext
from launcher.settings.settings_page import SettingsPage
from system.prefs.components.notworking import PrefsNotWorkingWarningPanel


class LanguageSettingsPage(SettingsPage):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        # icon = fsui.Icon("language-settings", "pkg:workspace")
        # title = gettext("Language")
        # subtitle = gettext("Set language for FS-UAE applications")
        # self.add_header(icon, title, subtitle)

        PrefsNotWorkingWarningPanel(parent=self)
        self.layout.add_spacer(20)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        # hori_layout.add(fsui.Label(self, gettext("Language:")))
        hori_layout.add(fsui.Label(self, gettext("Language:")))
        hori_layout.add_spacer(0, expand=True)
        self.language_choice = LanguageSettingChoice(self)
        hori_layout.add(self.language_choice)

        self.layout.add_spacer(20)

        information = ""
        # information = gettext(
        #     "A change of language will only affect applications "
        #     "which are restarted after the change.")
        # information += "\n\n"
        information += gettext(
            "When Automatic is specified, your preferred language is set "
            "based on information from the operating system (or English, "
            "if a supported language is not detected)."
        )
        self.layout.add(fsui.MultiLineLabel(self, information, 500))

        label = fsui.Label(
            self, "You can help translate FS-UAE on crowdin.net:"
        )
        self.layout.add(label, margin_top=20)
        label = fsui.URLLabel(
            self,
            "https://crowdin.com/project/fs-uae",
            "https://crowdin.com/project/fs-uae",
        )
        self.layout.add(label, margin_top=5)


class LanguageSettingChoice(fsui.Choice):
    def __init__(self, parent):
        fsui.Choice.__init__(self, parent)
        # FIXME: include in () what language is currently the automatic one

        selected_language = LauncherSettings.get("language")
        k = 0
        selected_index = 0
        for label, language_key, icon_name in getLanguageItems():
            self.add_item(
                label,
                fsui.Image(
                    "workspace:/data/16x16/flag-{0}.png".format(icon_name)
                ),
            )
            if language_key == selected_language:
                selected_index = k
            k += 1
        if selected_index > 0:
            self.set_index(selected_index)

    def on_changed(self):
        index = self.index()
        LauncherSettings.set("language", getLanguageItems()[index][1])


def getLanguageItems():
    return [
        # language name, language code, country flag code
        (gettext("Automatic"), "", "unknown"),
        ("Čeština", "cs", "cz"),
        ("Dansk", "da", "dk"),
        ("Deutsch", "de", "de"),
        ("English", "en", "gb"),
        ("Esperanto", "eo", "eo"),
        ("Español", "es", "es"),
        ("Français", "fr", "fr"),
        ("Eλληνικά", "el", "gr"),  # greek
        ("Italiano", "it", "it"),
        ("Magyar", "hu", "hu"),  # hungarian
        ("Nederlands", "nl", "nl"),
        ("Norsk (bokmål)", "nb", "no"),
        ("Polski", "pl", "pl"),
        ("Português", "pt", "pt"),
        ("Srpski", "sr", "rs"),  # srpski or српски
        ("Svensk", "sv", "se"),
        ("Suomi", "fi", "fi"),
        ("Türkçe", "tr", "tr"),
    ]
