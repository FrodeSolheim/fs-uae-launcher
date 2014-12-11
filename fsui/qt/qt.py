import sys

# import_order = ["PyQT5", "PyQT4", "PySide"]
import_order = ["PyQT4", "PySide", "PyQT5"]

if "--pyqt5" in sys.argv:
    import_order = ["PyQT5"]
elif "--pyqt4" in sys.argv:
    import_order = ["PyQT4"]
elif "--pyside" in sys.argv:
    import_order = ["PySide"]

for name in import_order:
    if name == "PyQT5":
        try:
            import PyQt5
        except ImportError:
            continue
        else:
            from PyQt5.QtCore import *
            from PyQt5.QtGui import *
            from PyQt5.QtWidgets import *
            from PyQt5.QtCore import pyqtSignal as Signal
            from PyQt5.QtCore import pyqtSignal as QSignal
            from PyQt5.QtOpenGL import *
            try:
                from PyQt5.QtX11Extras import *
            except ImportError:
                pass
    elif name == "PyQT4":
        try:
            import PyQt4
        except ImportError:
            continue
        else:
            import sip
            sip.setapi("QString", 2)
            from PyQt4.QtCore import *
            from PyQt4.QtGui import *
            from PyQt4.QtCore import pyqtSignal as Signal
            from PyQt4.QtCore import pyqtSignal as QSignal
            from PyQt4.QtOpenGL import *
    elif name == "PySide":
        try:
            import PySide
        except ImportError:
            continue
        else:
            from PySide.QtCore import *
            from PySide.QtCore import Signal as QSignal
            from PySide.QtGui import *
            from PySide.QtOpenGL import *
    else:
        raise Exception("unknown QT python bindings specified")
    break
else:
    raise Exception("no QT python bindings found")
