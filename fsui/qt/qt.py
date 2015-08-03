import fsbc.Application
import sys

# if "arcade" in sys.argv[0] or len(sys.argv) > 1 and "arcade" in sys.argv[1]:
#     import_order = ["PyQT4", "PySide", "PyQT5"]
# else:
#     import_order = ["PyQT5", "PyQT4", "PySide"]
# import_order = ["PyQT4", "PySide", "PyQT5"]

import_order = ["PyQT5"]

if "--qt-bindings=pyqt5" in sys.argv:
    import_order = ["PyQT5"]
elif "--qt-bindings=pyqt4" in sys.argv:
    import_order = ["PyQT4"]
elif "--qt-bindings=pyside" in sys.argv:
    import_order = ["PySide"]

for name in import_order:
    if name == "PyQT5":
        try:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            import PyQt5
        except ImportError:
            continue
        else:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtCore import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtGui import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtWidgets import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtCore import pyqtSignal as Signal
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtCore import pyqtSignal as QSignal
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtOpenGL import *
            try:
                # noinspection PyUnresolvedReferences, PyPackageRequirements
                from PyQt5.QtX11Extras import *
            except ImportError:
                pass
    elif name == "PyQT4":
        try:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            import PyQt4
        except ImportError:
            continue
        else:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            import sip
            sip.setapi("QString", 2)
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt4.QtCore import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt4.QtGui import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt4.QtCore import pyqtSignal as Signal
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt4.QtCore import pyqtSignal as QSignal
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt4.QtOpenGL import *
    elif name == "PySide":
        try:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            import PySide
        except ImportError:
            continue
        else:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PySide.QtCore import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PySide.QtCore import Signal as QSignal
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PySide.QtGui import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PySide.QtOpenGL import *
    else:
        raise Exception("unknown QT python bindings specified")
    break
else:
    raise Exception("no QT python bindings found")
