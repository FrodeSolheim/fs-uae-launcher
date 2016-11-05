from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from fsui.qt import QImage
# import numpy
# from PIL import Image
# from fsbc.Application import app
from arcade.resources import resources
from arcade.glui.opengl import gl, fs_emu_texturing, fs_emu_blending


class Texture(object):
    shadow = None
    shadow2 = None
    gloss = None
    screen_gloss = None
    static = None
    default_item = None
    missing_screenshot = None
    missing_cover = None
    logo = None
    top = None
    top_logo = None
    top_logo_selected = None
    splash = None

    add = None
    add_selected = None
    home = None
    home_selected = None
    minimize = None
    minimize_selected = None
    close = None
    close_selected = None
    shutdown = None
    shutdown_selected = None

    bottom_bar = None
    screen_border_1 = None
    screen_border_2 = None
    top_background = None
    top_item = None
    top_item_selected = None
    top_item_left = None
    top_item_left_selected = None
    top_item_right = None
    top_item_arrow = None
    top_item_arrow_selected = None

    glow_top = None
    glow_top_left = None
    glow_left = None

    sidebar_background = None
    sidebar_background_shadow = None
    heading_strip = None
    item_background = None
    top_item_background = None
    logo_32 = None
    stretch = None
    aspect = None

    def __init__(self, name, target=gl.GL_TEXTURE_2D, **kwargs):
        # print(repr(type(name)))
        # if isinstance(name, (int, long)):
        if isinstance(name, int):
            self.size = kwargs["size"]
            self.texture = name
        else:
            self.size = [0, 0]
            # print(name, kwargs)
            out_data = {}
            self.texture = self.from_resource(
                name, target=target, size=self.size, out_data=out_data,
                **kwargs)
            self.data = out_data["im_data"]
            self.gl_type = out_data["type"]
        self.w, self.h = self.size
        self.target = target

    def bind(self):
        gl.glBindTexture(self.target, self.texture)

    def render(self, x, y, w=None, h=None, z=0.0, opacity=1.0):
        if w is None:
            w = self.w
        if h is None:
            h = self.h
        self.bind()
        fs_emu_texturing(True)
        if self.gl_type == gl.GL_RGBA or opacity < 1.0:
            fs_emu_blending(True)
        else:
            fs_emu_blending(False)
        gl.glBegin(gl.GL_QUADS)
        if opacity < 1.0:
            gl.glColor4f(opacity, opacity, opacity, opacity)
        else:
            gl.glColor3f(1.0, 1.0, 1.0)
        gl.glTexCoord(0.0, 1.0)
        gl.glVertex3f(x, y, z)
        gl.glTexCoord(1.0, 1.0)
        gl.glVertex3f(x + w, y, z)
        gl.glTexCoord(1.0, 0.0)
        gl.glVertex3f(x + w, y + h, z)
        gl.glTexCoord(0.0, 0.0)
        gl.glVertex3f(x, y + h, z)
        gl.glEnd()

    @classmethod
    def load(cls, im, mipmap=False, min_filter=None,
             wrap_s=gl.GL_CLAMP_TO_EDGE, wrap_t=gl.GL_CLAMP_TO_EDGE,
             target=gl.GL_TEXTURE_2D, size=None, out_data=None):
        if size is None:
            size = [0, 0]
        # type = "RGB"
        # gl_type = gl.GL_RGB
        # if im.mode == "RGBA":
        #     # convert to premultiplied alpha
        #     #pix = im.load()
        #     #for x in range(im.size[0]):
        #     #    for y in range(im.size[1]):
        #     #        r, g, b, a = pix[x, y]
        #     #        if a:
        #     #            pix[x, y] = r * 255 // a, g * 255 // a, \
        #     #                 b * 255 // a, a
        #     #        else:
        #     #            pix[x, y] = 0, 0, 0, 0
        #     a = numpy.fromstring(im.tostring(), dtype=numpy.uint8)
        #     alpha_layer = a[3::4] / 255.0
        #     a[0::4] *= alpha_layer
        #     a[1::4] *= alpha_layer
        #     a[2::4] *= alpha_layer
        #     #im = Image.fromstring("RGBA", im.size, a.tostring())
        #     im_data = a.tostring()
        #     # type = "RGBA"
        #     gl_type = gl.GL_RGBA
        # else:
        #     im_data = im.tostring("raw", "RGB")
        #
        # size[0] = im.size[0]
        # size[1] = im.size[1]
        # #texture = glGenTextures(1)

        internal_format = gl.GL_RGBA
        texture_format = gl.GL_BGRA

        if im.format() != QImage.Format_ARGB32_Premultiplied:
            im = im.convertToFormat(QImage.Format_ARGB32_Premultiplied)

        bits = im.bits()
        try:
            pixels = bits.tobytes()
        except AttributeError:
            bits.setsize(im.byteCount())
            pixels = bytes(bits)
        size[0] = im.width()
        size[1] = im.height()

        from arcade.glui.render import Render
        texture = Render.get().create_texture()
        gl.glBindTexture(target, texture)
        gl.glTexImage2D(
            target, 0, internal_format, size[0], size[1], 0, texture_format,
            gl.GL_UNSIGNED_BYTE, pixels)
        if mipmap:
            gl.glGenerateMipmap(target)
            if min_filter is None:
                min_filter = gl.GL_LINEAR_MIPMAP_LINEAR
        else:
            if min_filter is None:
                min_filter = gl.GL_LINEAR
        gl.glTexParameteri(target, gl.GL_TEXTURE_MIN_FILTER, min_filter)
        gl.glTexParameteri(target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(target, gl.GL_TEXTURE_WRAP_S, wrap_s)
        gl.glTexParameteri(target, gl.GL_TEXTURE_WRAP_T, wrap_t)
        if out_data is not None:
            out_data["im_data"] = pixels
            out_data["type"] = internal_format
        return texture

    @classmethod
    def from_resource(cls, name, size=None, **kwargs):
        if size is None:
            size = [0, 0]
        # try:
        #     path = app.data_file(name)
        # except LookupError:
        #     im = resources.resource_pil_image(name)
        # else:
        #     im = Image.open(path)
        # return cls.load(im, size=size, **kwargs)
        im = resources.resource_qt_image(name)
        return cls.load(im, size=size, **kwargs)
