from arcade.glui.font import BitmapFont
from arcade.glui.inputmenu import InputMenu
from arcade.glui.menu import Menu
from arcade.glui.navigatable import Navigatable
from arcade.glui.opengl import fs_emu_blending, fs_emu_texturing, gl
from arcade.glui.render import Render
from arcade.glui.state import State
from arcade.glui.texture import Texture
from arcade.glui.topmenu import GameCenterItem
from arcade.option import Option
from fsgamesys.context import fsgs
from fsgamesys.platforms.platform import PlatformHandler

GROUP_SPACING = 26
HEADING_TEXT_LEFT = 1920 - 560 + 40 + 20 - 28
ITEM_TEXT_LEFT = 1920 - 560 + 40 + 20
SIDEBAR_START_Y = 1080 - 90 - 50


# FIXME: REMOVE?
class Transition(object):
    def __init__(self):
        self.value = 0.0
        self.start = 0
        self.end = 0
        self.on_finish = None


enter_transition = Transition()
exit_transition = Transition()


def render_wall():  # brightness=1.0):
    # glClearColor(0.1, 0.1, 0.1, 1.0)
    # glClear(GL_DEPTH_BUFFER_BIT);
    Render.get().hd_perspective()
    # fs_emu_ortho();
    # fs_emu_blending(FALSE);
    # fs_emu_texturing(FALSE);
    z = -0.999

    # glPushMatrix()
    # glTranslate(0.0, 0.0, 1.0)

    # transition y-coordinate between floor and wall
    split = 361
    fs_emu_blending(False)
    fs_emu_texturing(False)
    gl.glBegin(gl.GL_QUADS)

    gl.glColor3f(39.0 / 255.0, 44.0 / 255.0, 51.0 / 255.0)
    gl.glVertex3f(0, split, z)
    gl.glVertex3f(1920, split, z)
    color = 0
    gl.glColor3f(color, color, color)
    gl.glVertex3f(1920, 1020, z)
    gl.glVertex3f(0, 1020, z)

    gl.glVertex3f(0, 1020, z)
    gl.glVertex3f(1920, 1020, z)
    gl.glVertex3f(1920, 1080, z)
    gl.glVertex3f(0, 1080, z)

    color = 0
    gl.glColor3f(color, color, color)
    gl.glVertex3f(0, 0, z)
    gl.glVertex3f(1920, 0, z)
    gl.glColor3f(20.0 / 255.0, 22.0 / 255.0, 26.0 / 255.0)
    gl.glVertex3f(1920, split, z)
    gl.glVertex3f(0, split, z)

    gl.glEnd()
    # fs_emu_texturing(True)

    # fs_emu_perspective();
    # double t_x = t0_x + (t1_x - t0_x) * g_menu_transition;
    # double t_y = t0_y + (t1_y - t0_y) * g_menu_transition;
    # double t_z = t0_z + (t1_z - t0_z) * g_menu_transition;
    # double r_a = r0_a + (r1_a - r0_a) * g_menu_transition;
    #
    # glScaled(16.0 / 9.0, 1.0, 1.0);
    # glTranslated(t_x, t_y, t_z);
    # glRotated(r_a, 0.0, 1.0, 0.0);


