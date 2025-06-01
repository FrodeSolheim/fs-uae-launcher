import threading
import traceback

from arcade.glui.opengl import gl
from PyQt6.QtOpenGLWidgets import QOpenGLWidget


# noinspection PyPep8Naming
class GLWidget(QOpenGLWidget):
    def __init__(self, parent, callbacks):
        QOpenGLWidget.__init__(self, parent)
        self._callbacks = callbacks
        self._initialized = False
        self._first_initialize_gl_call = True
        self._first_resize_gl_call = True
        self._first_paint_gl_call = True

        # set_black_background(self)
        # palette = self.palette()
        # palette.setColor(self.backgroundRole(), Qt.blue)
        # self.setPalette(palette)
        # self.setAutoFillBackground(True)
        # self.setStyleSheet("background-color: black;")

    def initializeGL(self):
        print("[OPENGL] GLWidget.initializeGL")
        if self._first_initialize_gl_call:
            print("[OPENGL]", threading.current_thread())
            self._first_initialize_gl_call = False
        try:
            # Moved most of the initialization to (first invocation of)
            # resizeGL due to issues on OS X.
            context = self.context()
            print("[OPENGL] Qt OpenGL information:")
            print("[OPENGL] Valid context:", context.isValid())
            gl_format = context.format()
            print("[OPENGL] Version major:", gl_format.majorVersion())
            print("[OPENGL] Version minor:", gl_format.minorVersion())
            print("[OPENGL] Context profile:", gl_format.profile())
            print("[OPENGL] Direct rendering:", gl_format.directRendering())
            print("[OPENGL] Depth buffer size:", gl_format.depthBufferSize())
            print("[OPENGL] Double buffering:", self.doubleBuffer())
            print("[OPENGL] Auto buffer swap:", self.autoBufferSwap())
        except Exception:
            traceback.print_exc()

    def resizeGL(self, width, height):
        print("[OPENGL] GLWidget.resizeGL", width, height)
        if self._first_resize_gl_call:
            print("[OPENGL]", threading.current_thread())
            self._first_resize_gl_call = False

        gl.load()
        try:
            if not self._initialized:
                if width == 160 and height == 160:
                    print("[OPENGL] WARNING: OS X 160x160 workaround(?)")
                    # work around bug(?) on os x
                    return
            # Fail-safes to prevent a viewport of size 0 (prevents some
            # potential divide-by-zero nastiness).
            # if width == 0:
            #     width = 100
            # if height == 0:
            #     height = 100
            if width < 480:
                print("[OPENGL] Setting minimum width 480")
                width = 480
            if height < 270:
                print("[OPENGL] Setting minimum height 270")
                height = 270
            if not self._initialized:
                self._callbacks.initialize(width, height)
                self._initialized = True
                return
            self._callbacks.resize(width, height)
        except Exception:
            traceback.print_exc()
        gl.unload()

    def paintGL(self):
        if self._first_paint_gl_call:
            print("[OPENGL] GLWidget.paintGL")
            print("[OPENGL]", threading.current_thread())
            self._first_paint_gl_call = False
        gl.load()
        try:
            self._callbacks.render()
        except Exception:
            traceback.print_exc()
            # import sys
            # sys.exit(1)
        gl.unload()
