try:
    from launcher.i18n import gettext
except ImportError:
    gettext = lambda x: x
