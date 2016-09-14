import random

from arcade.glui.font import Font
from arcade.glui.opengl import gl, fs_emu_blending, fs_emu_texturing
from arcade.glui.render import Render
from arcade.glui.state import State
from arcade.glui.texture import Texture
from fsgs.platform import PlatformHandler

COORDS = 0.0, 1.0, 1.0, 0.0


def rectangle(x, y, w, h, z=0.0):
    # gl.glBegin(gl.GL_QUADS)
    gl.glVertex3f(x, y, z)
    gl.glVertex3f(x + w, y, z)
    gl.glVertex3f(x + w, y + h, z)
    gl.glVertex3f(x, y + h, z)
    # gl.glEnd()


def texture_rectangle(x, y, w, h, z=0.0, s1=0.0, s2=1.0, t1=1.0, t2=0.0):
    gl.glBegin(gl.GL_QUADS)
    gl.glTexCoord(s1, t1)
    gl.glVertex3f(x, y, z)
    gl.glTexCoord(s2, t1)
    gl.glVertex3f(x + w, y, z)
    gl.glTexCoord(s2, t2)
    gl.glVertex3f(x + w, y + h, z)
    gl.glTexCoord(s1, t2)
    gl.glVertex3f(x, y + h, z)
    gl.glEnd()


def static():
    s1 = random.uniform(0.0, 0.65)
    s2 = s1 + 0.35
    t1 = random.uniform(0.0, 0.65)
    t2 = t1 + 0.35
    # w, h = Texture.static.size
    # return Texture.static, (s1 * w, s2 * w, t1 * h, t2 * h)
    return Texture.static, (s1, s2, t1, t2)


last_item_id = None
item_time = 0


def render_bottom_bar_transparent():
    Render.get().hd_perspective()
    fs_emu_blending(True)
    Texture.bottom_bar.render(0, 0, 1920, 380, 0.3, opacity=1.0)
    item = State.get().current_menu.selected_item
    render_bottom_bar_text(item)


def render_bottom_bar():
    Render.get().hd_perspective()
    item = State.get().current_menu.selected_item
    render_bottom_bar_screens(item)


def render_bottom_bar_screens(item):
    global last_item_id
    global item_time
    if id(item) != last_item_id:
        last_item_id = id(item)
        item_time = State.get().time

    gl.glColor3f(1.0, 1.0, 1.0)
    fs_emu_texturing(True)
    fs_emu_blending(False)

    for i in range(3, -1, -1):
        if State.get().time - item_time > 0.1 + 0.05 * i:
            texture = item.get_screen_texture(2 + i)
        else:
            texture = None
        if texture:
            # coords = (0, texture.w, texture.h, 0)
            coords = COORDS
        else:
            texture, coords = static()
            # While rendering static, we must continue rendering.
            Render.get().dirty = True

        texture.bind()
        texture_rectangle(4 + 539 + 345 * i, 34, 308, 193, 0.2, *coords)
    if State.get().time - item_time > 0.1:
        texture = item.get_screen_texture(1)
    else:
        texture = None
    if texture:
        coords = COORDS
    else:
        texture, coords = static()
        # While rendering static, we must continue rendering.
        Render.get().dirty = True
    texture.bind()

    texture_rectangle(34, 34, 472, 295, 0.2, *coords)


def render_bottom_bar_text(item):
    strength = 0.9
    x = 544
    y = 290

    title = item.title.upper()
    if title:
        Render.get().text(title, Font.title_font, x, y, 1920 - x - 170,
                          shadow=True, color=(1.0, 1.0, 1.0, 1.0 * strength))

    year_text = str(getattr(State.get().current_menu.selected_item,
                            "year", "") or "").upper()
    if year_text:
        tw, th = Render.get().measure_text(year_text, Font.title_font)
        Render.get().text(year_text, Font.title_font, 1920 - 30 - tw, y, 0,
                          shadow=True, color=(1.0, 1.0, 1.0, 1.0 * strength))

    color = (0x6e / 0xff, 0x8b / 0xff, 0x96 / 0xff, 1.0)
    y = 258
    text_str = ""
    companies = set()
    publisher_text = (getattr(State.get().current_menu.selected_item,
                              "publisher", "") or "").upper()
    for text in publisher_text.split("/"):
        text = text.strip()
        if text:
            if text not in companies:
                text_str = text_str + u" \u00b7 " + text
                companies.add(text)
    developer_text = (getattr(State.get().current_menu.selected_item,
                              "developer", "") or "").upper()
    for text in developer_text.split("/"):
        text = text.strip()
        if text:
            if text not in companies:
                text_str = text_str + u" \u00b7 " + text
                companies.add(text)
    if len(text_str) > 3:
        text_str = text_str[3:]  # remove initial middle dot
        Render.get().text(text_str, Font.subtitle_font, x, y, 0,
                          shadow=True, color=color)

    platform_str = str(
        getattr(State.get().current_menu.selected_item, "platform", "") or "")
    if platform_str:
        platform_str = PlatformHandler.get_platform_name(platform_str).upper()
    if len(platform_str) >= 3:
        tw, th = Render.get().measure_text(platform_str, Font.subtitle_font)
        Render.get().text(platform_str, Font.subtitle_font, 1920 - 30 - tw, y,
                          0,
                          shadow=True, color=color)
    return
