from arcade.glui.opengl import fs_emu_blending, fs_emu_texturing, gl
from arcade.glui.text import TextRenderer

DISPLAY_FPS = False
DISPLAY_SYNC = False

PERSPECTIVE_STANDARD = 1
PERSPECTIVE_ORTHO = 2
PERSPECTIVE_HD = 3

TEXT_CACHE_SIZE = 100


class Render(object):
    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls("DO_NOT_INSTANTIATE")
        return cls._instance

    @classmethod
    def reset(cls):
        print("[STATE] Reset state")
        cls._instance = None

    def __init__(self, sentinel):
        assert sentinel == "DO_NOT_INSTANTIATE"
        print("[STATE] Init state")

        self.was_scanning = False

        self.currently_ingame = False
        self.game_running = False

        # Render items
        self.display_sync = DISPLAY_SYNC
        self.display_fps = DISPLAY_FPS
        self.display_last_iteration = 0
        self.display_width = 0
        self.display_height = 0
        self.last_time_str = ""

        self.gl_left = None
        self.gl_right = None
        self.gl_height = None
        self.gl_width = None
        self.fov_y = None
        self.fov_x = None
        self.display_aspect = None
        self.ortho_pscalex = None
        self.ortho_pscaley = None
        self.projection = None

        # State items

        self.time = 0
        self.down_navigatable = None
        self.dialog = None
        self.dialog_time = 0.0

        # ...

        self.quit = False
        self.allow_minimize = True

        self.history = []

        self.zoom = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        self.frame_number = 0
        self.idle_from = None
        self.dirty = True
        self.non_dirty_state = False
        self.twice = False
        self.fade_start = 0.0
        self.fade_end = 0.0
        self.fade_splash = True
        self.fade_from = (0, 0, 0, 0)
        self.fade_to = (0, 0, 0, 0)
        self.opacity = 1.0
        self.perspective = 0

        self.center_item = None
        self.center_item_time = 0

        self.items_brightness = 0.8
        # self.items_brightness_target = 1.0
        # self.items_brightness_speed = 1.0
        self.navigatable = None
        self.current_menu = None
        self.current_game = None
        self.config_menu = None
        self.top_menu = None

        self.hide_mouse_time = 0
        self.mouse_visible = True
        # options
        self.force_portrait = False
        self.max_ratio = None
        # self.max_ratio = 1.0

        self.delete_texture_list = []
        self.unused_texture_list = []

        self.text_cache_history = []
        self.text_cache = {}

        self.mouse_item = None
        self.mouse_press_item = None

    def create_texture(self):
        if len(self.unused_texture_list) == 0:
            self.unused_texture_list.extend(gl.glGenTextures(50))
        return self.unused_texture_list.pop()

    def delete_textures(self):
        # for t in cls.delete_texture_list:
        #     glDeleteTextures([t])

        gl.glDeleteTextures(self.delete_texture_list)
        self.delete_texture_list[:] = []

        # cls.unused_texture_list.extend(cls.delete_texture_list)
        # cls.delete_texture_list[:] = []
        # pass

        if len(self.delete_texture_list) > 0:
            texture = self.delete_texture_list.pop()
            gl.glDeleteTextures(texture)

    def standard_perspective(self):
        if self.perspective == PERSPECTIVE_STANDARD:
            return
        # aspect_ratio = cls.display_width / cls.display_height
        self.gl_height = 2.0
        self.gl_width = 2.0 * self.display_aspect
        self.gl_left = -1.0 * self.display_aspect
        self.fov_y = 45 / self.zoom
        self.fov_x = self.fov_y * self.display_aspect / self.zoom

        # left = cls.offset_x - 1.0 * cls.display_aspect / cls.zoom
        # right = cls.offset_x + 1.0 * cls.display_aspect / cls.zoom
        # top = cls.offset_y + 1.0 / cls.zoom
        # bottom = cls.offset_y - 1.0 / cls.zoom

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        # gluPerspective(cls.fov_y, cls.display_aspect, 0.1, 10.1)
        # glTranslatef(-cls.offset_x, -cls.offset_y, 0.0)

        gl.gluPerspective(45.0, 16.0 / 9.0, 0.1, 100.0)

        self.projection = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        # glScissor(0, display_yoffset, cls.display_width, cls.display_height)
        # glEnable(GL_SCISSOR_TEST)
        self.perspective = PERSPECTIVE_STANDARD

    def hd_perspective(self):
        if self.perspective == PERSPECTIVE_HD:
            return
        self.display_aspect = 16 / 9.0
        self.ortho_pscalex = 1920 / self.display_width
        # cls.ortho_pscalex = 1920 / cls.display_width * \
        #         (cls.display_width / cls.display_height)
        self.ortho_pscaley = 1080 / self.display_height
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        left = 0.0
        right = 1920.0
        top = 1080.0
        bottom = 0.0
        gl.glOrtho(left, right, bottom, top, -1.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        self.gl_left = left
        self.gl_right = right
        self.gl_height = 1080.0
        self.gl_width = 1920.0
        self.perspective = PERSPECTIVE_HD
        return self.ortho_pscalex, self.ortho_pscaley

    def ortho_perspective(self):
        if self.perspective == PERSPECTIVE_ORTHO:
            return
        self.display_aspect = 16 / 9.0
        self.ortho_pscalex = (
            2.0
            / self.display_width
            * (self.display_width / self.display_height)
        )
        self.ortho_pscaley = 2.0 / self.display_height
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        left = self.offset_x - 1.0 * self.display_aspect / self.zoom
        right = self.offset_x + 1.0 * self.display_aspect / self.zoom
        top = self.offset_y + 1.0 / self.zoom
        bottom = self.offset_y - 1.0 / self.zoom
        gl.glOrtho(left, right, bottom, top, -1.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        self.gl_left = -1.0 * self.display_aspect
        self.gl_right = 1.0 * self.display_aspect
        self.gl_height = 2.0  # * cls.display_aspect
        self.gl_width = 2.0 * self.display_aspect
        self.perspective = PERSPECTIVE_ORTHO
        return self.ortho_pscalex, self.ortho_pscaley

    def text(
        self,
        text,
        font,
        x,
        y,
        w=0,
        h=0,
        color=(1.0, 1.0, 1.0, 1.0),
        shadow=False,
        shadow_color=(0, 0, 0),
        halign=-1,
    ):
        if not text:
            return 0, 0
        # if len(color) == 3:
        #     color = (color[0], color[1], color[2], 1.0
        try:
            alpha = color[3]
        except IndexError:
            alpha = 1.0
        color = (
            int(round(color[0] * 255)),
            int(round(color[1] * 255)),
            int(round(color[2] * 255)),
        )

        cache_key = (text, hash(font), font.size, color, alpha)
        try:
            self.text_cache_history.remove(cache_key)
        except ValueError:
            texture = None
        else:
            texture, txtsize = self.text_cache[cache_key]

        fs_emu_blending(True)
        fs_emu_texturing(True)
        gl.glDisable(gl.GL_DEPTH_TEST)

        if texture:
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
        else:
            txtdata, txtsize = TextRenderer(font).render_text(text, color)
            texture = Render.get().create_texture()
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D,
                0,
                gl.GL_RGBA,
                txtsize[0],
                txtsize[1],
                0,
                gl.GL_BGRA,
                gl.GL_UNSIGNED_BYTE,
                txtdata,
            )
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR
            )
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR
            )
        tw, th = (
            txtsize[0] * self.ortho_pscalex,
            txtsize[1] * self.ortho_pscaley,
        )

        tx = x
        ty = y
        if w > 0:
            if tw > w:
                tw = w
            else:
                if halign == 0:
                    tx += (w - tw) / 2
        if h > 0:
            ty += (h - th) / 2
        # ts = 4 / cls.display_height  # Step

        # glDisable(GL_TEXTURE_RECTANGLE_ARB)

        # glTexEnv(GL_TEXTURE_2D, GL_MODULATE)
        # glDisable(GL_TEXTURE_RECTANGLE)
        # fs_emu_blending(True)
        gl.glBegin(gl.GL_QUADS)
        gl.glColor4f(alpha, alpha, alpha, alpha)

        gl.glTexCoord2f(0.0, 0.0)
        gl.glVertex2f(tx, ty + th)
        gl.glTexCoord2f(1.0, 0.0)
        gl.glVertex2f(tx + tw, ty + th)
        gl.glTexCoord2f(1.0, 1.0)
        gl.glVertex2f(tx + tw, ty)
        gl.glTexCoord2f(0.0, 1.0)
        gl.glVertex2f(tx, ty)

        # glRasterPos2f(tx, ty)
        # glDrawPixels(txtsize[0], txtsize[1], GL_RGBA, GL_UNSIGNED_BYTE,
        # txtdata)
        gl.glEnd()

        # fs_emu_blending(False)
        gl.glEnable(gl.GL_DEPTH_TEST)

        self.text_cache_history.append(cache_key)
        self.text_cache[cache_key] = texture, txtsize
        if len(self.text_cache) > TEXT_CACHE_SIZE:
            cache_key = self.text_cache_history.pop(0)
            texture, txtsize = self.text_cache.pop(cache_key)
            Render.get().delete_texture_list.append(texture)

        # # FIXME:
        # shadow = False
        #
        # glDisable(GL_DEPTH_TEST)
        # fs_emu_blending(True)
        # #text = current_menu.selected_item.title
        # #if shadow:
        # txtdata, txtsize = TextRenderer(font).render_text(text, shadow_color)
        # tw, th = txtsize[0] * ortho_pscalex, txtsize[1] * ortho_pscaley
        # tx = x
        # ty = y
        # if w > 0:
        #     tx = tx + (w - tw) / 2
        # if h > 0:
        #     ty = ty + (h - th) / 2
        # #tx = 0 - tw / 2
        # #ty = -0.67
        # ts = 4 / State.get().display_height # Step
        # if shadow:
        #     glPixelTransferf(GL_ALPHA_SCALE, 0.04)
        #     for fx, fy in [(1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (-1,
        #  0),
        #             (0, -1), (0, 1)]:
        #         glRasterPos2f(tx - fx * ts, ty - fy * ts)
        #         glDrawPixels(txtsize[0], txtsize[1], GL_RGBA,
        # GL_UNSIGNED_BYTE,
        #                 txtdata)
        #     glPixelTransferf(GL_ALPHA_SCALE, 0.01)
        #     for fx, fy in [(0, 2), (2, 0), (0, -2), (-2, 0),
        #             (1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2),
        #             (2, -1), (-1, -2), (-2, -1)]:
        #         glRasterPos2f(tx - fx * ts, ty - fy * ts)
        #         glDrawPixels(txtsize[0], txtsize[1], GL_RGBA,
        # GL_UNSIGNED_BYTE,
        #                 txtdata)
        # glPixelTransferf(GL_ALPHA_SCALE, alpha)
        # rendered = font.render(text, True, color)
        # txtsize = rendered.get_size()
        # txtdata = pygame.image.tostring(rendered, "RGBA", 1)
        # glRasterPos2f(tx, ty)
        # glDrawPixels(txtsize[0], txtsize[1], GL_RGBA, GL_UNSIGNED_BYTE,
        # txtdata)
        # #glPopAttrib()
        # glPixelTransferf(GL_ALPHA_SCALE, 1.0)
        # fs_emu_blending(False)
        # glEnable(GL_DEPTH_TEST)
        return tw, th

    def measure_text(self, text, font):
        tw, th = TextRenderer(font).get_size(text)
        return tw * self.ortho_pscalex, th * self.ortho_pscaley


State = Render
