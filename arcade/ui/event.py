from functools import lru_cache

from fscore.system import System
from fsgamesys.util import sdl2
from fsui.qt import QEvent, Qt


class KeySym:
    def __init__(self):
        self.sym = 0


class Key:
    def __init__(self):
        self.keysym = KeySym()


class Event:
    def __init__(self):
        self.type = 0
        self.key = None

    @classmethod
    def create_key_event(cls, ev):
        # event = Event()
        # event.key = Key()
        event = {}
        if ev.type() == QEvent.KeyPress:
            # event.type = sdl2.SDL_KEYDOWN
            event["type"] = "key-down"
        elif ev.type() == QEvent.KeyRelease:
            # event.type = sdl2.SDL_KEYUP
            event["type"] = "key-up"
        else:
            raise Exception("Unexpected event type in create_key_event")
        # key_map = get_key_map()
        # print(ev.key(), "vs", Qt.Key.Key_Shift)
        # event.key.keysym.sym = key_map.get(ev.key(), 0)
        # event["key"] = key_map.get(ev.key(), 0)
        event["key"] = get_key(ev)
        return event

    @classmethod
    def create_mouse_event(cls, ev, window_size):
        event = {}
        if ev.type() == QEvent.MouseMove:
            event["type"] = "mouse-motion"
        elif ev.type() == QEvent.MouseButtonPress:
            event["type"] = "mouse-press"
        elif ev.type() == QEvent.MouseButtonRelease:
            event["type"] = "mouse-release"
        elif ev.type() == QEvent.MouseButtonDblClick:
            event["type"] = "mouse-press"
        else:
            raise Exception("Unexpected event type in create_mouse_event")
        # Normalize coordinates to a 1920x1080 OpenGL-like coordinate system
        x, y = ev.x(), ev.y()
        x = (x * 1920) // window_size[0]
        y = 1080 - (y * 1080) // window_size[1]
        event["pos"] = x, y
        return event

    @classmethod
    def create_fake_mouse_event(cls, type_, x, y, window_size):
        event = {"type": type_}
        x = (x * 1920) // window_size[0]
        y = 1080 - (y * 1080) // window_size[1]
        event["pos"] = x, y
        return event


def get_key(ev):
    print("Qt key:", ev.key(), int(ev.modifiers()), Qt.KeypadModifier)
    if System.macos:
        # FIXME: TODO: CHECK
        # if ev.key() == Qt.Key.Key_AMeta:
        #     print("Control key, native virtual code:", ev.nativeVirtualCode())
        # elif ev.key() == Qt.Key.Key_Shift:
        pass
    else:
        if ev.key() == Qt.Key.Key_Control:
            print("Control key, native scan code:", ev.nativeScanCode())
            if ev.nativeScanCode() == 105:  # Linux
                return sdl2.SDLK_RCTRL
            # FIXME: TODO: WINDOWS
            return sdl2.SDLK_LCTRL
        elif ev.key() == Qt.Key.Key_Shift:
            print("Shift key, native scan code:", ev.nativeScanCode())
            if ev.nativeScanCode() == 62:  # Linux
                return sdl2.SDLK_RSHIFT
            # FIXME: TODO: WINDOWS
            return sdl2.SDLK_LSHIFT
    # On OS X, the KeypadModifier value will also be set when an arrow
    # key is pressed as the arrow keys are considered part of the keypad.
    # http://doc.qt.io/qt-5/qt.html#KeyboardModifier-enum
    macos_arrow_key = System.macos and ev.key() in [
        Qt.Key.Key_Left,
        Qt.Key.Key_Right,
        Qt.Key.Key_Up,
        Qt.Key.Key_Down,
    ]
    if int(ev.modifiers()) & Qt.KeypadModifier and not macos_arrow_key:
        print("keypad!")
        print(ev.key(), "vs", Qt.Key.Key_4)
        return {
            Qt.Key.Key_Insert: sdl2.SDLK_KP_0,
            Qt.Key.Key_End: sdl2.SDLK_KP_1,
            Qt.Key.Key_Down: sdl2.SDLK_KP_2,
            Qt.Key.Key_PageDown: sdl2.SDLK_KP_3,
            Qt.Key.Key_Left: sdl2.SDLK_KP_4,
            Qt.Key.Key_Clear: sdl2.SDLK_KP_5,
            Qt.Key.Key_Right: sdl2.SDLK_KP_6,
            Qt.Key.Key_Home: sdl2.SDLK_KP_7,
            Qt.Key.Key_Up: sdl2.SDLK_KP_8,
            Qt.Key.Key_PageUp: sdl2.SDLK_KP_9,
            Qt.Key.Key_Delete: sdl2.SDLK_KP_PERIOD,
        }.get(ev.key(), 0)
    key_map = get_key_map()
    return key_map.get(ev.key(), 0)


