import math
from game_center.glui.bottombar import render_bottom_bar, render_bottom_bar_transparent
from game_center.glui.displaylists import DisplayLists
from game_center.glui.menu import Menu
from game_center.glui.opengl import *
from game_center.glui.render import Render
from game_center.glui.state import State
from game_center.glui.texture import Texture
from game_center.glui.texturemanager import TextureManager


LIGHTING = False
MIN_WRAPAROUND_ITEMS = 9


def render_menu(menu, what=None, skip_center_item=False):
    if what is None:
        what = ["ITEMS", "SHADOWS"]
    Render.standard_perspective()
    item_data = _render_menu(menu, what, skip_center_item)
    return item_data


def _render_menu(menu, what=None, skip_center_item=False):
    if what is None:
        what = ["ITEMS", "SHADOWS"]
    # print "render menu with", len(menu), "items"
    position = menu.get_current_position()
    # selected = menu.get_selected_index()
    assert not skip_center_item

    # min_item = 0
    # max_item = len(menu) - 1
    num_items = len(menu)
    # i_position = min(max_item, int(round(position)))
    i_position = int(round(position))

    # print position, " (", selected, ")"
    # print "selected", selected

    # glEnable(GL_DEPTH_TEST)

    def get_item_position(ip_distance):
        inverse = ip_distance < 0
        ip_distance = abs(ip_distance)
        # y = 0.02 - 0.5
        # y = 0.243
        y = 0.293
        z = -3.1
        if ip_distance < 1.0:
            x = ip_distance * 0.8
            ip_rotation = -45.0 * ip_distance
            z = z + 0.6 - 0.6 * ip_distance
        else:
            # x = 0.8 + 0.15 * (ip_distance - 1.0)
            # x = 0.8 + 0.20 * (ip_distance - 1.0)
            x = 0.8 + 0.33 * (ip_distance - 1.0)
            ip_rotation = -45.0
        if inverse:
            return [-x, y, z], -ip_rotation
        else:
            return [x, y, z], ip_rotation
            
    def yield_render_item_sequence():
        if not skip_center_item:
            yield i_position
        # if MenuGameTransition.value == 0: #< 0.00001:
        # for i in range(9, 0, -1):
        for i in range(1, 10):
            # if (i_position - i) >= min_item:
            yield i_position - i
            # if (i_position + i) <= max_item:
            yield i_position + i

    def yield_image_file_sequence():
        for img in menu[i_position % num_items].get_image_files():
            yield img
        for i in range(1, 12):
            # if (i_position - i) >= min_item:
            #     for img in menu[i_position - i].get_image_files():
            #         yield img
            # if (i_position + i) <= max_item:
            #     for img in menu[i_position + i].get_image_files():
            #         yield img
            for img in menu[(i_position - i) % num_items].get_image_files():
                yield img
            for img in menu[(i_position + i) % num_items].get_image_files():
                yield img

    item_data = []
    if "ITEMS" in what:
        TextureManager.get().load_images(list(yield_image_file_sequence()))
        # TextureManager.get().load_textures(1)

        center_item = None
        light1_position = [-1.5, 0.2, -2.3, 1.0]
        light2_position = [-0.5, 2.5, -2.3, 1.0]
        # glDisable(GL_LIGHT2)

        if LIGHTING:
            glEnable(GL_LIGHTING)
            glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
            glLightfv(GL_LIGHT2, GL_POSITION, light2_position)
            glMaterialfv(GL_FRONT, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        glColor3f(1.0, 1.0, 1.0)

        # gloss_list = []
        # reflections = []
        # glColor3f(1.0, 1.0, 1.0)

        fs_emu_texturing(True)
        fs_emu_blending(False)

        for item_index in list(yield_render_item_sequence()):

            if num_items < MIN_WRAPAROUND_ITEMS:
                if not (0 <= item_index - (i_position // num_items *
                                           num_items) < num_items):
                    continue

            rel_index = item_index - position  # selected

            distance = abs(rel_index)
            # strength = 1.0

            glPushMatrix()

            pos, rotation = get_item_position(rel_index)
            
            glTranslate(*pos)
            scale = 1.0
            area = 0.9

            item = menu[item_index % num_items]
            height = math.sqrt(area / item.ratio)
            width = item.ratio * height

            if rel_index <= 0.0:
                spec = 0.8
            elif rel_index > 1.0:
                spec = 0.05
            else:
                spec = 0.8 - rel_index / 1.0 * 0.75
            if LIGHTING:
                glMaterialfv(GL_FRONT, GL_SPECULAR, (spec, spec, spec, 1.0))

            glRotate(rotation, 0.0, 1.0, 0.0)

            item.render(width, height)

            if not LIGHTING:
                if distance < 1.0:
                    gloss_alpha = 0.25 + distance * 0.25
                else:
                    gloss_alpha = 0.5
                render_item_gloss(
                    gloss_alpha, ratio=item.ratio, area=area)
            glPopMatrix()
            item_data.append(("ITEM", menu, item_index, pos, rotation, scale,
                              item.ratio, 1.0, area))

            # reflections.append((item, pos, rotation, width, height, spec * 0.3))

        if not center_item:
            State.center_item = None

        if LIGHTING:
            light1_position[1] = -light1_position[1]
            light2_position[1] = -light2_position[1]
            glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
            glLightfv(GL_LIGHT2, GL_POSITION, light2_position)
            # glLightfv(GL_LIGHT1, GL_POSITION, (-5.0, -1.5, 1.2, 1.0))
            # glLightfv(GL_LIGHT2, GL_POSITION, (-0.5, -5.0, 1.2, 1.0))
            glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.3, 0.3, 0.3, 0.0))

        # glColor3f(0.3, 0.3, 0.3)
        # for item, pos, rotation, width, height, spec in reflections:
        #     #if LIGHTING:
        #     #    glMaterialfv(GL_FRONT, GL_SPECULAR, (spec, spec, spec, 1.0))
        #     #else:
        #     #    glColor4f(0.33, 0.33, 0.33, 0.33)
        #     #    fs_emu_blending(True)
        #     glPushMatrix()
        #     glTranslate(*pos)
        #     glRotate(rotation, 0.0, 1.0, 0.0)
        #     item.render(width, height, reflection=True)
        #     glPopMatrix()

        if LIGHTING:
            glDisable(GL_LIGHTING)

    return item_data


