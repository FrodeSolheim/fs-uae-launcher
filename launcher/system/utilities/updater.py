from autologging import traced

from launcher.system.tools.updater import Updater


# FIXME: Move updater here?
@traced
def wsopen(window=None, **kwargs):
    return Updater.open(window, **kwargs)
