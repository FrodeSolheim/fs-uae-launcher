from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import locale
import traceback
from gettext import NullTranslations, bindtextdomain, find, translation

try:
    getcwd = os.getcwdu
except AttributeError:
    getcwd = os.getcwd

translations = NullTranslations()


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
            #noinspection PyUnresolvedReferences
            import CoreFoundation
            c_loc = CoreFoundation.CFLocaleCopyCurrent()
            loc = CoreFoundation.CFLocaleGetIdentifier(c_loc)
        except Exception:
            traceback.print_exc()
        print("mac locale", loc)

    dirs = [os.path.join(getcwd(), "launcher", "share"),
            os.path.join(getcwd(), "share"),
            getcwd(), "/usr/local/share", "/usr/share"]
    
    locale_base = None
    for dir in dirs:
        if not os.path.exists(
                os.path.join(dir, "fs-uae-launcher", "share-dir")):
            continue
        locale_base = os.path.join(dir, "locale")
        print("bindtextdomain fs-uae-launcher:", locale_base)
        bindtextdomain("fs-uae-launcher", locale_base)
        break
    
    mo_path = None
    if locale_base:
        try:
            mo_path = find("fs-uae-launcher", locale_base, [loc])
        except Exception:
            # a bug in openSUSE 12.2's gettext.py can cause an exception
            # in gettext.find (checking len of None).
            pass
    print("path to mo file:", mo_path)
    
    translations = translation(
        "fs-uae-launcher", locale_base, [loc], fallback=True)
    print("translations object:", translations)


def _(msg):
    try:
        return translations.ugettext(msg)
    except AttributeError:
        return translations.gettext(msg)

gettext = _


def ngettext(n, msg1, msg2):
    try:
        return translations.ungettext(n, msg1, msg2)
    except AttributeError:
        return translations.ngettext(n, msg1, msg2)
