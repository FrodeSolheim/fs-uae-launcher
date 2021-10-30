from typing import Dict, Tuple, Union

from fsgamesys.input.sdlkeycodes import sdl_key_codes
from fsgamesys.util import sdl2

# with open(os.expanduser('~/Desktop/keys.txt'), 'wb') as f:
#     for key in sorted(sdl_key_codes.keys()):
#         value = str(sdl_key_codes[key])
#         sdl_name = 'SDLK_' + key.upper()
#         try:
#             dik_name = 'DIK_' + sdlk_to_dik[key.upper()]
#         except KeyError:
#             dik_name = ''
#         try:
#             dik_code = str(dinput_key_codes[key.upper()])
#         except KeyError:
#             dik_code = ''
#         f.write("    '" + sdl_name + "': (" + value + ", '" + dik_name +
#                 "', " + dik_code + '),\n')


class Key(object):
    def __init__(self, name: str):
        self.name = name

    @property
    def sdl_name(self):
        return self.name

    # Deprecated
    @property
    def sdl_code(self):
        return key_table[self.name][0]

    @property
    def sdl1_key_code(self):
        return key_table[self.name][4]

    @property
    def sdl2_key_code(self):
        return key_table[self.name][0]

    @property
    def dinput_name(self):
        return key_table[self.name][1]

    @property
    def dinput_code(self):
        return key_table[self.name][2]

    @property
    def sdl2_scan_code(self):
        return key_table[self.name][3]

    def __str__(self):
        return "<Key {}>".format(self.name)


class Keyboard(object):
    @staticmethod
    def key(name: str) -> Key:
        # try:
        #     code = name.key.keysym.sym
        # except AttributeError:
        #     pass
        print("key({})".format(name))
        try:
            code = name["key"]
        except (KeyError, TypeError):
            pass
        else:
            name = sdl_key_code_to_name[code]
        if isinstance(name, int):
            name = sdl_key_code_to_name[name]
        name = name.upper()
        if name.startswith("SDLK_"):
            pass
        else:
            name = "SDLK_" + name
        return Key(name)


# class Keyboard(object):
#     @staticmethod
#     def key(name):
#         if isinstance(name, int):
#             name = sdl_key_code_to_name[name]
#         name = name.upper()
#         if name.startswith("SDLK_"):
#             pass
#         else:
#             name = "SDLK_" + name
#         return Key(name)


