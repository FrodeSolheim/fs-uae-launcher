try:
    # FIXME: this is a hack, there should not be a dependency here
    from launcher.i18n import gettext as _gettext
except ImportError:

    def _gettext(message):
        return message


def gettext(message):
    return _gettext(message)
