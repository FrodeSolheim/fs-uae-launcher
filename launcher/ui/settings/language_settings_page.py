import fsui
from launcher.launcher_settings import LauncherSettings
from launcher.res import gettext
from launcher.ui.settings.settings_page import SettingsPage


class LanguageSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("language-settings", "pkg:workspace")
        # gettext("Appearance")
        title = gettext("Language")
        # gettext("Set language and look for FS-UAE applications")
        subtitle = gettext("Set language for FS-UAE applications")
        self.add_header(icon, title, subtitle)

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
            "if a supported language is not detected).")
        self.layout.add(
            fsui.MultiLineLabel(self, information, 640))

        label = fsui.Label(
            self, "You can help translate FS-UAE on crowdin.net:")
        self.layout.add(label, margin_top=20)
        label = fsui.URLLabel(self, "https://crowdin.com/project/fs-uae",
                              "https://crowdin.com/project/fs-uae")
        self.layout.add(label, margin_top=5)


class LanguageSettingChoice(fsui.Choice):
    def __init__(self, parent):
        fsui.Choice.__init__(self, parent)
        # FIXME: include in () what language is currently the automatic one

        selected_language = LauncherSettings.get("language")
        k = 0
        selected_index = 0
        for label, language_key, icon_name in LANGUAGE_ITEMS:
            self.add_item(label, fsui.Image(
                "workspace:res/16x16/flag-{0}.png".format(icon_name)))
            if language_key == selected_language:
                selected_index = k
            k += 1
        if selected_index > 0:
            self.set_index(selected_index)

    def on_changed(self):
        index = self.get_index()
        LauncherSettings.set("language", LANGUAGE_ITEMS[index][1])


LANGUAGE_ITEMS = [
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