key_table: Dict[
    str,
    Union[
        Tuple[int, str],
        Tuple[int, str, int],
        Tuple[int, str, int, int],
        Tuple[int, str, int, int, int],
    ],
] = {
    "SDLK_NO_KEY": (0, "DIK_NO_KEY", 0, 0),
    "SDLK_0": (48, "DIK_0", 11, sdl2.SDL_SCANCODE_0),
    "SDLK_1": (49, "DIK_1", 2, sdl2.SDL_SCANCODE_1),
    "SDLK_2": (50, "DIK_2", 3, sdl2.SDL_SCANCODE_2),
    "SDLK_3": (51, "DIK_3", 4, sdl2.SDL_SCANCODE_3),
    "SDLK_4": (52, "DIK_4", 5, sdl2.SDL_SCANCODE_4),
    "SDLK_5": (53, "DIK_5", 6, sdl2.SDL_SCANCODE_5),
    "SDLK_6": (54, "DIK_6", 7, sdl2.SDL_SCANCODE_6),
    "SDLK_7": (55, "DIK_7", 8, sdl2.SDL_SCANCODE_7),
    "SDLK_8": (56, "DIK_8", 9, sdl2.SDL_SCANCODE_8),
    "SDLK_9": (57, "DIK_9", 10, sdl2.SDL_SCANCODE_9),
    "SDLK_A": (97, "DIK_A", 30, sdl2.SDL_SCANCODE_A),
    "SDLK_AMPERSAND": (38, "", 0),
    "SDLK_ASTERISK": (42, "", 0),
    "SDLK_AT": (64, "DIK_AT", 145),
    "SDLK_B": (98, "DIK_B", 48),
    "SDLK_BACKQUOTE": (96, "DIK_GRAVE", 0),
    "SDLK_BACKSLASH": (92, "DIK_BACKSLASH", 43),
    "SDLK_BACKSPACE": (sdl2.SDLK_BACKSPACE, "DIK_BACK", 14),
    "SDLK_BREAK": (318, "", 0),
    "SDLK_C": (99, "DIK_C", 46, sdl2.SDL_SCANCODE_C),
    "SDLK_CAPSLOCK": (301, "DIK_CAPITAL", 58),
    "SDLK_CARET": (94, "", 0),
    "SDLK_CLEAR": (12, "", 0),
    "SDLK_COLON": (58, "DIK_COLON", 146),
    "SDLK_COMMA": (44, "DIK_COMMA", 51),
    "SDLK_COMPOSE": (314, "", 0),
    "SDLK_D": (100, "DIK_D", 32, sdl2.SDL_SCANCODE_D),
    "SDLK_DELETE": (sdl2.SDLK_DELETE, "DIK_DELETE", 211),
    "SDLK_DOLLAR": (36, "", 0),
    "SDLK_DOWN": (
        sdl2.SDLK_DOWN,
        "DIK_DOWN",
        208,
        sdl2.SDL_SCANCODE_DOWN,
        sdl_key_codes["DOWN"],
    ),
    "SDLK_E": (101, "DIK_E", 18),
    "SDLK_END": (sdl2.SDLK_END, "DIK_END", 207),
    "SDLK_EQUALS": (61, "DIK_EQUALS", 13),
    "SDLK_ESCAPE": (sdl2.SDLK_ESCAPE, "DIK_ESCAPE", 1),
    "SDLK_EURO": (321, "", 0),
    "SDLK_EXCLAIM": (33, "", 0),
    "SDLK_F": (102, "DIK_F", 33),
    "SDLK_F1": (282, "DIK_F1", 59),
    "SDLK_F10": (291, "DIK_F10", 68),
    "SDLK_F11": (292, "DIK_F11", 87),
    "SDLK_F12": (293, "DIK_F12", 88),
    "SDLK_F13": (294, "DIK_F13", 100),
    "SDLK_F14": (295, "DIK_F14", 101),
    "SDLK_F15": (296, "DIK_F15", 102),
    "SDLK_F2": (283, "DIK_F2", 60),
    "SDLK_F3": (284, "DIK_F3", 61),
    "SDLK_F4": (285, "DIK_F4", 62),
    "SDLK_F5": (286, "DIK_F5", 63),
    "SDLK_F6": (287, "DIK_F6", 64),
    "SDLK_F7": (288, "DIK_F7", 65),
    "SDLK_F8": (289, "DIK_F8", 66),
    "SDLK_F9": (290, "DIK_F9", 67),
    "SDLK_G": (103, "DIK_G", 34),
    "SDLK_GREATER": (62, "", 0),
    "SDLK_H": (104, "DIK_H", 35),
    "SDLK_HASH": (35, "", 0),
    "SDLK_HELP": (315, "", 0),
    "SDLK_HOME": (sdl2.SDLK_HOME, "DIK_HOME", 199),
    "SDLK_I": (105, "DIK_I", 23),
    "SDLK_INSERT": (sdl2.SDLK_INSERT, "DIK_INSERT", 210),
    "SDLK_J": (106, "DIK_J", 36),
    "SDLK_K": (107, "DIK_K", 37),
    "SDLK_KP0": (sdl2.SDLK_KP_0, "DIK_NUMPAD0", 82),
    "SDLK_KP1": (sdl2.SDLK_KP_1, "DIK_NUMPAD1", 79),
    "SDLK_KP2": (sdl2.SDLK_KP_2, "DIK_NUMPAD2", 80),
    "SDLK_KP3": (sdl2.SDLK_KP_3, "DIK_NUMPAD3", 81),
    "SDLK_KP4": (sdl2.SDLK_KP_4, "DIK_NUMPAD4", 75),
    "SDLK_KP5": (sdl2.SDLK_KP_5, "DIK_NUMPAD5", 76),
    "SDLK_KP6": (sdl2.SDLK_KP_6, "DIK_NUMPAD6", 77),
    "SDLK_KP7": (sdl2.SDLK_KP_7, "DIK_NUMPAD7", 71),
    "SDLK_KP8": (sdl2.SDLK_KP_8, "DIK_NUMPAD8", 72),
    "SDLK_KP9": (sdl2.SDLK_KP_9, "DIK_NUMPAD9", 73),
    "SDLK_KP_DIVIDE": (267, "DIK_DIVIDE", 181),
    "SDLK_KP_ENTER": (271, "DIK_NUMPADENTER", 156),
    "SDLK_KP_EQUALS": (272, "", 141),
    "SDLK_KP_MINUS": (269, "DIK_SUBTRACT", 74),
    "SDLK_KP_MULTIPLY": (268, "DIK_MULTIPLY", 55),
    "SDLK_KP_PERIOD": (sdl2.SDLK_KP_PERIOD, "DIK_DECIMAL", 83),
    "SDLK_KP_PLUS": (270, "DIK_ADD", 78),
    "SDLK_L": (108, "DIK_L", 38, sdl2.SDL_SCANCODE_L),
    "SDLK_LALT": (308, "DIK_LMENU", 56, sdl2.SDL_SCANCODE_LALT),
    "SDLK_LCTRL": (
        sdl2.SDLK_LCTRL,
        "DIK_LCONTROL",
        29,
        sdl2.SDL_SCANCODE_LCTRL,
    ),
    "SDLK_LEFT": (
        sdl2.SDLK_LEFT,
        "DIK_LEFT",
        203,
        sdl2.SDL_SCANCODE_LEFT,
        sdl_key_codes["LEFT"],
    ),
    "SDLK_LEFTBRACKET": (91, "DIK_LBRACKET", 26),
    "SDLK_LEFTPAREN": (40, "", 0),
    "SDLK_LESS": (60, "", 0),
    "SDLK_LMETA": (310, "", 0),
    "SDLK_LSHIFT": (
        sdl2.SDLK_LSHIFT,
        "DIK_LSHIFT",
        42,
        sdl2.SDL_SCANCODE_LSHIFT,
    ),
    "SDLK_LSUPER": (311, "DIK_LWIN", 219),  # SDL_SCANCODE_LGUI ?
    "SDLK_M": (109, "DIK_M", 50),
    "SDLK_MENU": (319, "", 0),
    "SDLK_MINUS": (45, "DIK_MINUS", 12),
    "SDLK_MODE": (313, "", 0),
    "SDLK_N": (110, "DIK_N", 49),
    "SDLK_NUMLOCK": (300, "DIK_NUMLOCK", 69),
    "SDLK_O": (111, "DIK_O", 24),
    "SDLK_P": (112, "DIK_P", 25),
    "SDLK_PAGEDOWN": (sdl2.SDLK_PAGEDOWN, "DIK_NEXT", 209),
    "SDLK_PAGEUP": (sdl2.SDLK_PAGEUP, "DIK_PRIOR", 201),
    "SDLK_PAUSE": (19, "", 0),
    "SDLK_PERIOD": (46, "DIK_PERIOD", 52),
    "SDLK_PLUS": (43, "", 0),
    "SDLK_POWER": (320, "", 0),
    "SDLK_PRINT": (316, "", 0),
    "SDLK_Q": (113, "DIK_Q", 16),
    "SDLK_QUESTION": (63, "", 0),
    "SDLK_QUOTE": (39, "DIK_APOSTROPHE", 40),
    "SDLK_QUOTEDBL": (34, "", 0),
    "SDLK_R": (114, "DIK_R", 19),
    "SDLK_RALT": (
        sdl2.SDLK_RALT,
        "DIK_RMENU",
        184,
        sdl2.SDL_SCANCODE_RALT,
        sdl_key_codes["RALT"],
    ),
    "SDLK_RCTRL": (
        sdl2.SDLK_RCTRL,
        "DIK_RCONTROL",
        157,
        sdl2.SDL_SCANCODE_RCTRL,
        sdl_key_codes["RCTRL"],
    ),
    "SDLK_RETURN": (
        sdl2.SDLK_RETURN,
        "DIK_RETURN",
        28,
        sdl2.SDL_SCANCODE_RETURN,
    ),
    "SDLK_RIGHT": (
        sdl2.SDLK_RIGHT,
        "DIK_RIGHT",
        205,
        sdl2.SDL_SCANCODE_RIGHT,
        sdl_key_codes["RIGHT"],
    ),
    "SDLK_RIGHTBRACKET": (93, "DIK_RBRACKET", 27),
    "SDLK_RIGHTPAREN": (41, "", 0),
    "SDLK_RMETA": (309, "", 0),
    "SDLK_RSHIFT": (
        sdl2.SDLK_RSHIFT,
        "DIK_RSHIFT",
        54,
        sdl2.SDL_SCANCODE_RSHIFT,
    ),
    "SDLK_RSUPER": (312, "DIK_RWIN", 220),
    "SDLK_S": (115, "DIK_S", 31, sdl2.SDL_SCANCODE_S),
    "SDLK_SCROLLOCK": (302, "DIK_SCROLL", 70),
    "SDLK_SEMICOLON": (59, "DIK_SEMICOLON", 39),
    "SDLK_SLASH": (47, "DIK_SLASH", 53),
    "SDLK_SPACE": (sdl2.SDLK_SPACE, "DIK_SPACE", 57, sdl2.SDL_SCANCODE_SPACE),
    "SDLK_SYSREQ": (317, "DIK_SYSRQ", 183),
    "SDLK_T": (116, "DIK_T", 20),
    "SDLK_TAB": (9, "DIK_TAB", 15),
    "SDLK_U": (117, "DIK_U", 22),
    "SDLK_UNDERSCORE": (95, "", 147),
    "SDLK_UNDO": (322, "", 0),
    "SDLK_UP": (
        sdl2.SDLK_UP,
        "DIK_UP",
        200,
        sdl2.SDL_SCANCODE_UP,
        sdl_key_codes["UP"],
    ),
    "SDLK_V": (118, "DIK_V", 47),
    "SDLK_W": (119, "DIK_W", 17),
    "SDLK_WORLD_0": (160, ""),
    "SDLK_WORLD_1": (161, ""),
    "SDLK_WORLD_10": (170, ""),
    "SDLK_WORLD_11": (171, ""),
    "SDLK_WORLD_12": (172, ""),
    "SDLK_WORLD_13": (173, ""),
    "SDLK_WORLD_14": (174, ""),
    "SDLK_WORLD_15": (175, ""),
    "SDLK_WORLD_16": (176, ""),
    "SDLK_WORLD_17": (177, ""),
    "SDLK_WORLD_18": (178, ""),
    "SDLK_WORLD_19": (179, ""),
    "SDLK_WORLD_2": (162, ""),
    "SDLK_WORLD_20": (180, ""),
    "SDLK_WORLD_21": (181, ""),
    "SDLK_WORLD_22": (182, ""),
    "SDLK_WORLD_23": (183, ""),
    "SDLK_WORLD_24": (184, ""),
    "SDLK_WORLD_25": (185, ""),
    "SDLK_WORLD_26": (186, ""),
    "SDLK_WORLD_27": (187, ""),
    "SDLK_WORLD_28": (188, ""),
    "SDLK_WORLD_29": (189, ""),
    "SDLK_WORLD_3": (163, ""),
    "SDLK_WORLD_30": (190, ""),
    "SDLK_WORLD_31": (191, ""),
    "SDLK_WORLD_32": (192, ""),
    "SDLK_WORLD_33": (193, ""),
    "SDLK_WORLD_34": (194, ""),
    "SDLK_WORLD_35": (195, ""),
    "SDLK_WORLD_36": (196, ""),
    "SDLK_WORLD_37": (197, ""),
    "SDLK_WORLD_38": (198, ""),
    "SDLK_WORLD_39": (199, ""),
    "SDLK_WORLD_4": (164, ""),
    "SDLK_WORLD_40": (200, ""),
    "SDLK_WORLD_41": (201, ""),
    "SDLK_WORLD_42": (202, ""),
    "SDLK_WORLD_43": (203, ""),
    "SDLK_WORLD_44": (204, ""),
    "SDLK_WORLD_45": (205, ""),
    "SDLK_WORLD_46": (206, ""),
    "SDLK_WORLD_47": (207, ""),
    "SDLK_WORLD_48": (208, ""),
    "SDLK_WORLD_49": (209, ""),
    "SDLK_WORLD_5": (165, ""),
    "SDLK_WORLD_50": (210, ""),
    "SDLK_WORLD_51": (211, ""),
    "SDLK_WORLD_52": (212, ""),
    "SDLK_WORLD_53": (213, ""),
    "SDLK_WORLD_54": (214, ""),
    "SDLK_WORLD_55": (215, ""),
    "SDLK_WORLD_56": (216, ""),
    "SDLK_WORLD_57": (217, ""),
    "SDLK_WORLD_58": (218, ""),
    "SDLK_WORLD_59": (219, ""),
    "SDLK_WORLD_6": (166, ""),
    "SDLK_WORLD_60": (220, ""),
    "SDLK_WORLD_61": (221, ""),
    "SDLK_WORLD_62": (222, ""),
    "SDLK_WORLD_63": (223, ""),
    "SDLK_WORLD_64": (224, ""),
    "SDLK_WORLD_65": (225, ""),
    "SDLK_WORLD_66": (226, ""),
    "SDLK_WORLD_67": (227, ""),
    "SDLK_WORLD_68": (228, ""),
    "SDLK_WORLD_69": (229, ""),
    "SDLK_WORLD_7": (167, ""),
    "SDLK_WORLD_70": (230, ""),
    "SDLK_WORLD_71": (231, ""),
    "SDLK_WORLD_72": (232, ""),
    "SDLK_WORLD_73": (233, ""),
    "SDLK_WORLD_74": (234, ""),
    "SDLK_WORLD_75": (235, ""),
    "SDLK_WORLD_76": (236, ""),
    "SDLK_WORLD_77": (237, ""),
    "SDLK_WORLD_78": (238, ""),
    "SDLK_WORLD_79": (239, ""),
    "SDLK_WORLD_8": (168, ""),
    "SDLK_WORLD_80": (240, ""),
    "SDLK_WORLD_81": (241, ""),
    "SDLK_WORLD_82": (242, ""),
    "SDLK_WORLD_83": (243, ""),
    "SDLK_WORLD_84": (244, ""),
    "SDLK_WORLD_85": (245, ""),
    "SDLK_WORLD_86": (246, ""),
    "SDLK_WORLD_87": (247, ""),
    "SDLK_WORLD_88": (248, ""),
    "SDLK_WORLD_89": (249, ""),
    "SDLK_WORLD_9": (169, ""),
    "SDLK_WORLD_90": (250, ""),
    "SDLK_WORLD_91": (251, ""),
    "SDLK_WORLD_92": (252, ""),
    "SDLK_WORLD_93": (253, ""),
    "SDLK_WORLD_94": (254, ""),
    "SDLK_WORLD_95": (255, ""),
    "SDLK_X": (120, "DIK_X", 45, sdl2.SDL_SCANCODE_X),
    "SDLK_Y": (121, "DIK_Y", 21, sdl2.SDL_SCANCODE_Y),
    "SDLK_Z": (122, "DIK_Z", 44, sdl2.SDL_SCANCODE_Z),
}

sdl_key_code_to_name = {}
for key, value in key_table.items():
    sdl_key_code_to_name[value[0]] = key
