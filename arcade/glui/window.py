import ctypes
import os
import sys
import time
from collections import deque

from arcade.gamecenter import GameCenter
from arcade.gamecentersettings import ArcadeSettings
from arcade.glui.animation import AnimateValueBezier, AnimationSystem
from arcade.glui.bezier import Bezier
from arcade.glui.constants import TOP_HEIGHT
from arcade.glui.displaylists import DisplayLists
from arcade.glui.font import BitmapFont, Font
from arcade.glui.imageloader import ImageLoader
from arcade.glui.input import InputHandler
from arcade.glui.itemmenu import ItemMenu
from arcade.glui.items import (
    AllMenuItem,
    ListItem,
    MenuItem,
    NoItem,
    PlatformItem,
)
from arcade.glui.notificationrender import NotificationRender
from arcade.glui.opengl import fs_emu_blending, fs_emu_texturing, gl
from arcade.glui.render import Render
from arcade.glui.sdl import SDL_IsMinimized
from arcade.glui.settings import Settings
from arcade.glui.state import State
from arcade.glui.texture import Texture
from arcade.glui.texturemanager import TextureManager

# from arcade.main import Main
from arcade.resources import logger, resources
from fsbc import settings
from fscore.system import System
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.options.option import Option
from fsgamesys.platforms.platform import PlatformHandler
from fsgamesys.util.gamenameutil import GameNameUtil

# FIXME: rename to manager or director or somethign
main_window = None

# ENABLE_VSYNC = Config.get_bool("Menu/VSync", True)
ENABLE_VSYNC = "--vsync" in sys.argv
ALWAYS_RENDER = True
# IDLE = Config.get_bool("Menu/Idle", 1)
IDLE = 1
if "--no-idle" in sys.argv:
    IDLE = 0
# Render.get().display_fps = pyapp.user.ini.get_bool("Menu/ShowFPS", False)
# LIGHTING = Config.get_bool("Menu/Lighting", False)
LIGHTING = False
RENDER_DEBUG_SQUARES = 0
if "--render-debug-squares" in sys.argv:
    RENDER_DEBUG_SQUARES = 1
SEARCH_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 -:.,"
)
CONFIG_SEPARATION = 0.15
ANIMATION_SETTLE_TIME_1 = 1.0
ANIMATION_SETTLE_TIME_2 = 2.0

force_display_ratio = None
display = None
real_display_height = 0
current_menu = None
last_menu = None
last_game = None


def get_current_time():
    return time.time()


def set_current_menu(menu):
    if not isinstance(menu, SearchResultsMenu):
        menu.search_text = ""

    global current_menu
    if len(menu) == 0:
        menu.append(NoItem())
    current_menu = menu
    State.get().current_menu = menu
    if menu.navigatable:
        State.get().navigatable = menu.navigatable
    else:
        State.get().navigatable = menu
    State.get().top_menu = menu.top
    State.get().down_navigatable = None
    Render.get().dirty = True


# WINDOWED_SIZE = [1024, 640]  # 16:10
# WINDOWED_SIZE = (1024, 576)  # 16:9
# WINDOWED_SIZE = [1024, 768]  # 4:3
# WINDOWED_SIZE = [960, 540]  # 16:9
WINDOWED_SIZE = [1280, 720]  # 16:9

RENDER_GAME = ["IMAGE", "REFLECTIONS", "SCREENSHOTS"]
RENDER_GAME_OVERLAY = ["TITLE", "HEADER"]

# USE_MENU_TRANSITIONS = pyapp.user.ini.get_bool("Menu/Transitions", True)
# if "--disable-shaders" in sys.argv:
#     USE_MENU_TRANSITIONS = False
USE_MENU_TRANSITIONS = False
FIELD_COLOR = 0.1
WALL_COLOR = 0.0
# IDLE_EVENT = pygame.NUMEVENTS - 1
DEFAULT_ITEM_BRIGHTNESS = 0.8


class MenuGameTransition(object):
    value = 0.0


class MenuForwardTransition(object):
    # must be initially set to 1 because this indicates that
    # the transition is done / not in progress
    value = 1.0


class MenuBackwardTransition(object):
    # must be initially set to 1 because this indicates that
    # the transition is done / not in progress
    value = 1.0


class ScreenshotTransition(object):
    anim = None
    # must be initially set to 1 because this indicates that
    # the transition is done / not in progress
    value = 1.0


class RunTransition(object):
    value = 0.0


class Mouse(object):
    items = []
    focus = None

    @classmethod
    def set_visible(cls, visible=True):
        assert visible is not None
        # if State.get().mouse_visible == visible:
        #     return
        # if not visible:
        #     cls.focus = None
        # pygame.mouse.set_visible(visible)
        # State.get().mouse_visible = visible
        print("Mouse.set_visible not implemented")


def set_items_brightness(brightness, duration=1.0, delay=0.0):
    State.get().items_brightness_anim = AnimateValueBezier(
        (State, "items_brightness"),
        State.get().items_brightness,
        State.get().time + delay,
        State.get().items_brightness,
        State.get().time + delay,
        brightness,
        State.get().time + delay + duration,
        brightness,
        State.get().time + delay + duration,
    )


def compile_shader(source, shader_type):
    shader = gl.glCreateShaderObjectARB(shader_type)
    gl.glShaderSourceARB(shader, source)
    gl.glCompileShaderARB(shader)
    try:
        status = ctypes.c_int()
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ctypes.byref(status))
        status = status.value
    except TypeError:
        status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
    if not status:
        print_log(shader)
        gl.glDeleteObjectARB(shader)
        raise ValueError("Shader compilation failed")
    return shader


def compile_program(vertex_source, fragment_source):
    vertex_shader = None
    fragment_shader = None
    program = gl.glCreateProgram()
    if vertex_source:
        print("compile vertex shader")
        vertex_shader = compile_shader(vertex_source, gl.GL_VERTEX_SHADER)
        gl.glAttachShader(program, vertex_shader)
    if fragment_source:
        print("compile fragment shader")
        fragment_shader = compile_shader(
            fragment_source, gl.GL_FRAGMENT_SHADER
        )
        gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)
    status = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
    if status == gl.GL_FALSE:
        print("could not link shader program")
        print(gl.glGetProgramInfoLog(program))
        sys.exit(1)
    if vertex_shader:
        gl.glDeleteShader(vertex_shader)
    if fragment_shader:
        gl.glDeleteShader(fragment_shader)
    return program


def print_log(shader):
    length = ctypes.c_int()
    gl.glGetShaderiv(shader, gl.gl.GL_INFO_LOG_LENGTH, ctypes.byref(length))
    if length.value > 0:
        shader_log = gl.glGetShaderInfoLog(shader)
        print(shader_log)
        sys.exit(1)


texture_program = None
color_program = None
premultiplied_texture_program = None