def render_item_gloss(alpha, ratio=1.0, brightness=1.0, area=None):
    if State.max_ratio:
        ratio = min(State.max_ratio, ratio)
    if State.force_portrait and ratio > 1.0:
        ratio = 1.0 / ratio
    ba = brightness * alpha
    glColor4f(ba, ba, ba, alpha)
    fs_emu_blending(True)
    fs_emu_texturing(True)
    creating_list = DisplayLists.call_or_create("gloss", ratio)
    if not creating_list:
        return
    glPolygonOffset(0.0, -4.0)
    glEnable(GL_POLYGON_OFFSET_FILL)
    glDepthMask(False)
    # glBindTexture(GL_TEXTURE_2D, Texture.gloss)
    texture = Texture.gloss
    texture.bind()
    area = area or 0.8
    height = math.sqrt(area / ratio)
    width = ratio * height
    glTranslatef(-width / 2.0, -0.5, 0.0)
    glBegin(GL_QUADS)
    glTexCoord(0.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glTexCoord(1.0, 1.0)
    glVertex3f(width, 0.0, 0.0)
    glTexCoord(1.0, 0.0)
    glVertex3f(width, height, 0.0)
    glTexCoord(0.0, 0.0)
    glVertex3f(0.0, height, 0.0)
    glEnd()
    glPolygonOffset(0.0, 0.0)
    glDisable(GL_POLYGON_OFFSET_FILL)
    glDepthMask(True)
    # fs_emu_blending(False)
    if creating_list:
        glEndList()


def render_item_shadows(itemdata, front=False, back=True):
    Render.standard_perspective()
    # glEnable(GL_STENCIL_TEST)
    # glStencilFunc(GL_EQUAL, 1, 1)
    if front:
        glPolygonOffset(0.0, -4.0)
        glEnable(GL_POLYGON_OFFSET_FILL)
    elif back:
        glPolygonOffset(0.0, 4.0)
        glEnable(GL_POLYGON_OFFSET_FILL)
    glDepthMask(False)
    fs_emu_blending(True)
    fs_emu_texturing(True)
    glBindTexture(GL_TEXTURE_2D, Texture.shadow2)

    for type_, menu, item_index, pos, rotation, scale, ratio, brightness, \
            area in reversed(itemdata):
        glPushMatrix()
        glTranslate(*pos)
        glRotate(rotation, 0.0, 1.0, 0.0)
        glScalef(scale, scale, 1.0)
        render_item_shadow(ratio=ratio, brightness=brightness, area=area)
        glScalef(1.0, -1.0, 1.0)
        glTranslatef(0.0, 0.5, 0.0)
        # render_item_shadow(ratio=ratio, brightness=brightness * 0.33, area=area)
        render_item_shadow(ratio=ratio, brightness=brightness, area=area)
        glPopMatrix()

    glPolygonOffset(0.0, 0.0)
    glDisable(GL_POLYGON_OFFSET_FILL)
    glDepthMask(True)
    # fs_emu_blending(False)
    # glDisable(GL_STENCIL_TEST)


def render_item_shadow(ratio=1.0, brightness=1.0, area=None):
    if State.max_ratio:
        ratio = min(State.max_ratio, ratio)
    if State.force_portrait and ratio > 1.0:
        ratio = 1.0 / ratio
    glColor4f(brightness, brightness, brightness, brightness)
    creating_list = DisplayLists.call_or_create("shadow", ratio, area)
    if not creating_list:
        return
    glTranslatef(0.0, -0.5, 0.0)
    area = area or 0.8
    height = math.sqrt(area / ratio)
    width = ratio * height
    wh = width / 2
    t1 = 120 / 512
    t2 = (512 - 120) / 512
    glBegin(GL_QUADS)
    # left
    glTexCoord(0.0, t2)
    glVertex3f(-wh - 0.1, 0.02, 0.0)
    glTexCoord(t1, t2)
    glVertex3f(-wh + 0.02, 0.02, 0.0)
    glTexCoord(t1, t1)
    glVertex3f(-wh + 0.02, height - 0.02, 0.0)
    glTexCoord(0.0, t1)
    glVertex3f(-wh - 0.1, height - 0.02, 0.0)
    # top left
    glTexCoord(0.0, t1)
    glVertex3f(-wh - 0.1, height - 0.02, 0.0)
    glTexCoord(t1, t1)
    glVertex3f(-wh + 0.02, height - 0.02, 0.0)
    glTexCoord(t1, 0.0)
    glVertex3f(-wh + 0.02, height + 0.1, 0.0)
    glTexCoord(0.0, 0.0)
    glVertex3f(-wh - 0.1, height + 0.1, 0.0)
    # top
    glTexCoord(t1, t1)
    glVertex3f(-wh + 0.02, height - 0.02, 0.0)
    glTexCoord(t2, t1)
    glVertex3f(wh - 0.02, height - 0.02, 0.0)
    glTexCoord(t2, 0.0)
    glVertex3f(wh - 0.02, height + 0.1, 0.0)
    glTexCoord(t1, 0.0)
    glVertex3f(-wh + 0.02, height + 0.1, 0.0)
    # top right
    glTexCoord(t2, t1)
    glVertex3f(wh - 0.02, height - 0.02, 0.0)
    glTexCoord(1.0, t1)
    glVertex3f(wh + 0.1, height - 0.02, 0.0)
    glTexCoord(1.0, 0.0)
    glVertex3f(wh + 0.1, height + 0.1, 0.0)
    glTexCoord(t2, 0.0)
    glVertex3f(wh - 0.02, height + 0.1, 0.0)
    # right
    glTexCoord(t2, t2)
    glVertex3f(wh - 0.02, 0.02, 0.0)
    glTexCoord(1.0, t2)
    glVertex3f(wh + 0.1, 0.02, 0.0)
    glTexCoord(1.0, t1)
    glVertex3f(wh + 0.1, height - 0.02, 0.0)
    glTexCoord(t2, t1)
    glVertex3f(wh - 0.02, height - 0.02, 0.0)
    # bottom right
    glTexCoord(t2, 1.0)
    glVertex3f(wh - 0.02, -0.1, 0.0)
    glTexCoord(1.0, 1.0)
    glVertex3f(wh + 0.1, -0.1, 0.0)
    glTexCoord(1.0, t2)
    glVertex3f(wh + 0.1, 0.02, 0.0)
    glTexCoord(t2, t2)
    glVertex3f(wh - 0.02, 0.02, 0.0)
    # bottom
    glTexCoord(t1, 1.0)
    glVertex3f(-wh + 0.02, -0.1, 0.0)
    glTexCoord(t2, 1.0)
    glVertex3f(wh - 0.02, -0.1, 0.0)
    glTexCoord(t2, t2)
    glVertex3f(wh - 0.02, 0.02, 0.0)
    glTexCoord(t1, t2)
    glVertex3f(-wh + 0.02, 0.02, 0.0)
    # bottom left
    glTexCoord(0.0, 1.0)
    glVertex3f(-wh - 0.1, -0.1, 0.0)
    glTexCoord(t1, 1.0)
    glVertex3f(-wh + 0.02, -0.1, 0.0)
    glTexCoord(t1, t2)
    glVertex3f(-wh + 0.02, 0.02, 0.0)
    glTexCoord(0.0, t2)
    glVertex3f(-wh - 0.1, 0.02, 0.0)
    glEnd()
    # end list
    if creating_list:
        glEndList()


class ItemMenu(Menu):

    def __init__(self, title=""):
        Menu.__init__(self, title)

    def render(self):
        render_bottom_bar()
        result = render_menu(self)
        # FIXME: NO NEED TO RENDER THE BOTTOM PART OF THE WALL
        # -flag to render_wall?

        # from .gamemenu import render_wall
        # render_wall()
        return result

    def render_transparent(self, data):
        render_item_shadows(data)
        render_bottom_bar_transparent()
        pass