class GameMenu(Menu):
    def __init__(self, item):
        Menu.__init__(self)

        self.runner = None
        self.platform_handler = None
        self.last_menu_data = None

        self.temp_fix_configs(item)

        self.items.append(item)
        if self.use_game_center_item():
            self.top.left.append(GameCenterItem())
        # self.top.left.append(HomeItem())
        # self.top.left.append(MenuItem(item.title))
        self.top.set_selected_index(
            len(self.top.left) + len(self.top.right) - 1
        )

        self.context = None
        self.controller = None

        self.create_context()
        self.create_controller()
        print("GameMenu.__init__: controller is", self.controller)

        self.config_list = GameConfigList(self.runner, item)
        self.info_panel = GameInfoPanel()

        self.config_list.info_panel = self.info_panel
        # self.config_list.controller = self.controller
        self.info_panel.config_list = self.config_list

        self.navigatable = self.config_list

        # reset transitions
        enter_transition.start = State.get().time
        enter_transition.end = enter_transition.start + 0.2
        exit_transition.start = 0

    # noinspection PyMethodMayBeStatic
    def temp_fix_configs(self, item):
        # from fsgamesys.Database import Database
        # local_game_database = Database.get_instance()
        # game_database = fsgs.get_game_database()
        #
        # variants = local_game_database.find_game_variants_new(
        #     game_uuid=item.uuid)
        # print(variants)
        #
        # ordered_list = []
        # for variant in variants:
        #
        #     variant["like_rating"], variant["work_rating"] = \
        #         game_database.get_ratings_for_game(variant["uuid"])
        #     variant["personal_rating"], ignored = \
        #         local_game_database.get_ratings_for_game(variant["uuid"])
        #
        #     # user_rating = variant[5] or 0
        #     # global_rating = variant[3] or 0
        #     # user_rating = 0
        #     # global_rating = 0
        #
        #     variant_uuid = variant["uuid"]  # variant[2]
        #     variant_name = variant["name"]  # variant[1]
        #     variant_name = variant_name.replace("\n", " (")
        #     variant_name = variant_name.replace(" \u00b7 ", ", ")
        #     variant_name += ")"
        #     ordered_list.append(
        #         ((1 - bool(variant["have"]),
        #           1000 - variant["personal_rating"],
        #           1000 - variant["like_rating"]),
        #          (variant_uuid, variant_name, variant["database"])))
        # ordered_list.sort()
        # print("ordered variant list:")
        # for variant in ordered_list:
        #     print("-", variant[1][1])
        # item.configurations = [co[1] for co in ordered_list]
        variants = fsgs.get_ordered_game_variants(item.uuid)
        item.configurations = []
        for variant in variants:
            item.configurations.append(
                (
                    variant["uuid"],
                    variant["name"],
                    variant["database"],
                    variant["have"],
                )
            )

    def create_context(self):
        item = self.items[0]
        variant_uuid = item.configurations[0][0]
        database_name = item.configurations[0][2]
        print("\nitem:\n", item.configurations)
        print("\nitem[0]:\n", item.configurations[0])
        print("\n\nvariant_uuid =", variant_uuid, "\n\n")

        # print("configurations: ", item.configurations)
        # configs = sort_configurations(item.configurations)

        # configs = item.configurations
        # config = configs[0]
        # self.context = GameContext.create_for_game(
        #     item.platform, item.name, config)

        values = fsgs.game.set_from_variant_uuid(database_name, variant_uuid)

        # print("")
        # for key in sorted(values.keys()):
        #     print(" * {0} = {1}".format(key, values[key]))
        # print("")

        self.platform_handler = PlatformHandler.create(fsgs.game.platform.id)
        loader = self.platform_handler.get_loader(fsgs)
        fsgs.config.load(loader.load_values(values))

    def create_controller(self):
        # old_controller = self.controller
        # self.controller = GameHandler.create_for_game_context(
        #     self.context)

        self.runner = self.platform_handler.get_runner(fsgs)

        # self.controller = GameRunner()

    def recreate_controller(self):
        # self.create_controller()
        # self.config_list.set_controller(self.controller)
        print("recreate_controller, actually, just recreating game context")
        self.create_context()
        self.controller.context = self.context

    def render(self):
        # print("GameMenu.render")
        enter_transition.value = 1.0
        if enter_transition.start > 0:
            enter_transition.value = (
                State.get().time - enter_transition.start
            ) / (enter_transition.end - enter_transition.start)
            # prevent render from stopping when animating
            Render.get().dirty = True
        # transition goes from 1.0 ... 0.0
        # enter_transition.value = 1.0 - enter_transition.value
        # finished = 0
        if enter_transition.value >= 1.0:
            enter_transition.value = 1.0
            # finished = 1.0
            enter_transition.start = 0
            # enter_transition.on_finish()
            # return

        exit_transition.value = 0.0
        if exit_transition.start > 0:
            exit_transition.value = (
                State.get().time - exit_transition.start
            ) / (exit_transition.end - exit_transition.start)
            # prevent render from stopping when animating
            Render.get().dirty = True
        # transition goes from 1.0 ... 0.0
        exit_transition.value = 1.0 - exit_transition.value
        # finished = 0
        # if exit_transition.value <= 0.0:
        #     exit_transition.value = 0.0
        #     # finished = 1.0
        #     exit_transition.start = 0
        #     exit_transition.on_finish()
        #     return

        last_menu = State.get().history[-2]
        self.last_menu_data = last_menu.render()

        # self.top_menu_transition = transition

        # glClear(GL_DEPTH_BUFFER_BIT)
        # print(transition)
        # glEnable(GL_DEPTH_TEST)
        # glDepthMask(True)

        # render_wall(transition)
        # render_screen(transition)
        # if finished:
        #     # FIXME: defer to later via an event or similar?
        return None

    def render_transparent(self, data):
        # print("GameMenu.render_transparent")
        last_menu = State.get().history[-2]
        last_menu.render_transparent(self.last_menu_data)

        if exit_transition.value < 1.0:
            opacity = 1.0 - exit_transition.value
            opacity *= 1.25
            if opacity > 1.0:
                opacity = 1.0
            Render.get().hd_perspective()
            gl.glDisable(gl.GL_DEPTH_TEST)
            fs_emu_texturing(False)
            fs_emu_blending(True)
            gl.glBegin(gl.GL_QUADS)
            gl.glColor4f(0.0, 0.0, 0.0, opacity)
            gl.glVertex2f(0.0, 0.0)
            gl.glVertex2f(1920.0, 0.0)
            gl.glVertex2f(1920.0, 1020.0)
            gl.glVertex2f(0.0, 1020.0)
            gl.glEnd()
            gl.glEnable(gl.GL_DEPTH_TEST)

        alpha = enter_transition.value * 0.75

        Render.get().hd_perspective()
        gl.glDisable(gl.GL_DEPTH_TEST)
        fs_emu_texturing(False)
        fs_emu_blending(True)
        gl.glBegin(gl.GL_QUADS)
        gl.glColor4f(0.0, 0.0, 0.0, alpha)
        # Covers, left
        gl.glVertex2f(0.0, 366.0)
        gl.glVertex2f(746.0, 366.0)
        gl.glVertex2f(746.0, 1020.0)
        gl.glVertex2f(0.0, 1020.0)
        # Covers, right
        gl.glVertex2f(1920.0 - 746.0, 366.0)
        gl.glVertex2f(1920.0, 366.0)
        gl.glVertex2f(1920.0, 1020.0)
        gl.glVertex2f(1920.0 - 746.0, 1020.0)
        # Bottom
        gl.glColor4f(0.0, 0.0, 0.0, 0.50)
        gl.glVertex2f(0.0, 0.0)
        gl.glVertex2f(1920.0, 0.0)
        gl.glVertex2f(1920.0, 366.0)
        gl.glVertex2f(0.0, 366.0)
        gl.glEnd()
        gl.glEnable(gl.GL_DEPTH_TEST)

        transition = enter_transition.value
        if exit_transition.value < 1.0:
            # transition = exit_transition.value
            transition = 1.0 + 3.0 - exit_transition.value * 3.0
        # print("render, transition = ", transition)
        self.config_list.render(transition)

        if exit_transition.value <= 0.0:
            exit_transition.value = 0.0
            # finished = 1.0
            exit_transition.start = 0
            exit_transition.on_finish()

    def go_up(self):
        print("GameMenu.go_up")

    def go_down(self):
        print("GameMenu.go_down")

    def go_left(self, count=1):
        print("GameMenu.go_left")

    def go_right(self, count=1):
        print("GameMenu.go_right")

    def activate(self):
        print("GameMenu.activate")


