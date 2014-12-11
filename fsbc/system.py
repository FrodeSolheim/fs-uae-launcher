from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

windows = sys.platform == "win32"
linux = sys.platform.startswith("linux")
macosx = sys.platform == "darwin"

if windows:
    platform = "windows"
elif linux:
    platform = "linux"
elif macosx:
    platform = "macosx"
else:
    platform = "unknown"