def compile_programs():
    global texture_program, color_program, premultiplied_texture_program
    vertex_shader = None

    color_program = compile_program(
        vertex_shader,
        [
            """
void main()
{
vec4 s = gl_Color;
float extra_alpha = 1.0;
//float extra_alpha = gl_TextureEnvColor[0].a;
float a = s.a * extra_alpha;
gl_FragColor.a = a;
gl_FragColor.r = s.r*a;
gl_FragColor.g = s.g*a;
gl_FragColor.b = s.b*a;
}
            """
        ],
    )

    texture_program = compile_program(
        vertex_shader,
        [
            """
uniform sampler2D texture;

void main()
{
vec4 s = texture2D(texture,gl_TexCoord[0].st);
//float extra_alpha = 1.0;
//float extra_alpha = gl_TextureEnvColor[0].a;
float opacity = gl_Color.a;
float a = s.a * opacity;
gl_FragColor.a = a;
gl_FragColor.r = s.r * a;
gl_FragColor.g = s.g * a;
gl_FragColor.b = s.b * a;
}
"""
        ],
    )

    premultiplied_texture_program = compile_program(
        vertex_shader,
        [
            """
uniform sampler2D texture;

void main()
{
vec4 s = texture2D(texture,gl_TexCoord[0].st);
//float extra_alpha = 1.0;
//float extra_alpha = gl_TextureEnvColor[0].a;
float opacity = gl_Color.a;
gl_FragColor.a = s.a * opacity;
gl_FragColor.r = s.r * opacity;
gl_FragColor.g = s.g * opacity;
gl_FragColor.b = s.b * opacity;
}
"""
        ],
    )


