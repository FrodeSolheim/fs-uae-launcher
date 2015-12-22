import fsui
from fs_uae_launcher.res import gettext
from fs_uae_launcher.Settings import Settings
from fs_uae_launcher.ui.settings.settings_page import SettingsPage


class LanguageSettingsPage(SettingsPage):

    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("language-settings", "pkg:fs_uae_workspace")
        title = gettext("Appearance")
        subtitle = gettext("Set language and look for FS-UAE applications")
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

        self.add_section("FS-UAE Launcher")

        self.add_option("launcher_theme")
        self.add_option("launcher_font_size")

    def __del__(self):
        print("LanguageWindow.__del__")


class LanguageSettingChoice(fsui.Choice):

    def __init__(self, parent):
        fsui.Choice.__init__(self, parent)
        # FIXME: include in () what language is currently the automatic one

        selected_language = Settings.get("language")
        k = 0
        selected_index = 0
        for label, language_key, icon_name in LANGUAGE_ITEMS:
            self.add_item(label, fsui.Image(
                "fs_uae_workspace:res/16/flag-{0}.png".format(icon_name)))
            if language_key == selected_language:
                selected_index = k
            k += 1
        if selected_index > 0:
            self.set_index(selected_index)

        self.item_selected.connect(self.__item_changed)

    def __item_changed(self, index):
        Settings.set("language", LANGUAGE_ITEMS[index][1])


LANGUAGE_ITEMS = [
    # language name, language code, country flag code
    (gettext("Automatic"), "", "unknown"),
    ("Čeština", "cs", "cz"),
    ("Dansk", "da", "dk"),
    ("Deutsch", "de", "de"),
    ("English", "en", "gb"),
    ("Español", "es", "es"),
    ("Français", "fr", "fr"),
    ("Eλληνικά", "el", "gr"),  # greek
    ("Italiano", "it", "it"),
    ("Norsk (bokmål)", "nb", "no"),
    ("Polski", "pl", "pl"),
    ("Português", "pt", "pt"),
    ("Srpski", "sr", "rs"),  # srpski or српски
    ("Svensk", "sv", "se"),
    ("Suomi", "fi", "fi"),
    ("Türkçe", "tr", "tr"),
]
