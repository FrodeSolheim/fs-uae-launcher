import locale
# we must set the LC_NUMERIC locale to C, because PyOpenGL has
# a problem if comma is used as a decimal separator (problem
# parsing the OpenGL version)
locale.setlocale(locale.LC_NUMERIC, str("C"))

from OpenGL.GL import *
# noinspection PyUnresolvedReferences
from OpenGL.GLU import *
# noinspection PyUnresolvedReferences
from OpenGL.GL.ARB.shader_objects import *
# noinspection PyUnresolvedReferences
from OpenGL.GL.ARB.vertex_shader import *
# noinspection PyUnresolvedReferences
from OpenGL.GL.ARB.multitexture import *
# noinspection PyUnresolvedReferences
from OpenGL.GL.ARB.fragment_shader import *
# noinspection PyUnresolvedReferences
from OpenGL.GL.ARB.framebuffer_object import *
# noinspection PyUnresolvedReferences
from OpenGL.raw.GL.EXT.framebuffer_object import *
# noinspection PyUnresolvedReferences
from OpenGL.arrays.vbo import VBO
# from OpenGLContext.arrays import *


# these constants are repeated here to aid code inspection tools (in
# pyopengl they are expanded (run-time) from a string).

GL_BLEND = 0xBE2
GL_TEXTURE_2D = 0xDE1
GL_COMPILE_STATUS = 0x8b81
GL_LINK_STATUS = 0x8b82
GL_FRAGMENT_SHADER = 0x8b30
GL_VERTEX_SHADER = 0x8b31
GL_ONE = 0x1
GL_ONE_MINUS_SRC_COLOR = 0x301
GL_SRC_ALPHA = 0x302
GL_ONE_MINUS_SRC_ALPHA = 0x303
GL_RGB = 0x1907
GL_RGBA = 0x1908
GL_BGRA = 0x80E1
GL_TEXTURE_MAG_FILTER = 0x2800
GL_TEXTURE_MIN_FILTER = 0x2801
GL_FRAMEBUFFER_EXT = 0x8D40
GL_COLOR_ATTACHMENT0_EXT = 0x8CE0
GL_RENDERBUFFER_EXT = 0x8D41
GL_DEPTH_ATTACHMENT_EXT = 0x8D00
GL_LINEAR = 0x2601
GL_FRAMEBUFFER_COMPLETE_EXT = 0x8CD5
GL_DEPTH_COMPONENT24 = 0x81A6
GL_QUADS = 0x7
GL_DEPTH_TEST = 0xB71
GL_TEXTURE_2D_ARB = 0x207A
GL_COLOR_BUFFER_BIT = 0x4000
GL_DEPTH_BUFFER_BIT = 0x100
GL_MODELVIEW = 0x1700
GL_PROJECTION = 0x1701
GL_LIGHT_MODEL_TWO_SIDE = 0xB52
GL_LIGHT_MODEL_LOCAL_VIEWER = 0xB51
GL_LIGHT_MODEL_AMBIENT = 0xB53
GL_SEPARATE_SPECULAR_COLOR = 0x81FA
GL_LIGHT_MODEL_COLOR_CONTROL = 0x81F8
GL_LIGHTING = 0xB50
GL_LIGHT0 = 0x4000
GL_LIGHT1 = 0x4001
GL_LIGHT2 = 0x4002
GL_LIGHT3 = 0x4003
GL_LIGHT4 = 0x4004
GL_LIGHT5 = 0x4005
GL_LIGHT6 = 0x4006
GL_LIGHT7 = 0x4007
GL_AMBIENT = 0x1200
GL_DIFFUSE = 0x1201
GL_SPECULAR = 0x1202
GL_SHININESS = 0x1601
GL_EMISSION = 0x1600
GL_POSITION = 0x1203
GL_FRONT = 0x404
GL_BACK = 0x405
GL_POLYGON_OFFSET_FILL = 0x8037


# FIXME: cache


def fs_emu_blending(enable):
    if enable:
        glEnable(GL_BLEND)
    else:
        glDisable(GL_BLEND)


def fs_emu_texturing(enable):
    if enable:
        glEnable(GL_TEXTURE_2D)
    else:
        glDisable(GL_TEXTURE_2D)


def filter_global(x):
    if x.lower().startswith("gl"):
        return True
    return False


__all__ = ["fs_emu_texturing", "fs_emu_blending"]


for __x in list(globals()):
    if filter_global(__x):
        __all__.append(__x)


class GL:
    pass


gl = GL


for __x in list(globals()):
    if filter_global(__x):
        setattr(gl, __x, globals()[__x])


if False:
    # this fixes ImportError: No module named win32 when used with py2exe
    # and other problems related to required modules missing from pyOpenGL
    # noinspection PyUnresolvedReferences
    import ctypes
    # noinspection PyUnresolvedReferences
    import logging
    # noinspection PyUnresolvedReferences
    import OpenGL.platform.win32
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays._buffers
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays._numeric
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays._strings
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.arraydatatype
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.arrayhelpers
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.buffers
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.ctypesarrays
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.ctypesparameters
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.ctypespointers
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.formathandler
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.lists
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.nones
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.numbers
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.numeric
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.numericnames
    # noinspection PyUnresolvedReferences
    # import OpenGL.arrays.numpymodule
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.strings
    # noinspection PyUnresolvedReferences
    import OpenGL.arrays.vbo