def enable_texture_shader():
    fs_emu_blending(True)
    gl.glBlendFunc(gl.GL_ONE, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glUseProgram(texture_program)


def disable_shader():
    gl.glUseProgram(0)


def set_program(program):
    if not program:
        gl.glUseProgram(0)
    else:
        gl.glUseProgram(program)


def enter_menu(result, replace=False):
    print("enter_menu", result, "replace", replace)
    print("   menu parent_menu", result.parent_menu)

    if replace:
        State.get().history.pop()
    c_menu = State.get().history[-1]
    result.parents[:] = c_menu.parents
    result.parents.append(c_menu)
    print("   menu parents    ", result.parents)
    State.get().history.append(result)
    set_current_menu(result)


def create_main_menu():
    new_menu = AllMenuItem().activate(None)
    if len(new_menu) == 0:
        new_menu.append(NoItem())
    return new_menu


def recreate_main_menu_if_necessary():
    new_menu = create_main_menu()
    State.get().history.append(new_menu)
    set_current_menu(new_menu)


def show():
    global current_menu

    # fade_from is used on init_display, so we initialize this
    # color here. Set alpha to 2.0 to force 1 second of solid
    # color in combination with 2 sec. animation below
    if False and System.windows and not Settings.fullscreen_menu:
        State.get().fade_from = (1.0, 1.0, 1.0, 2.0)
        State.get().fade_to = (1.0, 1.0, 1.0, 0.0)
    else:
        State.get().fade_from = (0.0, 0.0, 0.0, 2.0)
        State.get().fade_to = (0.0, 0.0, 0.0, 0.0)
    init_display()
    if LIGHTING:
        init_lighting()
    init_textures()
    init_fonts()

    if USE_MENU_TRANSITIONS:
        compile_programs()

    InputHandler.open()

    on_resize((Render.get().display_width, Render.get().display_height))
    imageLoader = ImageLoader.get()
    imageLoader.start()
    new_menu = create_main_menu()
    State.get().history.append(new_menu)

    override_items = []
    for platform_id in PlatformHandler.get_platform_ids():
        if "--platform=" + platform_id in sys.argv:
            sys.argv.remove("--platform=" + platform_id)
            platform_item = PlatformItem(platform_id)
            override_items.append(platform_item)
            break
    # if "--favorites" in sys.argv or \
    #         settings.get(Option.ARCADE_INITIAL_VIEW) == "favorites":
    if (
        "--favorites" in sys.argv
        or settings.get(Option.ARCADE_INITIAL_FAVORITES) == "1"
    ):
        if "--favorites" in sys.argv:
            sys.argv.remove("--favorites")
        try:
            list_uuid = ListItem.get_favorites_uuid()
            favorites_item = ListItem("Favorites", list_uuid)
        except LookupError:
            print("No favorites list")
            # noinspection SpellCheckingInspection
            favorites_item = ListItem(
                "Favorites", "c03dd5fe-0e85-4efb-a126-f0e4f40feae6"
            )
        override_items.append(favorites_item)
    if override_items:
        parent_menu = new_menu
        override_menu = None
        parents = []
        for item in override_items:
            override_menu = ItemMenu()
            override_menu.parent_menu = parent_menu
            parents.append(parent_menu)
            # This is really hackish
            override_menu.parents = parents
            override_menu.items.append(item)
            parent_menu = override_menu
        new_menu = override_items[-1].activate(override_menu)
        print(new_menu)
        State.get().history.append(new_menu)

    set_current_menu(new_menu)
    if len(new_menu) == 1:
        # only n/a item showing, possibly
        if len(AllMenuItem().activate(None)) == 0:
            # no games, initiate game scan
            rescan_games()

    State.get().fade_start = get_current_time()
    State.get().fade_end = get_current_time() + 2.000

    # # make a timer so that update events are sent to modules at least once
    # # every second
    # pygame.time.set_timer(IDLE_EVENT, 1000)

    State.get().start_time = get_current_time()


def init_fonts():
    NotificationRender.init()

    BitmapFont.title_font = BitmapFont("title_font")
    BitmapFont.menu_font = BitmapFont("menu_font")


liberation_sans_bold_path = None
liberation_sans_narrow_bold_path = None
vera_font_path = None


def find_font_path_or_stream(name):
    path = os.path.join(
        FSGSDirectories.get_base_dir(), "Workspace", "Fonts", name
    )
    if os.path.exists(path):
        return path
    stream = resources.resource_stream(name)
    return stream


def reinit_fonts():
    print(
        "reinit_fonts, Render.get().display_height =",
        Render.get().display_height,
    )
    global liberation_sans_bold_path
    global liberation_sans_narrow_bold_path
    global vera_font_path

    if liberation_sans_bold_path is None:
        liberation_sans_bold_path = find_font_path_or_stream(
            "LiberationSans-Bold.ttf"
        )

    # if liberation_sans_narrow_bold_path is None:
    #     liberation_sans_narrow_bold_path = resources.resource_filename(
    #         "LiberationSansNarrow-Bold.ttf")
    # if vera_font_path is None:
    #     vera_font_path = resources.resource_filename(
    #         "VeraBd.ttf")

    if Font.title_font is None:
        Font.title_font = Font(
            liberation_sans_bold_path, int(0.04 * Render.get().display_height)
        )
    Font.title_font.set_size(int(0.04 * Render.get().display_height))
    if Font.subtitle_font is None:
        Font.subtitle_font = Font(
            liberation_sans_bold_path, int(0.025 * Render.get().display_height)
        )
    Font.subtitle_font.set_size(int(0.025 * Render.get().display_height))
    # if Font.small_font is None:
    #     Font.small_font = Font(
    #         liberation_sans_narrow_bold_path,
    #         int(0.025 * Render.get().display_height))
    # Font.small_font.set_size(int(0.025 * Render.get().display_height))
    if Font.main_path_font is None:
        Font.main_path_font = Font(
            liberation_sans_bold_path, int(0.025 * Render.get().display_height)
        )
    Font.main_path_font.set_size(int(0.025 * Render.get().display_height))
    if Font.list_subtitle_font is None:
        Font.list_subtitle_font = Font(
            liberation_sans_bold_path, int(0.020 * Render.get().display_height)
        )
    Font.list_subtitle_font.set_size(int(0.020 * Render.get().display_height))
    # if Font.header_font is None:
    #     Font.header_font = Font(
    #         vera_font_path, int(0.06 * Render.get().display_height))
    # Font.header_font.set_size(int(0.06 * Render.get().display_height))

    if NotificationRender.font is None:
        NotificationRender.font = Font(
            liberation_sans_bold_path, int(0.020 * Render.get().display_height)
        )


char_buffer = ""
char_buffer_last_updated = 0


def handle_search_menu_on_character_press(char_buffer):
    # if len(char_buffer) > 2 and t - char_buffer_last_updated > 0.5:
    if len(char_buffer) > 2:
        print(char_buffer)
        create_search_results_menu(char_buffer)
    if len(char_buffer) <= 2:
        if isinstance(current_menu, SearchResultsMenu):
            # collapse search menu

            # if hasattr(current_menu, "search_text"):
            print("setting current_menu (something with search)")
            # set_current_menu(current_menu.parent_menu)
            go_back()
        else:
            current_menu.search_text = char_buffer


# noinspection PyUnusedLocal
def character_press(char):
    print("character press", repr(char))
    if State.get().current_game:  # or isinstance(current_menu, GameMenu):
        print("ignoring key press", repr(char))
        return

    # global char_buffer
    char_buffer = current_menu.search_text

    global char_buffer_last_updated
    char_buffer_last_updated = State.get().time
    # return

    Render.get().dirty = True
    if char == "RETURN":
        print(char_buffer, len(char_buffer))
        print("returning false")
        return False
    elif char == "BACKSPACE" or char == u"\b":
        if ArcadeSettings().search():
            char_buffer = char_buffer[:-1]
            if len(char_buffer) <= 2:
                char_buffer = ""
            handle_search_menu_on_character_press(char_buffer)
        return True
    elif len(char) == 1:
        if ArcadeSettings().search():
            char_buffer += char
            handle_search_menu_on_character_press(char_buffer)
            if 1 <= len(char_buffer) <= 2:
                jump_to_item = -1
                for i, item in enumerate(current_menu.items):
                    # FIXME: a bit hack-y this, should check sort_name
                    # instead (need to store this in items then)
                    # also, should use binary search and not sequential search
                    searches = [
                        char_buffer,
                        "the " + char_buffer,
                        "a " + char_buffer,
                    ]
                    check = item.name.lower()
                    for s in searches:
                        if check.startswith(s):
                            jump_to_item = i
                            break
                if jump_to_item >= 0:
                    current_menu.set_selected_index(
                        jump_to_item, immediate=True
                    )
        return True
    else:
        raise Exception(repr(char))


class SearchTextItem(MenuItem):
    def __init__(self, title):
        MenuItem.__init__(self)
        self.path_title = title


class SearchResultsMenu(ItemMenu):
    pass


def create_search_results_menu(text):
    global current_menu
    try:
        if text == current_menu.search_text:
            return False
    except AttributeError:
        pass
    new_menu = SearchResultsMenu("Search Results")
    new_menu.search_text = text
    # words = [v.strip() for v in text.lower().split(" ")]
    # print "Creating search results for", words
    new_menu.top.append_left(SearchTextItem("Search: {0}_".format(text)))
    new_menu.top.set_selected_index(
        len(new_menu.top.left) + len(new_menu.top.right) - 1
    )

    # clause = []
    # args = []
    # for word in words:
    #     clause.append("AND name like ?")
    #     args.append("%{0}%".format(word))
    # clause = " ".join(clause)
    terms = GameNameUtil.extract_search_terms(text.lower())
    for item in MenuItem.create_game_items(terms):
        new_menu.append(item)
    if len(new_menu) == 0:
        new_menu.append(NoItem("No Search Results"))
    # if hasattr(current_menu, "search_text"):
    #     # replace current search menu, not append to path
    #     #new_menu.parent_menu = current_menu.parent_menu
    #     replace = True
    # else:
    #     #new_menu.parent_menu = current_menu
    #     replace = False
    replace = isinstance(current_menu, SearchResultsMenu)
    print("create search results menu")
    # set_current_menu(new_menu)
    enter_menu(new_menu, replace=replace)
    return True


def rescan_games():
    # global current_menu
    print("rescan games -- currently disabled")
    # GameScanner.scan()
    # Render.get().dirty = True
    pass


def go_back():
    c_menu = State.get().history[-1]
    if hasattr(c_menu, "go_back"):
        c_menu.go_back()
        return
    State.get().history.pop()
    set_current_menu(State.get().history[-1])


def default_input_func(button):
    if button == "LEFT":
        State.get().navigatable.go_left()
    elif button == "RIGHT":
        State.get().navigatable.go_right()
    elif button == "UP":
        State.get().navigatable.go_up()
    elif button == "DOWN":
        State.get().navigatable.go_down()
    elif button == "SKIP_LEFT":
        State.get().navigatable.go_left(10)
    elif button == "SKIP_RIGHT":
        State.get().navigatable.go_right(10)
    elif button == "PRIMARY":

        # global char_buffer
        # char_buffer = ""

        State.get().navigatable.activate()

    elif button == "BACK":
        print("-- button is BACK -- ")
        if State.get().config_menu:
            State.get().config_menu = None
            set_current_menu(State.get().current_menu)
            set_items_brightness(0.66, duration=0.500)
        elif State.get().current_game is None and current_menu.search_text:
            InputHandler.get_button()  # clear OK status
            character_press("BACKSPACE")
        elif State.get().current_game:
            State.get().current_game = None
            # game_fade_animation = AnimateValueBezier(
            #     (MenuGameTransition, "value"),
            #     1.0, State.get().time,
            #     1.0, State.get().time + 0.133,
            #     0.0, State.get().time + 0.133,
            #     0.0, State.get().time + 0.400)

        # elif can_navigate and current_menu.parent_menu:
        # elif can_navigate and len(State.get().history) > 1:
        elif len(State.get().history) > 1:
            go_back()
    elif button == "QUIT":
        State.get().quit = True


def render_top():
    Render.get().hd_perspective()
    gl.glPushMatrix()
    transition = State.get().current_menu.top_menu_transition
    gl.glTranslate(0.0, (1.0 - transition) * 90, 0.9)

    gl.glTranslate(0.0, 0.0, 0.05)

    if State.get().top_menu == State.get().navigatable:
        selected_index = State.get().top_menu.get_selected_index()
    else:
        selected_index = -1
    x = State.get().gl_left
    for item in State.get().top_menu.left:
        item.update_size_left()
        item.x = x
        item.y = 1080 - TOP_HEIGHT
        item.h = TOP_HEIGHT
        x += item.w

    index = len(State.get().top_menu.left) - 1
    for item in reversed(State.get().top_menu.left):
        item.render_top_left(selected=(index == selected_index))
        index -= 1

    index = len(State.get().top_menu) - 1
    x = State.get().gl_right
    for item in reversed(State.get().top_menu.right):
        item.update_size_right()
        x -= item.w
        item.x = x
        item.y = 1080 - TOP_HEIGHT
        item.h = TOP_HEIGHT
        if Mouse.focus:
            selected = Mouse.focus == item
        else:
            selected = index == selected_index
        item.render_top_right(selected=selected)
        Mouse.items.append(item)
        index -= 1
    gl.glPopMatrix()


def render_config_menu():
    if not State.get().config_menu:
        return

    Render.get().ortho_perspective()
    config_menu = State.get().config_menu
    # text = config_menu.items[config_menu.index]
    # otw, th = Render.get().text(text, title_font,
    #         -1.0, -0.93, 2.0, color=(1.0, 1.0, 1.0, 0.36 * strength))
    # x = 0.0 + otw / 2 + CONFIG_SEPARATION
    # for i in range(config_menu.index + 1, len(config_menu.items)):
    #     text = config_menu.items[i]
    #     tw, th = Render.get().text(text, title_font,
    #             x, -0.93, color=(1.0, 1.0, 1.0, 0.36 * strength))
    #     x += tw + CONFIG_SEPARATION
    # x = 0.0 - otw / 2 - CONFIG_SEPARATION
    x = -0.55
    y = 0.8
    for i in range(len(config_menu.items)):
        text = config_menu.items[i].upper()
        # tw, th = Render.get().measure_text(text, title_font)
        # x -= tw + CONFIG_SEPARATION
        y -= 0.15
        if i == config_menu.index and config_menu == State.get().navigatable:
            color = (1.0, 1.0, 1.0, 1.0)
        else:
            color = (1.0, 1.0, 1.0, 0.33)
        Render.get().text(text, Font.subtitle_font, x, y, color=color)


def render_scanning_status():
    # Render.get().hd_perspective()
    # text = GameScanner.get_status()
    # Render.get().dirty = True
    #
    # fs_emu_texturing(False)
    #
    # z = 0.0
    #
    # glBegin(GL_QUADS)
    # glColor3f(0.0, 0.0, 0.0)
    # glVertex3f(   0, 500, z)
    # glVertex3f(1920, 500, z)
    # glVertex3f(1920, 700, z)
    # glVertex3f(   0, 700, z)
    # glEnd()
    #
    # Render.get().text(text, Font.title_font, 200, 600, color=(1.0, 1.0,
    # 1.0, 1.0))
    #
    # glBegin(GL_QUADS)
    # glColor3f(1.0, 1.0, 1.0)
    # x = 200
    # y = 500
    # z = 0.9
    # x2 = 200 + 1520 * GameScanner.progress
    # glVertex3f(x, y, z)
    # glVertex3f(x2, y, z)
    # glVertex3f(x2, y + 20, z)
    # glVertex3f(x, y + 20, z)
    # glEnd()
    # fs_emu_texturing(True)
    pass


def do_render():
    if current_menu is None:
        return

    current_menu.update()

    if RunTransition.value > 0.99:
        # do not render anything when running a game
        return

    if State.get().currently_ingame:
        # print("currently ingame")
        return

    # try to exploit parallelism by uploading texture while rendering
    TextureManager.get().load_textures(1)

    # clear mouseover rects -these will be calculated during rendering
    Mouse.items[:] = []
    Render.get().standard_perspective()

    # scanning = GameScanner.scanning

    data = current_menu.render()
    current_menu.render_transparent(data)

    # if GameScanner.is_scanning():
    if False:
        render_scanning_status()
        State.get().was_scanning = True
    else:
        render_config_menu()
        if State.get().was_scanning:
            print("State.get().was_scanning")
            State.get().was_scanning = False
            # reload current menu

            # if current_menu.parent_menu:
            #     result = current_menu.parent_menu.selected_item.activate(
            #             current_menu.parent_menu)
            #     if isinstance(result, Menu):
            #         #if len(result) == 0:
            #         #    result.append(NoItem())
            #         result.parent_menu = current_menu.parent_menu
            #         print("set new menu (rescanned games)")
            #         set_current_menu(result)
            recreate_main_menu_if_necessary()

    render_top()

    if State.get().dialog:
        State.get().dialog.render()

    render_global_fade()
    NotificationRender.render()
    if RunTransition.value > 0.0:
        render_fade(a=RunTransition.value)


def render_fade(r=0.0, g=0.0, b=0.0, a=0.0):
    Render.get().hd_perspective()
    fs_emu_blending(True)
    fs_emu_texturing(False)
    gl.glBegin(gl.GL_QUADS)
    gl.glColor4f(r * a, g * a, b * a, a)
    gl.glVertex2f(0, 0)
    gl.glVertex2f(1920, 0)
    gl.glVertex2f(1920, 1080)
    gl.glVertex2f(0, 1080)
    gl.glEnd()


def render_global_fade():
    t = State.get().time
    if State.get().fade_end >= t >= State.get().fade_start:
        a = (t - State.get().fade_start) / (
            State.get().fade_end - State.get().fade_start
        )
        if a < 0.0:
            a = 0.0
        elif a > 1.0:
            a = 1.0

        Render.get().hd_perspective()
        gl.glPushMatrix()
        gl.glTranslatef(0.0, 0.0, 0.99999)
        fs_emu_blending(True)
        fs_emu_texturing(True)
        if State.get().fade_splash:
            Texture.splash.render(
                (1920 - Texture.splash.w) // 2,
                (1080 - Texture.splash.h) // 2,
                Texture.splash.w,
                Texture.splash.h,
                opacity=(1.0 - a),
            )

        c = [0, 0, 0, (1.0 - a)]
        # for i in range(4):
        #     c[i] = State.get().fade_from[i] + \
        #             (State.get().fade_to[i] - State.get().fade_from[i]) * a
        #  * (a)
        render_fade(*c)
        gl.glPopMatrix()
        Render.get().dirty = True


FPS_FRAMES = 100
render_times = deque()
for _ in range(FPS_FRAMES):
    render_times.append(0)

fps_str = ""
debug_x = 0
debug_x_2 = 0


def render_debug_square():
    global debug_x
    Render.get().hd_perspective()
    fs_emu_texturing(False)
    gl.glBegin(gl.GL_QUADS)
    gl.glColor3f(1.0, 1.0, 1.0)
    x = debug_x
    debug_x += 1
    if debug_x >= 1920:
        debug_x = 0
    y = 989
    z = 0.99
    gl.glVertex3f(x, y, z)
    gl.glVertex3f(x + 20, y, z)
    gl.glVertex3f(x + 20, y + 20, z)
    gl.glVertex3f(x, y + 20, z)
    gl.glEnd()
    fs_emu_texturing(True)


def render_debug_square_2():
    global debug_x_2
    Render.get().hd_perspective()
    fs_emu_texturing(False)
    gl.glBegin(gl.GL_QUADS)
    gl.glColor3f(0.2, 0.2, 0.2)
    x = debug_x_2
    debug_x_2 += 1
    if debug_x_2 >= 1920:
        debug_x_2 = 0
    y = 989 + 5
    z = 0.99
    gl.glVertex3f(x, y, z)
    gl.glVertex3f(x + 20, y, z)
    gl.glVertex3f(x + 20, y + 10, z)
    gl.glVertex3f(x, y + 10, z)
    gl.glEnd()
    fs_emu_texturing(True)


# FIXME: remove / move some code away
def swap_buffers():
    # global fps_str
    #
    # Render.get().ortho_perspective()
    # #glPushMatrix()
    # #glTranslatef(0.0, 0.0, 0.5)
    #
    # #if not fps_str:
    # #    fps_str = "WHY?"
    #
    # if Render.get().display_fps or True:
    #     if fps_str:
    #         Render.get().text(fps_str, Font.main_path_font,
    #                     -1.74, 0.82, h=0.1, color=(0.25, 0.25, 0.25, 1.0))
    # #glPopMatrix()
    #
    # # FIXME: Why does not minimize from fullscreen work on ATI unless we
    # render
    # # something here?
    # glBindTexture(GL_TEXTURE_2D, 0)
    # glPushMatrix()
    # glTranslate(2000.0, 0.0, 0.0)
    # glBegin(GL_QUADS)
    # glVertex2f(0.0, 0.0)
    # glVertex2f(1.0, 0.0)
    # glVertex2f(1.0, 1.0)
    # glVertex2f(0.0, 1.0)
    # glEnd()
    # glPopMatrix()
    #
    # #fs_emu_blending(False)
    # #glEnable(GL_DEPTH_TEST)
    #
    # #if Render.get().display_sync:
    # #    glFinish()
    #
    # #pygame.display.flip()
    # print("FIXME: not flipping")
    #
    # if Render.get().display_sync:
    #     # give up time slice
    #     time.sleep(0.001)
    #     glFinish()
    #
    # if Render.get().display_fps:
    #     t = get_current_time()
    #     render_times.append(t)
    #     t0 = render_times.popleft()
    #     if t0 > 0 and State.get().frame_number % 5 == 0:
    #         time_diff = t - t0
    #         #print("{0:0.2f}".format(300.0 / time_diff))
    #         fps = FPS_FRAMES / time_diff
    #         if fps >= 100:
    #             fps_str = "FPS:  {0:0.0f}".format(fps)
    #         else:
    #             fps_str = "FPS: {0:0.1f}".format(fps)
    #         #Render.get().text(fps_str, Font.title_font,
    #         #        -1.0, 0.90, 2.0, shadow=True)
    State.get().frame_number += 1
    Render.get().delete_textures()


def render_screen():
    # set Render.get().dirty to False here, so that render functions can
    # request a new render frame by setting dirty
    Render.get().dirty = False
    # glEnable(GL_SCISSOR_TEST)
    # can_idle =
    if SDL_IsMinimized():
        time.sleep(0.01)
        return
    # Render.get().dirty = True
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    do_render()
    if Render.get().display_fps:
        Render.get().dirty = True
    if RENDER_DEBUG_SQUARES:
        render_debug_square()


# noinspection PyPep8Naming
def init_display():
    global display
    global real_display_height  # , display_yoffset

    # global banner_texture, shadow_texture, gloss_texture
    # global top_texture, top_logo_texture, logo_texture
    # global missing_cover_texture, default_item_texture
    # global backdrop_texture

    logger.debug("Init OpenGL menu display")

    DisplayLists.clear()

    # on_resize()
    # depth = 0
    # FIXME: HACK / TESTING
    # if not Settings.fullscreen_menu:
    #    if windows:
    #        os.environ["SDL_VIDEO_WINDOW_POS"] = "3,29"
    #    else:
    #        os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
    # maximize_window = (not Settings.fullscreen_menu and
    #                    Settings.windowed_size is None)

    # display_info = pygame.display.Info()
    # dw = display_info.current_w
    # dh = display_info.current_h
    # dw, dh = fsui.get_screen_size()
    # dw, dh = 100, 100
    Render.get().display_width = main_window.width
    Render.get().display_height = main_window.height

    # if Settings.fullscreen_menu:
    #     print("fullscreen is True")
    #     if windows:
    #         #resolution = (0, 0)
    #         #flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.NOFRAME \
    #         #        | pygame.FULLSCREEN
    #         os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
    #         flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.NOFRAME
    #         #flags = flags | pygame.FULLSCREEN
    #         #if fs.linux:
    #         #    pass
    #         #else:
    #         if dw > dh * 2:
    #             # Assume dual monitor setup - hack for Linux / SDL
    #             resolution = (dw / 2, dh)
    #         else:
    #             resolution = (dw, dh)
    #     else:  # fullscreen, but not microsoft windows
    #         #resolution = (0, 0)
    #         flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.NOFRAME #|
    # pygame.FULLSCREEN
    #         if dw > dh * 2:
    #             # Assume dual monitor setup - hack for Linux / SDL
    #             resolution = (dw / 2, dh)
    #         else:
    #             resolution = (dw, dh)
    #         if linux:
    #             overscan = Config.get("display/overscan", "0,0,0,0")
    #             try:
    #                 overscan = overscan.split(",")
    #                 overscan = [int(x.strip()) for x in overscan]
    #                 print("using overscan", overscan)
    #             except Exception as e:
    #                 print("error parsing overscan from config:", repr(e))
    #                 overscan = [0, 0, 0, 0]
    #             os.environ["SDL_VIDEO_WINDOW_POS"] = "{0},{1}".format(
    #                 overscan[0], overscan[1])
    #             resolution = (resolution[0] - overscan[0] - overscan[2],
    #                           resolution[1] - overscan[1] - overscan[3])
    #         elif macosx:
    #             # FIXME: fullscreen mode does not work very well. -When
    #             # opening a fullscreen emulator from fullscreen, the emulator
    #             # crashes on glViewport. Tested with fs-amiga.
    #             #flags |= pygame.FULLSCREEN
    #
    #             # for now, we create an almost maximized window, works
    #             # quite well when the dock is set to auto-hide
    #             #resolution = (resolution[0], resolution[1] - 22)
    #
    #             # FIXME: trying LSUIPresentationMode
    #             os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
    #
    #             # kUIModeNormal = 0
    #             # kUIModeContentSuppressed = 1
    #             # kUIModeContentHidden = 2
    #             # kUIModeAllSuppressed = 4
    #             kUIModeAllHidden = 3
    #             kUIOptionAutoShowMenuBar = 1 << 0
    #             # kUIOptionDisableAppleMenu = 1 << 2
    #             # kUIOptionDisableProcessSwitch = 1 << 3
    #             # kUIOptionDisableForceQuit = 1 << 4
    #             # kUIOptionDisableSessionTerminate = 1 << 5
    #             # kUIOptionDisableHide = 1 << 6
    #
    #             #noinspection PyUnresolvedReferences
    #             import objc
    #             #noinspection PyUnresolvedReferences
    #             from Foundation import NSBundle
    #             bundle = NSBundle.bundleWithPath_(
    #                 "/System/Library/Frameworks/Carbon.framework")
    #             objc.loadBundleFunctions(
    #                 bundle, globals(),
    #                 (("SetSystemUIMode", "III", ""),))
    #             #noinspection PyUnresolvedReferences
    #             SetSystemUIMode(kUIModeAllHidden, kUIOptionAutoShowMenuBar)
    #
    # else:
    #     if windows and maximize_window and \
    #             not Settings.window_decorations:
    #         import ctypes
    #         SPI_GETWORKAREA = 48
    #
    #         class RECT(ctypes.Structure):
    #             _fields_ = [
    #                 ("left", ctypes.c_ulong),
    #                 ("top", ctypes.c_ulong),
    #                 ("right", ctypes.c_ulong),
    #                 ("bottom", ctypes.c_ulong)]
    #
    #         m = ctypes.windll.user32
    #         r = RECT()
    #         m.SystemParametersInfoA(SPI_GETWORKAREA, 0, ctypes.byref(r), 0)
    #         x = int(r.left)
    #         y = int(r.top)
    #         w = int(r.right) - int(r.left)
    #         h = int(r.bottom) - int(r.top)
    #         print(x, y, w, h)
    #         WINDOWED_SIZE[0] = w
    #         WINDOWED_SIZE[1] = h
    #         os.environ["SDL_VIDEO_WINDOW_POS"] = "{0},{1}".format(x, y)
    #         State.get().allow_minimize = False
    #
    #     if Settings.windowed_size:
    #         print("Settings.windowed_size", Settings.windowed_size)
    #         WINDOWED_SIZE[0] = Settings.windowed_size[0]
    #         WINDOWED_SIZE[1] = Settings.windowed_size[1]
    #         Render.get().display_width = WINDOWED_SIZE[0]
    #         Render.get().display_height = WINDOWED_SIZE[1]
    #         #if dw > 1400:
    #         #    Render.get().display_width = 1280
    #         #    Render.get().display_height = 720
    #     else:
    #         Render.get().display_width = WINDOWED_SIZE[0]
    #         Render.get().display_height = WINDOWED_SIZE[1]
    #     resolution = (Render.get().display_width, Render.get().display_height)
    #     #print(resolution)
    #     #sys.exit(1)
    #     if Settings.window_decorations:
    #         flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
    #     else:
    #         flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.NOFRAME
    #
    # display_yoffset = 0
    # Mouse.set_visible(False)
    #
    # pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
    # pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 16)
    #
    # Render.get().display_sync = ENABLE_VSYNC
    # if Render.get().display_sync:
    #     print("enabling vertical sync")
    #     os.environ["__GL_SYNC_TO_VBLANK"] = "1"
    #     pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 1)
    # else:
    #     os.environ["__GL_SYNC_TO_VBLANK"] = "0"
    #     pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 0)
    # pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    # fsaa = Config.get_int("video/fsaa", 0)
    # if fsaa:
    #     pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    #     pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, fsaa)
    # print("pygame set display mode", resolution, flags, depth)
    # display = pygame.display.set_mode(resolution, flags, depth)
    # if not Settings.fullscreen_game:
    #     try:
    #         del os.environ["SDL_VIDEO_WINDOW_POS"]
    #     except KeyError:
    #         pass
    #
    # if app.name == "fs-uae-arcade":
    #     pygame.display.set_caption("FS-UAE Arcade")
    # else:
    #     pygame.display.set_caption("FS Game Center")
    #
    # # FIXME: DISABLING MAXIMIZE FOR DEBUGGING
    # #maximize_window = False
    # if maximize_window:
    #     print("maximizing window")
    #     SDL_Maximize()
    #     for event in pygame.event.get():
    #         if event.type == pygame.VIDEORESIZE:
    #             #WINDOWED_SIZE[0] = event.w
    #             #WINDOWED_SIZE[1] = event.h
    #             on_resize((event.w, event.h))
    #     print("DISPLAY.GET_SIZE", display.get_size())
    # else:
    #     on_resize(display.get_size())

    gl.glMatrixMode(gl.GL_MODELVIEW)

    gl.glBlendFunc(gl.GL_ONE, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glClearColor(*State.get().fade_from)

    fs_emu_texturing(True)
    Texture.splash = Texture("splash.png")

    for _ in range(0):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        Render.get().hd_perspective()
        Texture.splash.render(
            (1920 - Texture.splash.w) // 2,
            (1080 - Texture.splash.h) // 2,
            Texture.splash.w,
            Texture.splash.h,
        )
        gl.glFinish()
        # pygame.display.flip()
        gl.glFinish()

    gl.glEnable(gl.GL_DEPTH_TEST)


def init_textures():
    Texture.shadow = Texture.from_resource("shadow.png")
    Texture.shadow2 = Texture.from_resource("shadow2.png")
    # Texture.gloss = Texture.from_resource("gloss.png")
    Texture.gloss = Texture("gloss.png")
    Texture.screen_gloss = Texture("screen_gloss.png")
    Texture.static = Texture("preview_static0.png")
    Texture.default_item = Texture("default_item.png")
    Texture.missing_screenshot = Texture("missing_screenshot.png")
    Texture.missing_cover = Texture("missing_cover.png")
    # path = os.path.join(fs.get_data_dir(), "logo.png")
    # if os.path.exists(path):
    #     im = Image.open(path)
    #     Texture.logo = Texture.load(im)
    # else:
    Texture.logo = Texture.from_resource("logo.png")
    Texture.top = Texture.from_resource("top.png")
    Texture.top_logo = Texture("top_logo.png")
    Texture.top_logo_selected = Texture("top_logo_selected.png")

    Texture.add = Texture("add.png")
    Texture.add_selected = Texture("add_selected.png")
    Texture.home = Texture("home.png")
    Texture.home_selected = Texture("home_selected.png")
    Texture.minimize = Texture("minimize.png")
    Texture.minimize_selected = Texture("minimize_selected.png")
    Texture.close = Texture("close.png")
    Texture.close_selected = Texture("close_selected.png")
    Texture.shutdown = Texture("shutdown.png")
    Texture.shutdown_selected = Texture("shutdown_selected.png")

    Texture.bottom_bar = Texture("bottom_bar.png")
    Texture.screen_border_1 = Texture("screen_border_1.png")
    Texture.screen_border_2 = Texture("screen_border_2.png")
    Texture.top_background = Texture("top_background.png")
    Texture.top_item = Texture("top_item.png")
    Texture.top_item_selected = Texture("top_item_selected.png")
    Texture.top_item_left = Texture("top_item_left.png")
    Texture.top_item_left_selected = Texture("top_item_left_selected.png")
    Texture.top_item_right = Texture("top_item_right.png")
    Texture.top_item_arrow = Texture("top_item_arrow.png")
    Texture.top_item_arrow_selected = Texture("top_item_arrow_selected.png")

    Texture.sidebar_background = Texture("sidebar_background.png")
    Texture.sidebar_background_shadow = Texture(
        "sidebar_background_shadow.png"
    )
    Texture.glow_top = Texture("glow_top.png")
    Texture.glow_top_left = Texture("glow_top_left.png")
    Texture.glow_left = Texture("glow_left.png")

    Texture.heading_strip = Texture("heading_strip.png")
    Texture.item_background = Texture("item_background.png")
    Texture.top_item_background = Texture("top_item_background.png")
    Texture.logo_32 = Texture("logo-32.png")

    Texture.stretch = Texture("stretch.png")
    Texture.aspect = Texture("stretch-aspect.png")
    Texture.square_pixels = Texture("stretch-none.png")

    # # FIXME: TEMPORARY - FOR TESTING, ONLY
    # path = "c:\\git\\fs-game-database\\Backdrops\\ffx.png"
    # if os.path.exists(path):
    #     im = Image.open(path)
    #     #im = resources.get_resource_image_pil("shadow.png")
    #     assert im.size == (1024, 1024)
    #     imdata = im.tostring("raw", "RGB")
    #     backdrop_texture = Render.get().create_texture()
    #     glBindTexture(GL_TEXTURE_2D, backdrop_texture)
    #     glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, im.size[0], im.size[1], 0,
    #                  GL_RGB, GL_UNSIGNED_BYTE, imdata)
    #     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    #     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # else:
    #     backdrop_texture = 0


def init_lighting():
    gl.glLightModeli(gl.GL_LIGHT_MODEL_LOCAL_VIEWER, gl.GL_TRUE)
    gl.glLightModeli(gl.GL_LIGHT_MODEL_TWO_SIDE, gl.GL_FALSE)
    gl.glLightModeli(
        gl.GL_LIGHT_MODEL_COLOR_CONTROL, gl.GL_SEPARATE_SPECULAR_COLOR
    )

    light_position = (0.0, 0.0, 3.0, 1.0)
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, light_position)
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
    gl.glEnable(gl.GL_LIGHT0)

    gl.glLightfv(gl.GL_LIGHT1, gl.GL_DIFFUSE, (0.0, 0.0, 0.0, 1.0))
    gl.glLightfv(gl.GL_LIGHT1, gl.GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    gl.glEnable(gl.GL_LIGHT1)

    gl.glLightfv(gl.GL_LIGHT2, gl.GL_DIFFUSE, (0.0, 0.0, 0.0, 1.0))
    gl.glLightfv(gl.GL_LIGHT2, gl.GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
    gl.glEnable(gl.GL_LIGHT2)

    gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SHININESS, (10,))


def handle_videoresize_event(event):
    WINDOWED_SIZE[0] = event.w
    WINDOWED_SIZE[1] = event.h
    on_resize((event.w, event.h))


def on_resize(display_size):
    print("glui.window.on_resize", display_size)
    # traceback.print_stack()

    global display
    global real_display_height, display_yoffset
    global browse_curve, header_curve  # ,screenshot_curve

    DisplayLists.clear()

    Render.get().display_width, Render.get().display_height = display_size  #
    #  display# .get_size()
    State.get().display_aspect = (
        Render.get().display_width / Render.get().display_height
    )
    print(WINDOWED_SIZE)
    Settings.windowed_size = tuple(WINDOWED_SIZE)

    real_display_height = Render.get().display_height
    # if Render.get().display_width / Render.get().display_height < 4 / 3:
    #    Render.get().display_height = int(Render.get().display_width / 4 * 3)
    #    display_yoffset = (real_display_height - Render.get(
    # ).display_height) // 2
    # else:
    display_yoffset = 0
    # glViewport(0, 0, Render.get().display_width, real_display_height)
    # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # swap_buffers()
    # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # swap_buffers()
    print(display_yoffset)

    reinit_fonts()

    print(
        0,
        display_yoffset,
        Render.get().display_width,
        Render.get().display_height,
    )
    gl.glViewport(
        0,
        display_yoffset,
        Render.get().display_width,
        Render.get().display_height,
    )

    # aspect_ratio = max(4 / 3, (Render.get().display_width / Render.get(
    # ).display_height))
    factor = (Render.get().display_width / Render.get().display_height) / (
        1024 / 600
    )
    browse_curve = Bezier.bezier(
        (-5.0 * factor, -10.0),
        (-1.7 * factor, -0.0),
        (1.7 * factor, -0.0),
        (5.0 * factor, -10.0),
    )
    header_curve = Bezier.bezier(
        (-2.0 * factor, 0.00),
        (-1.0 * factor, 0.075),
        (1.0 * factor, 0.075),
        (2.0 * factor, 0.00),
        steps=50,
    )

    # if USE_MENU_TRANSITIONS:
    #    State.get().fbo = FrameBufferObject(
    #        Render.get().display_width, Render.get().display_height)
    Render.get().dirty = True


class LogoStrength(object):
    anim = None
    value = 1.0


def set_ingame_status():
    # State.get().fade_start = State.get().time
    # State.get().fade_end = State.get().time + 86400.0 * 365.0
    # State.get().fade_from = (0.0, 0.0, 0.0, 0.0)
    # State.get().fade_to = (0.0, 0.0, 0.0, 0.0)
    # State.get().fade_splash = False
    print("State.get().currently_ingame = True")
    State.get().currently_ingame = True


def back_to_menu_from_game():
    print("State.get().currently_ingame = False")
    State.get().currently_ingame = False

    set_items_brightness(0.66, duration=0.500)

    RunTransition.value = 0.0
    RunTransition.anim = None
    LogoStrength.anim = None
    LogoStrength.value = 1.0

    Render.get().zoom = 1.0
    Render.get().offset_x = 0.0
    Render.get().offset_y = 0.0

    State.get().fade_splash = True
    State.get().fade_start = State.get().time
    State.get().fade_end = State.get().time + 0.5
    State.get().fade_from = (0.0, 0.0, 0.0, 2.0)
    State.get().fade_to = (0.0, 0.0, 0.0, 0.0)


def fade_quit():
    print("fade_quit")
    duration = 0.500
    alpha = 0.0
    start = get_current_time()
    while True:
        alpha = min(1.0, (get_current_time() - start) / duration)

        def render_func():
            render_screen()
            Render.get().ortho_perspective()
            fs_emu_blending(True)
            fs_emu_texturing(False)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glBegin(gl.GL_QUADS)
            gl.glColor4f(0.0, 0.0, 0.0, alpha)
            gl.glVertex2f(-10.0, -1.0)
            gl.glVertex2f(10.0, -1.0)
            gl.glVertex2f(10.0, 1.0)
            gl.glVertex2f(-10.0, 1.0)
            gl.glEnd()
            gl.glEnable(gl.GL_DEPTH_TEST)
            # fs_emu_blending(False)
            fs_emu_texturing(True)
            swap_buffers()
            Render.get().dirty = True

        Render.get().dirty = True
        main_loop_iteration(input_func=None, render_func=render_func)
        if alpha >= 1.0:
            break


def default_render_func():
    # rendered = False

    time_str = time.strftime("%H:%M")
    if time_str != Render.get().last_time_str:
        # clock must be updated, at least
        Render.get().dirty = True
        Render.get().last_time_str = time_str

    if Render.get().dirty or ALWAYS_RENDER:
        # print(Render.get().frame_number)
        render_screen()
        # rendered = True
        Render.get().twice = False
        # Render.get().twice = True
    else:
        if not Render.get().twice:
            Render.get().twice = True
            render_screen()
            # rendered = True
    if RENDER_DEBUG_SQUARES:
        render_debug_square_2()
    # if not rendered:
    #     pass
    # time.sleep(0.01)
    swap_buffers()


def find_item_at_coordinate(pos):
    menu = current_menu
    # Just checking top items for now
    for item in menu.top.left:
        if (
            item.x <= pos[0] <= item.x + item.w
            and item.y <= pos[1] <= item.y + item.h
        ):
            return item
    for item in menu.top.right:
        if (
            item.x <= pos[0] <= item.x + item.w
            and item.y <= pos[1] <= item.y + item.h
        ):
            return item
    return None


def handle_mouse_event(event):
    if event["type"] == "mouse-motion":
        item = find_item_at_coordinate(event["pos"])
        # print("mouse over item", item)
        state = State.get()
        state.mouse_item = item
    elif event["type"] == "mouse-press":
        item = find_item_at_coordinate(event["pos"])
        state = State.get()
        state.mouse_press_item = item
    elif event["type"] == "mouse-release":
        item = find_item_at_coordinate(event["pos"])
        state = State.get()
        # state.mouse_press_item = item
        if item is not None and item == state.mouse_press_item:
            item.activate(current_menu)
        state.mouse_press_item = None


def main_loop_iteration(
    input_func=default_input_func, render_func=default_render_func
):
    state = State.get()

    # if State.get().currently_ingame:
    #     print("currently ingame")
    #     #return False

    # print("main loop iteration")
    # time.sleep(0.1)
    # stop_loop = False

    # if State.get().idle_from and State.get().idle_from < get_current_time():
    #     #print(State.get().idle_from)
    #     if not Render.get().dirty:
    #         #print("waiting for events...")
    #         events = [pygame.event.wait()]
    #     else:
    #         events = pygame.event.get()
    # else:
    #     events = pygame.event.get()

    state.time = get_current_time()

    # Main.process()

    # t = State.get().time

    # if len(char_buffer) > 2 and t - char_buffer_last_updated > 0.5:
    # print(current_menu, isinstance(current_menu, ItemMenu))
    # if isinstance(current_menu, ItemMenu):
    #
    #    # if len(char_buffer) > 2 and t - char_buffer_last_updated > 0.5:
    #    if len(char_buffer) > 2:
    #        create_search_results_menu(char_buffer)
    #    if len(char_buffer) <= 2:
    #        # collapse search menu
    #
    #        if hasattr(current_menu, "search_text"):
    #            print("setting current_menu (something with search)")
    #            set_current_menu(current_menu.parent_menu)

    if state.hide_mouse_time and state.time > state.hide_mouse_time:
        if Mouse.focus:
            # keep cursor visible if mouse has focus
            pass
        else:
            state.hide_mouse_time = 0
            Mouse.set_visible(False)

    had_mouse_event = False
    for event in InputHandler.pop_all_text_events():
        if event["type"] == "text":
            # if key was handled as a virtual button, only allow this
            # character if already started typing something, or else
            # navigating with X-Arcade may start searching for games
            if InputHandler.peek_button():
                if len(current_menu.search_text) > 0:
                    character_press(event["text"])
                    # reset InputHandler so that virtual button
                    # is not processed, since we handled this press
                    # as a char
                    InputHandler.get_button()
            else:
                character_press(event["text"])
        elif event["type"] in ["mouse-motion", "mouse-press", "mouse-release"]:
            had_mouse_event = True
            handle_mouse_event(event)
        else:
            print("[WARNING] Unhandled event", event)

    AnimationSystem.update()
    NotificationRender.update()

    # if idle_events_only:
    #     # do not update State.get().idle_from
    #     pass
    # elif len(events) > 0:
    #     #print(events)
    #     if IDLE:
    #         State.get().idle_from = State.get().time + IDLE
    #         #print(State.get().idle_from)

    if Render.get().dirty or ALWAYS_RENDER:
        if Render.get().non_dirty_state:
            print("must start rendering again...")
        Render.get().non_dirty_state = False
        render_func()
    else:
        # if not Render.get().non_dirty_state:
        #     print("pause rendering!")
        # Render.get().non_dirty_state = True
        Render.get().dirty = True

    button = InputHandler.get_button()
    if button:
        print("InputHandler.get_button", button, InputHandler.last_device)
        GameCenter.register_user_activity()
        if input_func:
            input_func(button)
        Render.get().dirty = True
    if InputHandler.repeat_info:
        Render.get().dirty = True

    # if IDLE:
    if AnimationSystem.is_active():
        # State.get().idle_from = None
        Render.get().dirty = True
        # elif State.get().idle_from is None:
        #     State.get().idle_from = State.get().time + IDLE
    if not IDLE:
        Render.get().dirty = True
    # except KeyboardInterrupt:
    #     print "KeyboardInterrupt"
    #     return
    # return stop_loop
    if had_mouse_event:
        Render.get().dirty = True

    if not Render.get().display_sync:
        t = time.time()
        diff = t - Render.get().display_last_iteration
        # print(diff)
        frame_time = 1 / 60.0
        if diff < frame_time:
            # FIXME: use real refresh rate / frame time
            sleep_time = frame_time - diff
            time.sleep(sleep_time)
        Render.get().display_last_iteration = t

    return state.quit
