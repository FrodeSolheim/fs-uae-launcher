from game_center.glui.opengl import gl, fs_emu_texturing, fs_emu_blending
from game_center.glui.text import TextRenderer


DISPLAY_FPS = False
DISPLAY_SYNC = False

PERSPECTIVE_STANDARD = 1
PERSPECTIVE_ORTHO = 2
PERSPECTIVE_HD = 3

TEXT_CACHE_SIZE = 100

text_cache_history = []
text_cache = {}


class Render(object):

    currently_ingame = False

    # Render items
    display_sync = DISPLAY_SYNC
    display_fps = DISPLAY_FPS
    display_last_iteration = 0
    display_width = 0
    display_height = 0
    last_time_str = ""

    # State items
    
    time = 0
    down_navigatable = None
    dialog = None
    dialog_time = 0.0
    
    # ...

    quit = False
    allow_minimize = True

    history = []

    zoom = 1.0
    offset_x = 0.0
    offset_y = 0.0

    frame_number = 0
    idle_from = None
    dirty = True
    non_dirty_state = False
    twice = False
    fade_start = 0.0
    fade_end = 0.0
    fade_splash = True
    fade_from = (0, 0, 0, 0)
    fade_to = (0, 0, 0, 0)
    opacity = 1.0
    perspective = 0

    center_item = None
    center_item_time = 0

    items_brightness = 0.8
    # items_brightness_target = 1.0
    # items_brightness_speed = 1.0
    navigatable = None
    current_menu = None
    current_game = None
    config_menu = None
    top_menu = None

    hide_mouse_time = 0
    mouse_visible = True
    # options
    force_portrait = False
    max_ratio = None
    # max_ratio = 1.0

    delete_texture_list = []
    unused_texture_list = []

    @classmethod
    def create_texture(cls):
        if len(cls.unused_texture_list) == 0:
            cls.unused_texture_list.extend(gl.glGenTextures(50))
        return cls.unused_texture_list.pop()

    @classmethod
    def delete_textures(cls):
        # for t in cls.delete_texture_list:
        #     glDeleteTextures([t])

        gl.glDeleteTextures(cls.delete_texture_list)
        cls.delete_texture_list[:] = []

        # cls.unused_texture_list.extend(cls.delete_texture_list)
        # cls.delete_texture_list[:] = []
        # pass

        if len(cls.delete_texture_list) > 0:
            texture = cls.delete_texture_list.pop()
            gl.glDeleteTextures(texture)

    @classmethod
    def standard_perspective(cls):
        if cls.perspective == PERSPECTIVE_STANDARD:
            return
        # aspect_ratio = cls.display_width / cls.display_height
        cls.gl_height = 2.0
        cls.gl_width = 2.0 * cls.display_aspect
        cls.gl_left = -1.0 * cls.display_aspect
        cls.fov_y = 45 / cls.zoom
        cls.fov_x = cls.fov_y * cls.display_aspect / cls.zoom

        # left = cls.offset_x - 1.0 * cls.display_aspect / cls.zoom
        # right = cls.offset_x + 1.0 * cls.display_aspect / cls.zoom
        # top = cls.offset_y + 1.0 / cls.zoom
        # bottom = cls.offset_y - 1.0 / cls.zoom

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        
        # gluPerspective(cls.fov_y, cls.display_aspect, 0.1, 10.1)
        # glTranslatef(-cls.offset_x, -cls.offset_y, 0.0)
        
        gl.gluPerspective(45.0, 16.0 / 9.0, 0.1, 100.0)
        
        cls.projection = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        # glScissor(0, display_yoffset, cls.display_width, cls.display_height)
        # glEnable(GL_SCISSOR_TEST)
        cls.perspective = PERSPECTIVE_STANDARD

    @classmethod
    def hd_perspective(cls):
        if cls.perspective == PERSPECTIVE_HD:
            return
        cls.display_aspect = 16 / 9.0
        cls.ortho_pscalex = 1920 / cls.display_width
        # cls.ortho_pscalex = 1920 / cls.display_width * \
        #         (cls.display_width / cls.display_height)
        cls.ortho_pscaley = 1080 / cls.display_height
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        left = 0.0
        right = 1920.0
        top = 1080.0
        bottom = 0.0
        gl.glOrtho(left, right, bottom, top, -1.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        cls.gl_left = left
        cls.gl_right = right
        cls.gl_height = 1080.0
        cls.gl_width = 1920.0
        cls.perspective = PERSPECTIVE_HD
        return cls.ortho_pscalex, cls.ortho_pscaley

    @classmethod
    def ortho_perspective(cls):
        if cls.perspective == PERSPECTIVE_ORTHO:
            return
        cls.display_aspect = 16 / 9.0
        cls.ortho_pscalex = (2.0 / cls.display_width *
                             (cls.display_width / cls.display_height))
        cls.ortho_pscaley = 2.0 / cls.display_height
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        left = cls.offset_x - 1.0 * cls.display_aspect / cls.zoom
        right = cls.offset_x + 1.0 * cls.display_aspect / cls.zoom
        top = cls.offset_y + 1.0 / cls.zoom
        bottom = cls.offset_y - 1.0 / cls.zoom
        gl.glOrtho(left, right, bottom, top, -1.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        cls.gl_left = -1.0 * cls.display_aspect
        cls.gl_right = 1.0 * cls.display_aspect
        cls.gl_height = 2.0  # * cls.display_aspect
        cls.gl_width = 2.0 * cls.display_aspect
        cls.perspective = PERSPECTIVE_ORTHO
        return cls.ortho_pscalex, cls.ortho_pscaley

    @classmethod
    def text(cls, text, font, x, y, w=0, h=0, color=(1.0, 1.0, 1.0, 1.0),
             shadow=False, shadow_color=(0, 0, 0), halign=-1):
        if not text:
            return 0, 0
        # if len(color) == 3:
        #     color = (color[0], color[1], color[2], 1.0
        try:
            alpha = color[3]
        except IndexError:
            alpha = 1.0
        color = (int(round(color[0] * 255)),
                 int(round(color[1] * 255)),
                 int(round(color[2] * 255)))

        cache_key = (text, hash(font), font.size, color, alpha)
        try:
            text_cache_history.remove(cache_key)
        except ValueError:
            texture = None
        else:
            texture, txtsize = text_cache[cache_key]

        fs_emu_blending(True)
        fs_emu_texturing(True)
        gl.glDisable(gl.GL_DEPTH_TEST)

        if texture:
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
        else:
            txtdata, txtsize = TextRenderer(font).render_text(text, color)
            texture = Render.create_texture()
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, txtsize[0], txtsize[1],
                0, gl.GL_BGRA, gl.GL_UNSIGNED_BYTE, txtdata)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        tw, th = txtsize[0] * cls.ortho_pscalex, txtsize[1] * cls.ortho_pscaley

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
        # glDrawPixels(txtsize[0], txtsize[1], GL_RGBA, GL_UNSIGNED_BYTE, txtdata)
        gl.glEnd()
        
        # fs_emu_blending(False)
        gl.glEnable(gl.GL_DEPTH_TEST)

        text_cache_history.append(cache_key)
        text_cache[cache_key] = texture, txtsize
        if len(text_cache) > TEXT_CACHE_SIZE:
            cache_key = text_cache_history.pop(0)
            texture, txtsize = text_cache.pop(cache_key)
            Render.delete_texture_list.append(texture)

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
        # ts = 4 / State.display_height # Step
        # if shadow:
        #     glPixelTransferf(GL_ALPHA_SCALE, 0.04)
        #     for fx, fy in [(1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (-1, 0),
        #             (0, -1), (0, 1)]:
        #         glRasterPos2f(tx - fx * ts, ty - fy * ts)
        #         glDrawPixels(txtsize[0], txtsize[1], GL_RGBA, GL_UNSIGNED_BYTE,
        #                 txtdata)
        #     glPixelTransferf(GL_ALPHA_SCALE, 0.01)
        #     for fx, fy in [(0, 2), (2, 0), (0, -2), (-2, 0),
        #             (1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2),
        #             (2, -1), (-1, -2), (-2, -1)]:
        #         glRasterPos2f(tx - fx * ts, ty - fy * ts)
        #         glDrawPixels(txtsize[0], txtsize[1], GL_RGBA, GL_UNSIGNED_BYTE,
        #                 txtdata)
        # glPixelTransferf(GL_ALPHA_SCALE, alpha)
        # rendered = font.render(text, True, color)
        # txtsize = rendered.get_size()
        # txtdata = pygame.image.tostring(rendered, "RGBA", 1)
        # glRasterPos2f(tx, ty)
        # glDrawPixels(txtsize[0], txtsize[1], GL_RGBA, GL_UNSIGNED_BYTE, txtdata)
        # #glPopAttrib()
        # glPixelTransferf(GL_ALPHA_SCALE, 1.0)
        # fs_emu_blending(False)
        # glEnable(GL_DEPTH_TEST)
        return tw, th

    @classmethod
    def measure_text(cls, text, font):
        tw, th = TextRenderer(font).get_size(text)
        return tw * cls.ortho_pscalex, th * cls.ortho_pscaley


State = Render