@lru_cache()
def get_key_map():
    result = {
        Qt.Key.Key_Escape: sdl2.SDLK_ESCAPE,
        Qt.Key.Key_Tab: sdl2.SDLK_TAB,
        # Qt.Key.Key_Backtab	0x01000002
        Qt.Key.Key_Backspace: sdl2.SDLK_BACKSPACE,
        Qt.Key.Key_Return: sdl2.SDLK_RETURN,
        # Typically located on the keypad.
        Qt.Key.Key_Enter: sdl2.SDLK_KP_ENTER,
        Qt.Key.Key_Insert: sdl2.SDLK_INSERT,
        Qt.Key.Key_Delete: sdl2.SDLK_DELETE,
        # The Pause/Break key (Note: Not anything to do with pausing media).
        Qt.Key.Key_Pause: sdl2.SDLK_PAUSE,
        # Qt.Key.Key_Print	0x01000009
        # Qt.Key.Key_SysReq	0x0100000a
        # Qt.Key.Key.Key_Clear	0x0100000b
        Qt.Key.Key_Home: sdl2.SDLK_HOME,
        Qt.Key.Key_End: sdl2.SDLK_END,
        Qt.Key.Key_Left: sdl2.SDLK_LEFT,
        Qt.Key.Key_Up: sdl2.SDLK_UP,
        Qt.Key.Key_Right: sdl2.SDLK_RIGHT,
        Qt.Key.Key_Down: sdl2.SDLK_DOWN,
        Qt.Key.Key_PageUp: sdl2.SDLK_PAGEUP,
        Qt.Key.Key_PageDown: sdl2.SDLK_PAGEDOWN,
        # FIXME: LSHIFT vs RSHIFT
        Qt.Key.Key_Shift: sdl2.SDLK_LSHIFT,
        # On Mac OS X, this corresponds to the Command keys.
        # Qt.Key.Key_Control	0x01000021
        # FIXME: LCTRL vs RCTRL, OS X, etc
        Qt.Key.Key_Control: sdl2.SDLK_LCTRL,
        # On Mac OS X, this corresponds to the Control keys. On Windows
        # keyboards, this key is mapped to the Windows key.
        # Qt.Key.Key_Meta	0x01000022
        # Qt.Key.Key_Alt	0x01000023
        # On Windows, when the KeyDown event for this key is sent, the
        # Ctrl+Alt modifiers are also set.
        # Qt.Key.Key_AltGr	0x01001103
        # Qt.Key.Key_CapsLock	0x01000024
        # Qt.Key.Key_NumLock	0x01000025
        # Qt.Key.Key_ScrollLock	0x01000026
        Qt.Key.Key_F1: sdl2.SDLK_F1,
        Qt.Key.Key_F2: sdl2.SDLK_F2,
        Qt.Key.Key_F3: sdl2.SDLK_F3,
        Qt.Key.Key_F4: sdl2.SDLK_F4,
        Qt.Key.Key_F5: sdl2.SDLK_F5,
        Qt.Key.Key_F6: sdl2.SDLK_F6,
        Qt.Key.Key_F7: sdl2.SDLK_F7,
        Qt.Key.Key_F8: sdl2.SDLK_F8,
        Qt.Key.Key_F9: sdl2.SDLK_F9,
        Qt.Key.Key_F10: sdl2.SDLK_F10,
        # Qt.Key.Key_F11	0x0100003a
        # Qt.Key.Key_F12	0x0100003b
        # Qt.Key.Key_F13	0x0100003c
        # Qt.Key.Key_F14	0x0100003d
        # Qt.Key.Key_F15	0x0100003e
        # Qt.Key.Key_F16	0x0100003f
        # Qt.Key.Key_F17	0x01000040
        # Qt.Key.Key_F18	0x01000041
        # Qt.Key.Key_F19	0x01000042
        # Qt.Key.Key_F20	0x01000043
        # Qt.Key.Key_F21	0x01000044
        # Qt.Key.Key_F22	0x01000045
        # Qt.Key.Key_F23	0x01000046
        # Qt.Key.Key_F24	0x01000047
        # Qt.Key.Key_F25	0x01000048
        # Qt.Key.Key_F26	0x01000049
        # Qt.Key.Key_F27	0x0100004a
        # Qt.Key.Key_F28	0x0100004b
        # Qt.Key.Key_F29	0x0100004c
        # Qt.Key.Key_F30	0x0100004d
        # Qt.Key.Key_F31	0x0100004e
        # Qt.Key.Key_F32	0x0100004f
        # Qt.Key.Key_F33	0x01000050
        # Qt.Key.Key_F34	0x01000051
        # Qt.Key.Key_F35	0x01000052
        # Qt.Key.Key_Super_L	0x01000053
        # Qt.Key.Key_Super_R	0x01000054
        # Qt.Key.Key_Menu	0x01000055
        # Qt.Key.Key_Hyper_L	0x01000056
        # Qt.Key.Key_Hyper_R	0x01000057
        # Qt.Key.Key_Help	0x01000058
        # Qt.Key.Key_Direction_L	0x01000059
        # Qt.Key.Key_Direction_R	0x01000060
        Qt.Key.Key_Space: sdl2.SDLK_SPACE,
        # Qt.Key.Key_Any	Key_Space
        # Qt.Key.Key_Exclam	0x21
        # Qt.Key.Key_QuoteDbl	0x22
        # Qt.Key.Key_NumberSign	0x23
        # Qt.Key.Key_Dollar	0x24
        # Qt.Key.Key_Percent	0x25
        # Qt.Key.Key_Ampersand	0x26
        # Qt.Key.Key_Apostrophe	0x27
        # Qt.Key.Key_ParenLeft	0x28
        # Qt.Key.Key_ParenRight	0x29
        # Qt.Key.Key_Asterisk	0x2a
        # Qt.Key.Key_Plus	0x2b
        # Qt.Key.Key_Comma	0x2c
        # Qt.Key.Key_Minus	0x2d
        # Qt.Key.Key_Period	0x2e
        # Qt.Key.Key_Slash	0x2f
        # Qt.Key.Key_0	0x30
        # Qt.Key.Key_1	0x31
        # Qt.Key.Key_2	0x32
        # Qt.Key.Key_3	0x33
        # Qt.Key.Key_4	0x34
        # Qt.Key.Key_5	0x35
        # Qt.Key.Key_6	0x36
        # Qt.Key.Key_7	0x37
        # Qt.Key.Key_8	0x38
        # Qt.Key.Key_9	0x39
        # Qt.Key.Key_Colon	0x3a
        # Qt.Key.Key_Semicolon	0x3b
        # Qt.Key.Key_Less	0x3c
        # Qt.Key.Key_Equal	0x3d
        # Qt.Key.Key_Greater	0x3e
        # Qt.Key.Key_Question	0x3f
        # Qt.Key.Key_At	0x40
        Qt.Key.Key_A: sdl2.SDLK_a,
        Qt.Key.Key_B: sdl2.SDLK_b,
        Qt.Key.Key_C: sdl2.SDLK_c,
        Qt.Key.Key_D: sdl2.SDLK_d,
        Qt.Key.Key_E: sdl2.SDLK_e,
        Qt.Key.Key_F: sdl2.SDLK_f,
        Qt.Key.Key_G: sdl2.SDLK_g,
        Qt.Key.Key_H: sdl2.SDLK_h,
        Qt.Key.Key_I: sdl2.SDLK_i,
        Qt.Key.Key_J: sdl2.SDLK_j,
        Qt.Key.Key_K: sdl2.SDLK_k,
        Qt.Key.Key_L: sdl2.SDLK_l,
        Qt.Key.Key_M: sdl2.SDLK_m,
        Qt.Key.Key_N: sdl2.SDLK_n,
        Qt.Key.Key_O: sdl2.SDLK_o,
        Qt.Key.Key_P: sdl2.SDLK_p,
        Qt.Key.Key_Q: sdl2.SDLK_q,
        Qt.Key.Key_R: sdl2.SDLK_r,
        Qt.Key.Key_S: sdl2.SDLK_s,
        Qt.Key.Key_T: sdl2.SDLK_t,
        Qt.Key.Key_U: sdl2.SDLK_u,
        Qt.Key.Key_V: sdl2.SDLK_v,
        Qt.Key.Key_W: sdl2.SDLK_w,
        Qt.Key.Key_X: sdl2.SDLK_x,
        Qt.Key.Key_Y: sdl2.SDLK_y,
        Qt.Key.Key_Z: sdl2.SDLK_z,
        # FIXME: Depends on keymap?
        Qt.Key.Key_BracketLeft: sdl2.SDLK_LEFTBRACKET,
        # Qt.Key.Key_Backslash	0x5c
        # FIXME: Depends on keymap?
        Qt.Key.Key_BracketRight: sdl2.SDLK_RIGHTBRACKET,
        # Qt.Key.Key_BracketRight	0x5d
        # Qt.Key.Key_AsciiCircum	0x5e
        # Qt.Key.Key_Underscore	0x5f
        # Qt.Key.Key_QuoteLeft	0x60
        # Qt.Key.Key_BraceLeft	0x7b
        # Qt.Key.Key_Bar	0x7c
        # Qt.Key.Key_BraceRight	0x7d
        # Qt.Key.Key_AsciiTilde	0x7e
        # Qt.Key.Key_nobreakspace	0x0a0
        # Qt.Key.Key_exclamdown	0x0a1
        # Qt.Key.Key_cent	0x0a2
        # Qt.Key.Key_sterling	0x0a3
        # Qt.Key.Key_currency	0x0a4
        # Qt.Key.Key_yen	0x0a5
        # Qt.Key.Key_brokenbar	0x0a6
        # Qt.Key.Key_section	0x0a7
        # Qt.Key.Key_diaeresis	0x0a8
        # Qt.Key.Key_copyright	0x0a9
        # Qt.Key.Key_ordfeminine	0x0aa
        # Qt.Key.Key_guillemotleft	0x0ab
        # Qt.Key.Key_notsign	0x0ac
        # Qt.Key.Key_hyphen	0x0ad
        # Qt.Key.Key_registered	0x0ae
        # Qt.Key.Key_macron	0x0af
        # Qt.Key.Key_degree	0x0b0
        # Qt.Key.Key_plusminus	0x0b1
        # Qt.Key.Key_twosuperior	0x0b2
        # Qt.Key.Key_threesuperior	0x0b3
        # Qt.Key.Key_acute	0x0b4
        # Qt.Key.Key_mu	0x0b5
        # Qt.Key.Key_paragraph	0x0b6
        # Qt.Key.Key_periodcentered	0x0b7
        # Qt.Key.Key_cedilla	0x0b8
        # Qt.Key.Key_onesuperior	0x0b9
        # Qt.Key.Key_masculine	0x0ba
        # Qt.Key.Key_guillemotright	0x0bb
        # Qt.Key.Key_onequarter	0x0bc
        # Qt.Key.Key_onehalf	0x0bd
        # Qt.Key.Key_threequarters	0x0be
        # Qt.Key.Key_questiondown	0x0bf
        # Qt.Key.Key_Agrave	0x0c0
        # Qt.Key.Key_Aacute	0x0c1
        # Qt.Key.Key_Acircumflex	0x0c2
        # Qt.Key.Key_Atilde	0x0c3
        # Qt.Key.Key_Adiaeresis	0x0c4
        # Qt.Key.Key_Aring	0x0c5
        # Qt.Key.Key_AE	0x0c6
        # Qt.Key.Key_Ccedilla	0x0c7
        # Qt.Key.Key_Egrave	0x0c8
        # Qt.Key.Key_Eacute	0x0c9
        # Qt.Key.Key_Ecircumflex	0x0ca
        # Qt.Key.Key_Ediaeresis	0x0cb
        # Qt.Key.Key_Igrave	0x0cc
        # Qt.Key.Key_Iacute	0x0cd
        # Qt.Key.Key_Icircumflex	0x0ce
        # Qt.Key.Key_Idiaeresis	0x0cf
        # Qt.Key.Key_ETH	0x0d0
        # Qt.Key.Key_Ntilde	0x0d1
        # Qt.Key.Key_Ograve	0x0d2
        # Qt.Key.Key_Oacute	0x0d3
        # Qt.Key.Key_Ocircumflex	0x0d4
        # Qt.Key.Key_Otilde	0x0d5
        # Qt.Key.Key_Odiaeresis	0x0d6
        # Qt.Key.Key_multiply	0x0d7
        # Qt.Key.Key_Ooblique	0x0d8
        # Qt.Key.Key_Ugrave	0x0d9
        # Qt.Key.Key_Uacute	0x0da
        # Qt.Key.Key_Ucircumflex	0x0db
        # Qt.Key.Key_Udiaeresis	0x0dc
        # Qt.Key.Key_Yacute	0x0dd
        # Qt.Key.Key_THORN	0x0de
        # Qt.Key.Key_ssharp	0x0df
        # Qt.Key.Key_division	0x0f7
        # Qt.Key.Key_ydiaeresis	0x0ff
        # Qt.Key.Key_Multi_key	0x01001120
        # Qt.Key.Key_Codeinput	0x01001137
        # Qt.Key.Key_ASingleCandidate	0x0100113c
        # Qt.Key.Key_AMultipleCandidate	0x0100113d
        # Qt.Key.Key_APreviousCandidate	0x0100113e
        # Qt.Key.Key_AMode_switch	0x0100117e
        # Qt.Key.Key_AKanji	0x01001121
        # Qt.Key.Key_AMuhenkan	0x01001122
        # Qt.Key.Key_AHenkan	0x01001123
        # Qt.Key.Key_ARomaji	0x01001124
        # Qt.Key.Key_AHiragana	0x01001125
        # Qt.Key.Key_AKatakana	0x01001126
        # Qt.Key.Key_AHiragana_Katakana	0x01001127
        # Qt.Key.Key_AZenkaku	0x01001128
        # Qt.Key.Key_AHankaku	0x01001129
        # Qt.Key.Key_AZenkaku_Hankaku	0x0100112a
        # Qt.Key.Key_ATouroku	0x0100112b
        # Qt.Key.Key_AMassyo	0x0100112c
        # Qt.Key.Key_AKana_Lock	0x0100112d
        # Qt.Key.Key_AKana_Shift	0x0100112e
        # Qt.Key.Key_AEisu_Shift	0x0100112f
        # Qt.Key.Key_AEisu_toggle	0x01001130
        # Qt.Key.Key_AHangul	0x01001131
        # Qt.Key.Key_AHangul_Start	0x01001132
        # Qt.Key.Key_AHangul_End	0x01001133
        # Qt.Key.Key_AHangul_Hanja	0x01001134
        # Qt.Key.Key_AHangul_Jamo	0x01001135
        # Qt.Key.Key_AHangul_Romaja	0x01001136
        # Qt.Key.Key_AHangul_Jeonja	0x01001138
        # Qt.Key.Key_AHangul_Banja	0x01001139
        # Qt.Key.Key_AHangul_PreHanja	0x0100113a
        # Qt.Key.Key_AHangul_PostHanja	0x0100113b
        # Qt.Key.Key_AHangul_Special	0x0100113f
        # Qt.Key.Key_ADead_Grave	0x01001250
        # Qt.Key.Key_ADead_Acute	0x01001251
        # Qt.Key.Key_ADead_Circumflex	0x01001252
        # Qt.Key.Key_ADead_Tilde	0x01001253
        # Qt.Key.Key_ADead_Macron	0x01001254
        # Qt.Key.Key_ADead_Breve	0x01001255
        # Qt.Key.Key_ADead_Abovedot	0x01001256
        # Qt.Key.Key_ADead_Diaeresis	0x01001257
        # Qt.Key.Key_ADead_Abovering	0x01001258
        # Qt.Key.Key_ADead_Doubleacute	0x01001259
        # Qt.Key.Key_ADead_Caron	0x0100125a
        # Qt.Key.Key_ADead_Cedilla	0x0100125b
        # Qt.Key.Key_ADead_Ogonek	0x0100125c
        # Qt.Key.Key_ADead_Iota	0x0100125d
        # Qt.Key.Key_ADead_Voiced_Sound	0x0100125e
        # Qt.Key.Key_ADead_Semivoiced_Sound	0x0100125f
        # Qt.Key.Key_ADead_Belowdot	0x01001260
        # Qt.Key.Key_ADead_Hook	0x01001261
        # Qt.Key.Key_ADead_Horn	0x01001262
        # Qt.Key.Key_ABack	0x01000061
        # Qt.Key.Key_AForward	0x01000062
        # Qt.Key.Key_AStop	0x01000063
        # Qt.Key.Key_ARefresh	0x01000064
        # Qt.Key.Key_AVolumeDown	0x01000070
        # Qt.Key.Key_AVolumeMute	0x01000071
        # Qt.Key.Key_AVolumeUp	0x01000072
        # Qt.Key.Key_ABassBoost	0x01000073
        # Qt.Key.Key_ABassUp	0x01000074
        # Qt.Key.Key_ABassDown	0x01000075
        # Qt.Key.Key_ATrebleUp	0x01000076
        # Qt.Key.Key_ATrebleDown	0x01000077
        # A key setting the state of the media player to play
        # Qt.Key.Key_AMediaPlay	0x01000080
        # A key setting the state of the media player to stop
        # Qt.Key.Key_AMediaStop	0x01000081
        # Qt.Key.Key_AMediaPrevious	0x01000082
        # Qt.Key.Key_AMediaNext	0x01000083
        # Qt.Key.Key_AMediaRecord	0x01000084
        # A key setting the state of the media player to pause
        # (Note: not the pause/break key)
        # Qt.Key.Key_AMediaPause	0x1000085
        # A key to toggle the play/pause state in the media player
        # (rather than setting an absolute state)
        # Qt.Key.Key_AMediaTogglePlayPause	0x1000086
        # Qt.Key.Key_HomePage	0x01000090
        # Qt.Key.Key_AFavorites	0x01000091
        # Qt.Key.Key_ASearch	0x01000092
        # Qt.Key.Key_AStandby	0x01000093
        # Qt.Key.Key_AOpenUrl	0x01000094
        # Qt.Key.Key_ALaunchMail	0x010000a0
        # Qt.Key.Key_ALaunchMedia	0x010000a1
        # On X11 this key is mapped to "My Computer" (XF86XK_MyComputer) key
        # for legacy reasons.
        # Qt.Key.Key_ALaunch0	0x010000a2
        # On X11 this key is mapped to "Calculator" (XF86XK_Calculator) key
        # for legacy reasons.
        # Qt.Key.Key_ALaunch1	0x010000a3
        # On X11 this key is mapped to XF86XK_Launch0 key for legacy reasons.
        # Qt.Key.Key_ALaunch2	0x010000a4
        # Qt.Key.Key_ALaunch3	0x010000a5	On X11 this key is mapped to
        # XF86XK_Launch1 key for legacy reasons.
        # Qt.Key.Key_ALaunch4	0x010000a6	On X11 this key is mapped to
        # XF86XK_Launch2 key for legacy reasons.
        # Qt.Key.Key_ALaunch5	0x010000a7	On X11 this key is mapped to
        # XF86XK_Launch3 key for legacy reasons.
        # Qt.Key.Key_ALaunch6	0x010000a8	On X11 this key is mapped to
        # XF86XK_Launch4 key for legacy reasons.
        # Qt.Key.Key_ALaunch7	0x010000a9	On X11 this key is mapped to
        # XF86XK_Launch5 key for legacy reasons.
        # Qt.Key.Key_ALaunch8	0x010000aa	On X11 this key is mapped to
        # XF86XK_Launch6 key for legacy reasons.
        # Qt.Key.Key_ALaunch9	0x010000ab	On X11 this key is mapped to
        # XF86XK_Launch7 key for legacy reasons.
        # Qt.Key.Key_ALaunchA	0x010000ac	On X11 this key is mapped to
        # XF86XK_Launch8 key for legacy reasons.
        # Qt.Key.Key_ALaunchB	0x010000ad	On X11 this key is mapped to
        # XF86XK_Launch9 key for legacy reasons.
        # Qt.Key.Key_ALaunchC	0x010000ae	On X11 this key is mapped to
        # XF86XK_LaunchA key for legacy reasons.
        # Qt.Key.Key_ALaunchD	0x010000af	On X11 this key is mapped to
        # XF86XK_LaunchB key for legacy reasons.
        # Qt.Key.Key_ALaunchE	0x010000b0	On X11 this key is mapped to
        # XF86XK_LaunchC key for legacy reasons.
        # Qt.Key.Key_ALaunchF	0x010000b1	On X11 this key is mapped to
        # XF86XK_LaunchD key for legacy reasons.
        # Qt.Key.Key_ALaunchG	0x0100010e	On X11 this key is mapped to
        # XF86XK_LaunchE key for legacy reasons.
        # Qt.Key.Key_ALaunchH	0x0100010f	On X11 this key is mapped to
        # XF86XK_LaunchF key for legacy reasons.
        # Qt.Key.Key_AMonBrightnessUp	0x010000b2
        # Qt.Key.Key_AMonBrightnessDown	0x010000b3
        # Qt.Key.Key_AKeyboardLightOnOff	0x010000b4
        # Qt.Key.Key_AKeyboardBrightnessUp	0x010000b5
        # Qt.Key.Key_AKeyboardBrightnessDown	0x010000b6
        # Qt.Key.Key_APowerOff	0x010000b7
        # Qt.Key.Key_AWakeUp	0x010000b8
        # Qt.Key.Key_AEject	0x010000b9
        # Qt.Key.Key_AScreenSaver	0x010000ba
        # Qt.Key.Key_AWWW	0x010000bb
        # Qt.Key.Key_AMemo	0x010000bc
        # Qt.Key.Key_ALightBulb	0x010000bd
        # Qt.Key.Key_AShop	0x010000be
        # Qt.Key.Key_AHistory	0x010000bf
        # Qt.Key.Key_AAddFavorite	0x010000c0
        # Qt.Key.Key_AHotLinks	0x010000c1
        # Qt.Key.Key_ABrightnessAdjust	0x010000c2
        # Qt.Key.Key_AFinance	0x010000c3
        # Qt.Key.Key_ACommunity	0x010000c4
        # Qt.Key.Key_AAudioRewind	0x010000c5
        # Qt.Key.Key_ABackForward	0x010000c6
        # Qt.Key.Key_AApplicationLeft	0x010000c7
        # Qt.Key.Key_AApplicationRight	0x010000c8
        # Qt.Key.Key_ABook	0x010000c9
        # Qt.Key.Key_ACD	0x010000ca
        # On X11 this key is not mapped for legacy reasons.
        # Use Qt.Key.Key_ALaunch1 instead.
        # Qt.Key.Key_ACalculator	0x010000cb
        # Qt.Key.Key_AToDoList	0x010000cc
        # Qt.Key.Key_ClearGrab	0x010000cd
        # Qt.Key.Key_AClose	0x010000ce
        # Qt.Key.Key_ACopy	0x010000cf
        # Qt.Key.Key_ACut	0x010000d0
        # Qt.Key.Key_ADisplay	0x010000d1
        # Qt.Key.Key_ADOS	0x010000d2
        # Qt.Key.Key_ADocuments	0x010000d3
        # Qt.Key.Key_AExcel	0x010000d4
        # Qt.Key.Key_AExplorer	0x010000d5
        # Qt.Key.Key_AGame	0x010000d6
        # Qt.Key.Key_AGo	0x010000d7
        # Qt.Key.Key_AiTouch	0x010000d8
        # Qt.Key.Key_ALogOff	0x010000d9
        # Qt.Key.Key_AMarket	0x010000da
        # Qt.Key.Key_AMeeting	0x010000db
        # Qt.Key.Key_AMenuKB	0x010000dc
        # Qt.Key.Key_AMenuPB	0x010000dd
        # Qt.Key.Key_AMySites	0x010000de
        # Qt.Key.Key_ANews	0x010000df
        # Qt.Key.Key_AOfficeHome	0x010000e0
        # Qt.Key.Key_AOption	0x010000e1
        # Qt.Key.Key_APaste	0x010000e2
        # Qt.Key.Key_APhone	0x010000e3
        # Qt.Key.Key_ACalendar	0x010000e4
        # Qt.Key.Key_AReply	0x010000e5
        # Qt.Key.Key_AReload	0x010000e6
        # Qt.Key.Key_ARotateWindows	0x010000e7
        # Qt.Key.Key_ARotationPB	0x010000e8
        # Qt.Key.Key_ARotationKB	0x010000e9
        # Qt.Key.Key_ASave	0x010000ea
        # Qt.Key.Key_ASend	0x010000eb
        # Qt.Key.Key_ASpell	0x010000ec
        # Qt.Key.Key_ASplitScreen	0x010000ed
        # Qt.Key.Key_ASupport	0x010000ee
        # Qt.Key.Key_ATaskPane	0x010000ef
        # Qt.Key.Key_ATerminal	0x010000f0
        # Qt.Key.Key_ATools	0x010000f1
        # Qt.Key.Key_ATravel	0x010000f2
        # Qt.Key.Key_AVideo	0x010000f3
        # Qt.Key.Key_AWord	0x010000f4
        # Qt.Key.Key_AXfer	0x010000f5
        # Qt.Key.Key_AZoomIn	0x010000f6
        # Qt.Key.Key_AZoomOut	0x010000f7
        # Qt.Key.Key_AAway	0x010000f8
        # Qt.Key.Key_AMessenger	0x010000f9
        # Qt.Key.Key_AWebCam	0x010000fa
        # Qt.Key.Key_AMailForward	0x010000fb
        # Qt.Key.Key_APictures	0x010000fc
        # Qt.Key.Key_AMusic	0x010000fd
        # Qt.Key.Key_ABattery	0x010000fe
        # Qt.Key.Key_ABluetooth	0x010000ff
        # Qt.Key.Key_AWLAN	0x01000100
        # Qt.Key.Key_AUWB	0x01000101
        # Qt.Key.Key_AAudioForward	0x01000102
        # Qt.Key.Key_AAudioRepeat	0x01000103
        # Qt.Key.Key_AAudioRandomPlay	0x01000104
        # Qt.Key.Key_ASubtitle	0x01000105
        # Qt.Key.Key_AAudioCycleTrack	0x01000106
        # Qt.Key.Key_ATime	0x01000107
        # Qt.Key.Key_AHibernate	0x01000108
        # Qt.Key.Key_AView	0x01000109
        # Qt.Key.Key_ATopMenu	0x0100010a
        # Qt.Key.Key_APowerDown	0x0100010b
        # Qt.Key.Key_ASuspend	0x0100010c
        # Qt.Key.Key_AContrastAdjust	0x0100010d
        # Qt.Key.Key_AMediaLast	0x0100ffff
        # Qt.Key.Key_Aunknown	0x01ffffff
        # A key to answer or initiate a call (see Qt.Key.Key_AToggleCallHangup
        # for a key to toggle current call state)
        # Qt.Key.Key_ACall	0x01100004
        # A key to activate the camera shutter
        # Qt.Key.Key_ACamera	0x01100020
        # Qt.Key.Key_ACameraFocus	0x01100021	A key to focus the camera
        # Qt.Key.Key_AContext1	0x01100000
        # Qt.Key.Key_AContext2	0x01100001
        # Qt.Key.Key_AContext3	0x01100002
        # Qt.Key.Key_AContext4	0x01100003
        # Qt.Key.Key_AFlip	0x01100006
        # A key to end an ongoing call (see Qt.Key.Key_AToggleCallHangup for a
        # key to toggle current call state)
        # Qt.Key.Key_AHangup	0x01100005
        # Qt.Key.Key_ANo	0x01010002
        # Qt.Key.Key_ASelect	0x01010000
        # Qt.Key.Key_AYes	0x01010001
        # A key to toggle the current call state (ie. either answer, or
        # hangup) depending on current call state
        # Qt.Key.Key_AToggleCallHangup	0x01100007
        # Qt.Key.Key_AVoiceDial	0x01100008
        # Qt.Key.Key_ALastNumberRedial	0x01100009
        # Qt.Key.Key_AExecute	0x01020003
        # Qt.Key.Key_APrinter	0x01020002
        # Qt.Key.Key_APlay	0x01020005
        # Qt.Key.Key_ASleep	0x01020004
        # Qt.Key.Key_AZoom	0x01020006
        # Qt.Key.Key_ACancel	0x01020001
    }
    return result