class GameConfigList(Navigatable):
    def __init__(self, controller, game_item):
        self.index = 0
        self.runner = None
        self.game_item = game_item
        self.items = []
        self.set_controller(controller)

    def set_controller(self, controller):

        self.items = []
        self.items.append(Option.create_group("Game Control", -2.5))
        play_option = Option.create_play_option()
        self.items.append(play_option)

        self.items.append(Option.create_group("Variant", -2.5))
        config_option = Option.create_config_option()
        config_option.title = self.game_item.configurations[0][1]
        self.items.append(config_option)

        if len(self.game_item.configurations) > 1:
            self.items.append(Option.create_group("Other Variants", -2.5))
            for config in self.game_item.configurations[1:]:
                config_option = Option.create_config_option()
                config_option.title = config[1]
                self.items.append(config_option)

        # self.items = controller.options
        self.index = 0
        # set index to first non-group item
        for i, item in enumerate(self.items):
            if not item.group:
                self.index = i
                break
        self.runner = controller
        # self.controller = controller
        # print("GameConfigList.set_controller", id(self.controller))

    def go_up(self):
        old_index = self.index
        if self.index > 0:
            new_index = self.index - 1
            while new_index > 0 and self.items[new_index].group:
                new_index -= 1
        else:
            new_index = 0
        if new_index != old_index and not self.items[new_index].group:
            self.index = new_index
        else:
            Navigatable.go_up(self)

    def go_down(self):
        old_index = self.index
        if self.index < len(self.items) - 1:
            new_index = self.index + 1
            while (
                new_index < len(self.items) - 1 and self.items[new_index].group
            ):
                new_index += 1
        else:
            new_index = len(self.items) - 1
        if new_index != old_index and not self.items[new_index].group:
            self.index = new_index

    def go_left(self, count=1):
        print("GameConfigList.go_left")
        pass

    def go_right(self, count=1):
        pass

    def activate(self):
        # Hack for variants
        if self.index > 4:
            # Put chosen configuration at the top
            temp_config = self.game_item.configurations[0]
            # temp_config = self.game_item.configurations[self.index - 4 + 1]
            self.game_item.configurations[0] = self.game_item.configurations[
                self.index - 4
            ]
            self.game_item.configurations[self.index - 4] = temp_config
            # Put chosen variant item at the top
            temp = self.items[3]
            self.items[3] = self.items[self.index]
            self.items[self.index] = temp
            # Select play game option
            self.index = 1
            # Hackish, please clean up...
            print("ACTIVE CONFIGURATION:", self.game_item.configurations[0])
            State.get().current_menu.create_context()
            State.get().current_menu.create_controller()
            self.runner = State.get().current_menu.runner
            return
        result = self.items[self.index].activate()
        if result == "PLAY":

            # noinspection PyDecorator
            # @staticmethod
            def show_input():
                # print("Create input menu, controller = ", id(self.controller))
                # new_menu = InputMenu(self.game_item, self.controller)
                # State.get().history.append(new_menu)
                # # FIXME
                # from .window import set_current_menu
                # set_current_menu(new_menu)

                print("Create input menu, runner = ", id(self.runner))
                new_menu = InputMenu(self.game_item, self.runner)
                State.get().history.append(new_menu)
                # FIXME
                from arcade.glui.window import set_current_menu

                set_current_menu(new_menu)

            exit_transition.start = State.get().time
            exit_transition.end = exit_transition.start + 0.5
            exit_transition.on_finish = show_input

    def render(self, transition=1.0):
        Render.get().hd_perspective()

        # w = 560
        # h = 92
        # x = 1920 - w * transition
        # y = 1080 - 60 - h
        # y = 1080 - 60 - h - 44
        # z = -0.9

        # item_top = 1080 - 90 - 50
        # item_left = 1920 - 560 + 40

        dx = Texture.sidebar_background_shadow.w * (1.0 - transition)

        gl.glPushMatrix()
        gl.glTranslate(0.0, 0.0, 0.7)
        # glTranslated((1.0 - transition) * g_tex_sidebar_background->width,
        # 0, 0)
        # fs_emu_set_texture(g_tex_sidebar_background)
        # fs_emu_render_texture_with_size(g_tex_sidebar_background,
        #         1920 - g_tex_sidebar_background->width,
        #         0, g_tex_sidebar_background->width,
        #         g_tex_sidebar_background->height)
        # fs_emu_render_sidebar()
        fs_emu_blending(True)
        fs_emu_texturing(True)
        gl.glDepthMask(False)
        Texture.sidebar_background_shadow.render(
            1920 - Texture.sidebar_background_shadow.w * transition,
            0,
            Texture.sidebar_background_shadow.w,
            Texture.sidebar_background_shadow.h,
        )
        if transition > 1.0:
            padding = 1920
            Texture.sidebar_background.render(
                1920
                - Texture.sidebar_background_shadow.w * transition
                + Texture.sidebar_background_shadow.w,
                0,
                1920 + padding,
                Texture.sidebar_background.h,
            )
        gl.glDepthMask(True)
        gl.glPopMatrix()

        y = SIDEBAR_START_Y
        for i, item in enumerate(self.items):
            if item.group:
                if i > 0:
                    y -= GROUP_SPACING
            selected = i == self.index and State.get().navigatable == self
            # z = 0.71
            fs_emu_texturing(False)
            gl.glDisable(gl.GL_DEPTH_TEST)

            if selected:
                fg_color = [1.0, 1.0, 1.0, 1.0]
                # gl.glBegin(gl.GL_QUADS)
                #
                # gl.glColor3f(0.00, 0x99 / 0xff, 0xcc / 0xff)
                # gl.glVertex3f(x, y - 18, z)
                # gl.glVertex3f(x + w, y - 18, z)
                # gl.glVertex3f(x + w, y + h - 4, z)
                # gl.glVertex3f(x, y + h - 4, z)
                # # glColor3f(0.6, 0.6, 0.6)
                # # glVertex3f(x, y + 4, z)
                # # glVertex3f(x + w, y + 4, z)
                # # glVertex3f(x + w, y + h, z)
                # # glVertex3f(x, y + h, z)
                # gl.glEnd()
                fs_emu_blending(True)
                fs_emu_texturing(True)
                gl.glDepthMask(False)
                Texture.item_background.render(1920 - 540 + 13 + dx, y - 18)
                gl.glDepthMask(True)
            else:
                fg_color = [1.0, 1.0, 1.0, 1.0]

            # glBegin(GL_QUADS)
            # glColor3f(0.4, 0.4, 0.4)
            # glVertex3f(x, y, z)
            # glVertex3f(x + w, y, z)
            # glVertex3f(x + w, y + 4, z)
            # glVertex3f(x, y + 4, z)
            # glEnd()
            # fs_emu_texturing(True)

            if i > 0:
                fg_color[3] *= 0.35

            text = item.title

            # FIXME: REMOVE
            # fs_emu_blending(False)
            # fs_emu_blending(True)

            if item.group:
                BitmapFont.menu_font.render(
                    text,
                    HEADING_TEXT_LEFT + dx,
                    y + 14,
                    r=0.0,
                    g=0x99 / 0xFF,
                    b=0xCC / 0xFF,
                )
                x, _ = BitmapFont.menu_font.measure(text)
                x += HEADING_TEXT_LEFT + 12
                fs_emu_blending(True)
                fs_emu_texturing(True)
                # gl.glDepthMask(False)
                Texture.heading_strip.render(x + dx, y + 14, 1920 - x, 32)
            else:
                BitmapFont.menu_font.render(text, ITEM_TEXT_LEFT + dx, y + 14)
            gl.glEnable(gl.GL_DEPTH_TEST)
            # text = item.title.upper()
            # tw, th = Render.get().text(text, Font.main_path_font,
            #         x + 40, y + 43, color=fg_color)
            # text = item.subtitle.upper()
            # fg_color[3] = fg_color[3] * 0.4
            # text = item.title.upper()
            # tw, th = Render.get().text(text, Font.list_subtitle_font,
            #         x + 40, y + 18, color=fg_color)
            y -= 54

        # Gradually erase menu items when transitioning
        if transition > 1.0:
            gl.glDisable(gl.GL_DEPTH_TEST)
            # tr = (transition - 1.0) / 3.0
            alpha = max(0.0, (transition - 1.0) / 2.0)
            Texture.sidebar_background.render(
                1920 - Texture.sidebar_background_shadow.w * transition + 200,
                0,
                1920,
                Texture.sidebar_background.h,
                opacity=alpha,
            )
            gl.glEnable(gl.GL_DEPTH_TEST)


class GameInfoPanel(Navigatable):
    def __init__(self):
        self.index = 0
        self.position = 0
        self.config_list = []

    def go_up(self):
        print("GameInfoPanel.go_up")
        if self.index == 0 and self.position == 0:
            Navigatable.go_up(self)

    def go_down(self):
        print("GameInfoPanel.go_down")

    def go_left(self, count=1):
        print("GameInfoPanel.go_left")

    def go_right(self, count=1):
        State.get().navigatable = self.config_list

    def render(self):
        z = -0.999
        fs_emu_texturing(False)
        fs_emu_blending(False)
        gl.glBegin(gl.GL_QUADS)
        gl.glColor3f(0.0, 0.0, 0.0)
        # glVertex3f(0, 365, z)
        # glVertex3f(1270, 365, z)
        gl.glVertex3f(0, 400, z)
        gl.glVertex3f(1270, 400, z)
        gl.glColor3f(0.25, 0.25, 0.25)
        gl.glVertex3f(1270, 1080 - 60, z)
        gl.glVertex3f(0, 1080 - 60, z)
        gl.glEnd()
        # fs_emu_texturing(True)
