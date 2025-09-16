import json
import traceback

from arcade.glui.opengl import fs_emu_blending, fs_emu_texturing
from OpenGL import GL as gl
from OpenGL.GLU import gluOrtho2D
from arcade.glui.texture import Texture
from arcade.resources import resources
from fsbc.util import memoize
from fsui.qt import (
    QColor,
    QFontDatabase,
    QFontMetrics,
    QImage,
    QPainter,
    QPen,
    QPoint,
    is_pyqt6,
)

CACHE_SIZE = 100
text_cache = []
for _ in range(CACHE_SIZE):
    text_cache.append({"text": None, "font": None, "texture": None})


class Font(object):
    title_font = None
    subtitle_font = None
    small_font = None
    main_path_font = None
    list_subtitle_font = None
    header_font = None

    font_ids = {}

    def __init__(self, path, size):
        if is_pyqt6:
            self.database = QFontDatabase
        else:
            self.database = QFontDatabase()
        try:
            self.font_id = Font.font_ids[path]
        except Exception:
            if isinstance(path, str):
                self.font_id = self.database.addApplicationFont(path)
            else:
                self.font_id = self.database.addApplicationFontFromData(
                    path.read()
                )
            Font.font_ids[path] = self.font_id
        self.families = self.database.applicationFontFamilies(self.font_id)
        print(self.families)
        self.size = size
        if len(self.families) > 0:
            styles = self.database.styles(self.families[0])
            print(styles)
            self.font = self.database.font(self.families[0], "Bold", size)
            if self.size <= 0:
                print("WARNING: font size is", self.size)
                traceback.print_stack()
            self.font.setPixelSize(self.size)
        else:
            self.font = None

    def set_size(self, size):
        if self.font is not None:
            self.size = size
            if self.size <= 0:
                print("WARNING: font size is", self.size)
                traceback.print_stack()
            self.font.setPixelSize(self.size)

    def render(self, text, _, color):
        if self.font is None:
            return "", (0, 0)

        fm = QFontMetrics(self.font)
        rect = fm.boundingRect(text)
        im = QImage(
            rect.x() + rect.width(),
            rect.height(),
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        im.fill(QColor(0, 0, 0, 0))
        painter = QPainter()
        painter.begin(im)
        painter.setPen(QPen(QColor(*color)))
        painter.setFont(self.font)
        painter.drawText(QPoint(0 - rect.x(), 0 - rect.y()), text)
        painter.end()

        bits = im.bits()
        try:
            pixels = bits.tobytes()
        except AttributeError:
            bits.setsize(im.sizeInBytes())
            pixels = bytes(bits)
        return pixels, (rect.x() + rect.width(), rect.height())

    def rendered_size(self, text):
        if self.font is None:
            return 0, 0

        fm = QFontMetrics(self.font)
        rect = fm.boundingRect(text)
        return rect.width(), rect.height()


class BitmapFont(object):
    title_font = None
    menu_font = None

    def __init__(self, name):
        self.texture = None
        self.x = []
        self.y = []
        self.w = [0 for _ in range(256)]
        self.h = 0
        self.load(name)

    @memoize
    def measure(self, text):
        required_width = 0
        required_height = self.h
        for c in text:
            required_width += self.w[ord(c)]
        return required_width, required_height

    def render(self, text, x, y, r=1.0, g=1.0, b=1.0, alpha=1.0):
        global text_cache
        if not text:
            return 0

        # find cached text entry, if any

        for i, item in enumerate(text_cache):
            if item["text"] == text and item["font"] == self:
                text_cache.pop(i)
                break
        else:
            item = None

        if item:
            fs_emu_blending(True)
            fs_emu_texturing(True)

            w = item["w"]
            h = item["h"]
            gl.glBindTexture(gl.GL_TEXTURE_2D, item["texture"])
            gl.glBegin(gl.GL_QUADS)
            gl.glColor4f(r * alpha, g * alpha, b * alpha, alpha)
            gl.glTexCoord2d(0.0, 0.0)
            gl.glVertex2d(x, y)
            gl.glTexCoord2d(1.0, 0.0)
            gl.glVertex2d(x + w, y)
            gl.glTexCoord2d(1.0, 1.0)
            gl.glVertex2d(x + w, y + h)
            gl.glTexCoord2d(0.0, 1.0)
            gl.glVertex2d(x, y + h)
            gl.glEnd()

            # re-insert item at front
            text_cache.insert(0, item)
            return w, h

        # calculate size of text

        required_width, required_height = self.measure(text)

        # setup fbo

        render_texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, render_texture)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_RGBA,
            required_width,
            required_height,
            0,
            gl.GL_RGBA,
            gl.GL_UNSIGNED_INT,
            None,
        )
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE
        )
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE
        )
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR
        )

        # FIXME: Mipmapping?
        mip_mapping = 0
        if mip_mapping:
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D,
                gl.GL_TEXTURE_MIN_FILTER,
                gl.GL_LINEAR_MIPMAP_LINEAR,
            )
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_GENERATE_MIPMAP, gl.GL_TRUE
            )
            gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        else:
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR
            )

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # Set up some renderbuffer state

        from OpenGL.GL import (
            glBindFramebuffer,
            glCheckFramebufferStatus,
            glDeleteFramebuffers,
            glFramebufferTexture2D,
            glGenFramebuffers,
        )

        frame_buffer = gl.GLuint()
        glGenFramebuffers(1, frame_buffer)
        glBindFramebuffer(gl.GL_FRAMEBUFFER, frame_buffer)
        glFramebufferTexture2D(
            gl.GL_FRAMEBUFFER,
            gl.GL_COLOR_ATTACHMENT0,
            gl.GL_TEXTURE_2D,
            render_texture,
            0,
        )

        status = glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            print("glCheckFramebufferStatusEXT error", status)

        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glPushAttrib(int(gl.GL_VIEWPORT_BIT) | int(gl.GL_ENABLE_BIT))
        gl.glViewport(0, 0, required_width, required_height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gluOrtho2D(0, required_width, 0, required_height)

        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_TEXTURE_2D)

        self.texture.bind()

        tw = self.texture.w
        th = self.texture.h

        gl.glBegin(gl.GL_QUADS)
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        x2 = 0
        h = self.h
        for ch in text:
            c = ord(ch)
            w = self.w[c]
            s1 = self.x[c] / tw
            s2 = (self.x[c] + w) / tw
            t1 = (self.y[c]) / th
            t2 = (self.y[c] + h) / th
            gl.glTexCoord2d(s1, t2)
            gl.glVertex2d(x2, 0)
            gl.glTexCoord2d(s2, t2)
            gl.glVertex2d(x2 + w, 0)
            gl.glTexCoord2d(s2, t1)
            gl.glVertex2d(x2 + w, h)
            gl.glTexCoord2d(s1, t1)
            gl.glVertex2d(x2, h)
            x2 += w
        gl.glEnd()

        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopAttrib()
        glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glPopMatrix()

        glDeleteFramebuffers(1, frame_buffer)

        if mip_mapping:
            gl.glBindTexture(gl.GL_TEXTURE_2D, render_texture)
            gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        new_item = {
            "font": self,
            "text": text,
            "w": required_width,
            "h": required_height,
            "texture": render_texture,
        }
        text_cache.insert(0, new_item)

        item = text_cache.pop()
        if item["texture"]:
            gl.glDeleteTextures([item["texture"]])

        # now the text is in the cache, so call function again
        return self.render(text, x, y, r, g, b, alpha)

    def load(self, name):
        print("load font", name)
        self.texture = Texture(name + ".png")
        f = resources.resource_stream(name + ".json")
        doc = json.loads(f.read().decode("UTF-8"))
        self.x = doc["x"]
        self.y = doc["y"]
        self.w = doc["w"]
        self.h = doc["h"][0]
