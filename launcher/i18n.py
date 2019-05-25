import gettext as gettext_module
import locale
import os
import sys
import traceback

import fsboot
from fsbc.settings import Settings

_initialized = False


def initialize_locale(language=None):
    global translations, _initialized
    _initialized = True

    if language is None:
        language = Settings.instance()["language"]

    print("[I18N] Initialize_locale language =", language)
    loc = language
    if not loc:
        try:
            loc, _charset = locale.getdefaultlocale()
            print("[I18N] Locale is", loc)
        except:
            print("[I18N] Exception while checking locale")
            loc = ""
        if not loc:
            loc = ""

    if not loc and sys.platform == "darwin":
        try:
            # noinspection PyUnresolvedReferences
            import CoreFoundation

            c_loc = CoreFoundation.CFLocaleCopyCurrent()
            loc = CoreFoundation.CFLocaleGetIdentifier(c_loc)
        except Exception:
            traceback.print_exc()
        print("[I18N] OS X locale", loc)

    dirs = [
        os.path.join(fsboot.executable_dir(), "share"),
        os.path.join(fsboot.executable_dir(), "..", "share"),
    ]
    if sys.platform == "darwin":
        dirs.insert(
            0, os.path.join(fsboot.executable_dir(), "..", "Resources")
        )

    locale_base = None
    for dir_ in dirs:
        check = os.path.join(dir_, "fs-uae-launcher", "share-dir")
        print("[I18N] Checking", check)
        if not os.path.exists(check):
            continue
        locale_base = os.path.join(dir_, "locale")
        break
    if not locale_base and getattr(sys, "frozen", False):
        if not locale_base:
            p = os.path.abspath(
                os.path.join(fsboot.executable_dir(), "..", "..", "Locale")
            )
            if os.path.exists(p):
                locale_base = p
        if not locale_base:
            p = os.path.abspath(
                os.path.join(
                    fsboot.executable_dir(), "..", "..", "Data", "Locale"
                )
            )
            if os.path.exists(p):
                locale_base = p
        if sys.platform == "darwin":
            # .app/Contents/Locale
            p = os.path.abspath(
                os.path.join(fsboot.executable_dir(), "..", "Locale")
            )
            if os.path.exists(p):
                locale_base = p

    if locale_base:
        print("[I18N] bindtextdomain fs-uae-launcher:", locale_base)
        gettext_module.bindtextdomain("fs-uae-launcher", locale_base)

    mo_path = None
    if locale_base:
        print(
            "[I18N] find translations for",
            loc,
            "in local directory",
            locale_base,
        )
        try:
            mo_path = gettext_module.find(
                "fs-uae-launcher", locale_base, [loc]
            )
        except Exception as e:
            # a bug in openSUSE 12.2's gettext.py can cause an exception
            # in gettext.find (checking len of None).
            print(repr(e))
    else:
        print("[I18N]  No locale directory found")
    print("[I18N] Path to mo file:", mo_path)

    translations = gettext_module.translation(
        "fs-uae-launcher", locale_base, [loc], fallback=True
    )
    print("[I18N] Translations object:", translations)


def gettext(msg):
    if not _initialized:
        initialize_locale()
    return translations.gettext(msg)


def ngettext(n, msg1, msg2):
    if not _initialized:
        initialize_locale()
    return translations.ngettext(n, msg1, msg2)


translations = gettext_module.NullTranslations()
_ = gettext
