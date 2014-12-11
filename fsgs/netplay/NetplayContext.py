from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..BaseContext import BaseContext


class NetplayContext(BaseContext):

    def __init__(self, main_context):
        BaseContext.__init__(self, main_context)

    @property
    def enabled(self):
        try:
            from fs_uae_launcher.netplay.Netplay import Netplay
        except ImportError:
            # FIXME: a bit ugly hack, but fs_uae_launcher.netplay.Netplay is not
            # imported from FS-UAE Game Center
            # noinspection PyPep8Naming
            Netplay = None
            assert Netplay is None
            return False
        else:
            return Netplay.enabled
