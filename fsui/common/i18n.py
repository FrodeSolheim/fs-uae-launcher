try:
    from launcher.i18n import gettext
except ImportError:

    def gettext(message: str) -> str:
        return message


__all__ = ["gettext"]
