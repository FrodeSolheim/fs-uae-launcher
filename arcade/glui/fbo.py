import ctypes

from .opengl import fs_emu_texturing, gl
from .render import Render
from .window import premultiplied_texture_program, set_program, texture_program


class FrameBufferObject(object):  # Renderable, RendererBase):
    def __init__(self, width=100, height=100):
        self._transparent = True
        self._has_transparency = True
        self._width = width
        self._height = height
        self._fb = None
        self._depth_rb = None
        self._stencil_rb = None
        self._texture = None

    def __del__(self):
        self.free()

    def free(self):
        if self._fb:
            gl.glDeleteFramebuffersEXT(1, self._fb)
        if self._depth_rb:
            gl.glDeleteRenderbuffersEXT(1, self._depth_rb)
        if self._stencil_rb:
            gl.glDeleteRenderbuffersEXT(1, self._stencil_rb)
        if self._texture:
            gl.glDeleteTextures([self._texture])

    def _create(self):
        if self._fb is not None:
            return

        w = self._width
        h = self._height
        if self._transparent:
            texture_format = gl.GL_RGBA
        else:
            texture_format = gl.GL_RGBA
        texture_target = gl.GL_TEXTURE_2D
        fb = gl.GLuint()
        depth_rb = gl.GLuint()
        stencil_rb = gl.GLuint()

        gl.glGenFramebuffersEXT(1, ctypes.byref(fb))
        color_tex = Render.get().create_texture()
        gl.glGenRenderbuffersEXT(1, ctypes.byref(depth_rb))
        gl.glGenRenderbuffersEXT(1, ctypes.byref(stencil_rb))

        fb = fb.value
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, fb)

        # initialize color texture
        gl.glBindTexture(texture_target, color_tex)
        gl.glTexParameterf(
            texture_target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR
        )
        gl.glTexParameterf(
            texture_target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR
        )
        gl.glTexImage2D(
            texture_target,
            0,
            texture_format,
            w,
            h,
            0,
            gl.GL_RGB,
            gl.GL_INT,
            None,
        )
        try:
            # FIXME: An error seems to be thrown here on Windows, even
            # though it seems to work...
            gl.glFramebufferTexture2DEXT(
                gl.GL_FRAMEBUFFER_EXT,
                gl.GL_COLOR_ATTACHMENT0_EXT,
                texture_target,
                color_tex,
                0,
            )
        except Exception:
            pass

        # initialize depth renderbuffer
        gl.glBindRenderbufferEXT(gl.GL_RENDERBUFFER_EXT, depth_rb)
        gl.glRenderbufferStorageEXT(
            gl.GL_RENDERBUFFER_EXT, gl.GL_DEPTH_COMPONENT24, w, h
        )
        gl.glFramebufferRenderbufferEXT(
            gl.GL_FRAMEBUFFER_EXT,
            gl.GL_DEPTH_ATTACHMENT_EXT,
            gl.GL_RENDERBUFFER_EXT,
            depth_rb,
        )

        # initialize stencil renderbuffer

        # glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, stencil_rb)
        # glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_STENCIL_INDEX,
        #         512, 512)
        # glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT,
        #        GL_STENCIL_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, stencil_rb)
        gl.glBindTexture(texture_target, 0)

        # Check framebuffer completeness at the end of initialization.
        status = gl.glCheckFramebufferStatusEXT(gl.GL_FRAMEBUFFER_EXT)
        assert status == gl.GL_FRAMEBUFFER_COMPLETE_EXT, str(status)
        self._fb = fb
        self._depth_rb = depth_rb
        self._stencil_rb = stencil_rb
        self._texture = color_tex

    def bind(self):
        if self._fb is None:
            self._create()
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self._fb)
        # glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, self._depth_rb)

    def unbind(self):
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)
        # glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, 0)

    def set_viewport(self):
        gl.glViewport(0, 0, self._width, self._height)

    def render(self, opacity=1.0):
        render_texture(
            self._texture,
            -1.0,
            -1.0,
            0,
            2.0,
            2.0,
            opacity=opacity,
            is_premultiplied=True,
        )


def render_texture(
    texture, x, y, z, w, h, opacity=1.0, is_premultiplied=False
):
    if is_premultiplied:
        set_program(premultiplied_texture_program)
    else:
        set_program(texture_program)
    fs_emu_texturing(True)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    gl.glBegin(gl.GL_QUADS)
    gl.glColor(1.0, 1.0, 1.0, opacity)
    gl.glTexCoord2f(0.0, 0.0)
    gl.glVertex3f(x, y, z)
    gl.glTexCoord2f(1.0, 0.0)
    gl.glVertex3f(x + w, y, z)
    gl.glTexCoord2f(1.0, 1.0)
    gl.glVertex3f(x + w, y + h, z)
    gl.glTexCoord2f(0.0, 1.0)
    gl.glVertex3f(x, y + h, z)
    gl.glEnd()
    set_program(None)
