import os
import sys
import locale
import traceback
import gettext as gettext_module


def initialize_locale(language=""):
    global translations

    loc = language    
    if not loc:
        try:
            loc, _charset = locale.getdefaultlocale()
            print("locale is", loc)
        except:
            print("exception while checking locale")
            loc = ""
        if not loc:
            loc = ""

    if not loc and sys.platform == 'darwin':
        try:
            # noinspection PyUnresolvedReferences
            import CoreFoundation
            c_loc = CoreFoundation.CFLocaleCopyCurrent()
            loc = CoreFoundation.CFLocaleGetIdentifier(c_loc)
        except Exception:
            traceback.print_exc()
        print("mac locale", loc)

    dirs = [os.path.join(os.getcwd(), "launcher", "share"),
            os.path.join(os.getcwd(), "share"),
            os.getcwd(), "/usr/local/share", "/usr/share"]
    
    locale_base = None
    for dir in dirs:
        if not os.path.exists(
                os.path.join(dir, "fs-uae-launcher", "share-dir")):
            continue
        locale_base = os.path.join(dir, "locale")
        print("bindtextdomain fs-uae-launcher:", locale_base)
        gettext_module.bindtextdomain("fs-uae-launcher", locale_base)
        break
    
    mo_path = None
    if locale_base:
        try:
            mo_path = gettext_module.find(
                "fs-uae-launcher", locale_base, [loc])
        except Exception:
            # a bug in openSUSE 12.2's gettext.py can cause an exception
            # in gettext.find (checking len of None).
            pass
    print("path to mo file:", mo_path)
    
    translations = gettext_module.translation(
        "fs-uae-launcher", locale_base, [loc], fallback=True)
    print("translations object:", translations)


def gettext(msg):
    return translations.gettext(msg)


def ngettext(n, msg1, msg2):
    return translations.ngettext(n, msg1, msg2)


translations = gettext_module.NullTranslations()
_ = gettext
