# noinspection PyUnresolvedReferences
# noinspection PyUnresolvedReferences
from OpenGL.arrays.vbo import VBO
from OpenGL.GL import *
# noinspection PyUnresolvedReferences
from OpenGL.GL.ARB.fragment_shader import *
# noinspection PyUnresolvedReferences
from OpenGL.GL.ARB.framebuffer_object import *
# noinspection PyUnresolvedReferences
from OpenGL.GL.ARB.multitexture import *
# noinspection PyUnresolvedReferences
from OpenGL.GL.ARB.shader_objects import *
# noinspection PyUnresolvedReferences
from OpenGL.GL.ARB.vertex_shader import *
# noinspection PyUnresolvedReferences
from OpenGL.GLU import *
# noinspection PyUnresolvedReferences
from OpenGL.raw.GL.EXT.framebuffer_object import *

# from OpenGLContext.arrays import *


def filter_global(x):
    if x.lower().startswith("gl"):
        return True
    return False


def pyopengl_globals():
    return globals()
