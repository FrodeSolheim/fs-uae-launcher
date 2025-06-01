from functools import lru_cache

from fsgs.util import sdl2
from fsbc.system import macosx
from fsui.qt import Qt, QEvent


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
        if ev.type() == QEvent.Type.KeyPress:
            # event.type = sdl2.SDL_KEYDOWN
            event["type"] = "key-down"
        elif ev.type() == QEvent.Type.KeyRelease:
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
        if ev.type() == QEvent.Type.MouseMove:
            event["type"] = "mouse-motion"
        elif ev.type() == QEvent.Type.MouseButtonPress:
            event["type"] = "mouse-press"
        elif ev.type() == QEvent.Type.MouseButtonRelease:
            event["type"] = "mouse-release"
        elif ev.type() == QEvent.Type.MouseButtonDblClick:
            event["type"] = "mouse-press"
        else:
            raise Exception("Unexpected event type in create_mouse_event")
        # Normalize coordinates to a 1920x1080 OpenGL-like coordinate system
        pos = ev.position()
        x, y = pos.x(), pos.y()
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
    # print("Qt key:", ev.key(), int(ev.modifiers()), Qt.KeypadModifier)
    if macosx:
        # FIXME: TODO: CHECK
        # if ev.key() == Qt.Key.Key_Meta:
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
    macos_arrow_key = macosx and ev.key() in [
        Qt.Key.Key_Left,
        Qt.Key.Key_Right,
        Qt.Key.Key_Up,
        Qt.Key.Key_Down,
    ]
    if int(ev.modifiers().value) & Qt.KeyboardModifier.KeypadModifier.value and not macos_arrow_key:
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
        # Qt.Key.Key_Clear	0x0100000b
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
        # Qt.Key.Key_SingleCandidate	0x0100113c
        # Qt.Key.Key_MultipleCandidate	0x0100113d
        # Qt.Key.Key_PreviousCandidate	0x0100113e
        # Qt.Key.Key_Mode_switch	0x0100117e
        # Qt.Key.Key_Kanji	0x01001121
        # Qt.Key.Key_Muhenkan	0x01001122
        # Qt.Key.Key_Henkan	0x01001123
        # Qt.Key.Key_Romaji	0x01001124
        # Qt.Key.Key_Hiragana	0x01001125
        # Qt.Key.Key_Katakana	0x01001126
        # Qt.Key.Key_Hiragana_Katakana	0x01001127
        # Qt.Key.Key_Zenkaku	0x01001128
        # Qt.Key.Key_Hankaku	0x01001129
        # Qt.Key.Key_Zenkaku_Hankaku	0x0100112a
        # Qt.Key.Key_Touroku	0x0100112b
        # Qt.Key.Key_Massyo	0x0100112c
        # Qt.Key.Key_Kana_Lock	0x0100112d
        # Qt.Key.Key_Kana_Shift	0x0100112e
        # Qt.Key.Key_Eisu_Shift	0x0100112f
        # Qt.Key.Key_Eisu_toggle	0x01001130
        # Qt.Key.Key_Hangul	0x01001131
        # Qt.Key.Key_Hangul_Start	0x01001132
        # Qt.Key.Key_Hangul_End	0x01001133
        # Qt.Key.Key_Hangul_Hanja	0x01001134
        # Qt.Key.Key_Hangul_Jamo	0x01001135
        # Qt.Key.Key_Hangul_Romaja	0x01001136
        # Qt.Key.Key_Hangul_Jeonja	0x01001138
        # Qt.Key.Key_Hangul_Banja	0x01001139
        # Qt.Key.Key_Hangul_PreHanja	0x0100113a
        # Qt.Key.Key_Hangul_PostHanja	0x0100113b
        # Qt.Key.Key_Hangul_Special	0x0100113f
        # Qt.Key.Key_Dead_Grave	0x01001250
        # Qt.Key.Key_Dead_Acute	0x01001251
        # Qt.Key.Key_Dead_Circumflex	0x01001252
        # Qt.Key.Key_Dead_Tilde	0x01001253
        # Qt.Key.Key_Dead_Macron	0x01001254
        # Qt.Key.Key_Dead_Breve	0x01001255
        # Qt.Key.Key_Dead_Abovedot	0x01001256
        # Qt.Key.Key_Dead_Diaeresis	0x01001257
        # Qt.Key.Key_Dead_Abovering	0x01001258
        # Qt.Key.Key_Dead_Doubleacute	0x01001259
        # Qt.Key.Key_Dead_Caron	0x0100125a
        # Qt.Key.Key_Dead_Cedilla	0x0100125b
        # Qt.Key.Key_Dead_Ogonek	0x0100125c
        # Qt.Key.Key_Dead_Iota	0x0100125d
        # Qt.Key.Key_Dead_Voiced_Sound	0x0100125e
        # Qt.Key.Key_Dead_Semivoiced_Sound	0x0100125f
        # Qt.Key.Key_Dead_Belowdot	0x01001260
        # Qt.Key.Key_Dead_Hook	0x01001261
        # Qt.Key.Key_Dead_Horn	0x01001262
        # Qt.Key.Key_Back	0x01000061
        # Qt.Key.Key_Forward	0x01000062
        # Qt.Key.Key_Stop	0x01000063
        # Qt.Key.Key_Refresh	0x01000064
        # Qt.Key.Key_VolumeDown	0x01000070
        # Qt.Key.Key_VolumeMute	0x01000071
        # Qt.Key.Key_VolumeUp	0x01000072
        # Qt.Key.Key_BassBoost	0x01000073
        # Qt.Key.Key_BassUp	0x01000074
        # Qt.Key.Key_BassDown	0x01000075
        # Qt.Key.Key_TrebleUp	0x01000076
        # Qt.Key.Key_TrebleDown	0x01000077
        # A key setting the state of the media player to play
        # Qt.Key.Key_MediaPlay	0x01000080
        # A key setting the state of the media player to stop
        # Qt.Key.Key_MediaStop	0x01000081
        # Qt.Key.Key_MediaPrevious	0x01000082
        # Qt.Key.Key_MediaNext	0x01000083
        # Qt.Key.Key_MediaRecord	0x01000084
        # A key setting the state of the media player to pause
        # (Note: not the pause/break key)
        # Qt.Key.Key_MediaPause	0x1000085
        # A key to toggle the play/pause state in the media player
        # (rather than setting an absolute state)
        # Qt.Key.Key_MediaTogglePlayPause	0x1000086
        # Qt.Key.Key_HomePage	0x01000090
        # Qt.Key.Key_Favorites	0x01000091
        # Qt.Key.Key_Search	0x01000092
        # Qt.Key.Key_Standby	0x01000093
        # Qt.Key.Key_OpenUrl	0x01000094
        # Qt.Key.Key_LaunchMail	0x010000a0
        # Qt.Key.Key_LaunchMedia	0x010000a1
        # On X11 this key is mapped to "My Computer" (XF86XK_MyComputer) key
        # for legacy reasons.
        # Qt.Key.Key_Launch0	0x010000a2
        # On X11 this key is mapped to "Calculator" (XF86XK_Calculator) key
        # for legacy reasons.
        # Qt.Key.Key_Launch1	0x010000a3
        # On X11 this key is mapped to XF86XK_Launch0 key for legacy reasons.
        # Qt.Key.Key_Launch2	0x010000a4
        # Qt.Key.Key_Launch3	0x010000a5	On X11 this key is mapped to
        # XF86XK_Launch1 key for legacy reasons.
        # Qt.Key.Key_Launch4	0x010000a6	On X11 this key is mapped to
        # XF86XK_Launch2 key for legacy reasons.
        # Qt.Key.Key_Launch5	0x010000a7	On X11 this key is mapped to
        # XF86XK_Launch3 key for legacy reasons.
        # Qt.Key.Key_Launch6	0x010000a8	On X11 this key is mapped to
        # XF86XK_Launch4 key for legacy reasons.
        # Qt.Key.Key_Launch7	0x010000a9	On X11 this key is mapped to
        # XF86XK_Launch5 key for legacy reasons.
        # Qt.Key.Key_Launch8	0x010000aa	On X11 this key is mapped to
        # XF86XK_Launch6 key for legacy reasons.
        # Qt.Key.Key_Launch9	0x010000ab	On X11 this key is mapped to
        # XF86XK_Launch7 key for legacy reasons.
        # Qt.Key.Key_LaunchA	0x010000ac	On X11 this key is mapped to
        # XF86XK_Launch8 key for legacy reasons.
        # Qt.Key.Key_LaunchB	0x010000ad	On X11 this key is mapped to
        # XF86XK_Launch9 key for legacy reasons.
        # Qt.Key.Key_LaunchC	0x010000ae	On X11 this key is mapped to
        # XF86XK_LaunchA key for legacy reasons.
        # Qt.Key.Key_LaunchD	0x010000af	On X11 this key is mapped to
        # XF86XK_LaunchB key for legacy reasons.
        # Qt.Key.Key_LaunchE	0x010000b0	On X11 this key is mapped to
        # XF86XK_LaunchC key for legacy reasons.
        # Qt.Key.Key_LaunchF	0x010000b1	On X11 this key is mapped to
        # XF86XK_LaunchD key for legacy reasons.
        # Qt.Key.Key_LaunchG	0x0100010e	On X11 this key is mapped to
        # XF86XK_LaunchE key for legacy reasons.
        # Qt.Key.Key_LaunchH	0x0100010f	On X11 this key is mapped to
        # XF86XK_LaunchF key for legacy reasons.
        # Qt.Key.Key_MonBrightnessUp	0x010000b2
        # Qt.Key.Key_MonBrightnessDown	0x010000b3
        # Qt.Key.Key_KeyboardLightOnOff	0x010000b4
        # Qt.Key.Key_KeyboardBrightnessUp	0x010000b5
        # Qt.Key.Key_KeyboardBrightnessDown	0x010000b6
        # Qt.Key.Key_PowerOff	0x010000b7
        # Qt.Key.Key_WakeUp	0x010000b8
        # Qt.Key.Key_Eject	0x010000b9
        # Qt.Key.Key_ScreenSaver	0x010000ba
        # Qt.Key.Key_WWW	0x010000bb
        # Qt.Key.Key_Memo	0x010000bc
        # Qt.Key.Key_LightBulb	0x010000bd
        # Qt.Key.Key_Shop	0x010000be
        # Qt.Key.Key_History	0x010000bf
        # Qt.Key.Key_AddFavorite	0x010000c0
        # Qt.Key.Key_HotLinks	0x010000c1
        # Qt.Key.Key_BrightnessAdjust	0x010000c2
        # Qt.Key.Key_Finance	0x010000c3
        # Qt.Key.Key_Community	0x010000c4
        # Qt.Key.Key_AudioRewind	0x010000c5
        # Qt.Key.Key_BackForward	0x010000c6
        # Qt.Key.Key_ApplicationLeft	0x010000c7
        # Qt.Key.Key_ApplicationRight	0x010000c8
        # Qt.Key.Key_Book	0x010000c9
        # Qt.Key.Key_CD	0x010000ca
        # On X11 this key is not mapped for legacy reasons.
        # Use Qt.Key.Key_Launch1 instead.
        # Qt.Key.Key_Calculator	0x010000cb
        # Qt.Key.Key_ToDoList	0x010000cc
        # Qt.Key.Key_ClearGrab	0x010000cd
        # Qt.Key.Key_Close	0x010000ce
        # Qt.Key.Key_Copy	0x010000cf
        # Qt.Key.Key_Cut	0x010000d0
        # Qt.Key.Key_Display	0x010000d1
        # Qt.Key.Key_DOS	0x010000d2
        # Qt.Key.Key_Documents	0x010000d3
        # Qt.Key.Key_Excel	0x010000d4
        # Qt.Key.Key_Explorer	0x010000d5
        # Qt.Key.Key_Game	0x010000d6
        # Qt.Key.Key_Go	0x010000d7
        # Qt.Key.Key_iTouch	0x010000d8
        # Qt.Key.Key_LogOff	0x010000d9
        # Qt.Key.Key_Market	0x010000da
        # Qt.Key.Key_Meeting	0x010000db
        # Qt.Key.Key_MenuKB	0x010000dc
        # Qt.Key.Key_MenuPB	0x010000dd
        # Qt.Key.Key_MySites	0x010000de
        # Qt.Key.Key_News	0x010000df
        # Qt.Key.Key_OfficeHome	0x010000e0
        # Qt.Key.Key_Option	0x010000e1
        # Qt.Key.Key_Paste	0x010000e2
        # Qt.Key.Key_Phone	0x010000e3
        # Qt.Key.Key_Calendar	0x010000e4
        # Qt.Key.Key_Reply	0x010000e5
        # Qt.Key.Key_Reload	0x010000e6
        # Qt.Key.Key_RotateWindows	0x010000e7
        # Qt.Key.Key_RotationPB	0x010000e8
        # Qt.Key.Key_RotationKB	0x010000e9
        # Qt.Key.Key_Save	0x010000ea
        # Qt.Key.Key_Send	0x010000eb
        # Qt.Key.Key_Spell	0x010000ec
        # Qt.Key.Key_SplitScreen	0x010000ed
        # Qt.Key.Key_Support	0x010000ee
        # Qt.Key.Key_TaskPane	0x010000ef
        # Qt.Key.Key_Terminal	0x010000f0
        # Qt.Key.Key_Tools	0x010000f1
        # Qt.Key.Key_Travel	0x010000f2
        # Qt.Key.Key_Video	0x010000f3
        # Qt.Key.Key_Word	0x010000f4
        # Qt.Key.Key_Xfer	0x010000f5
        # Qt.Key.Key_ZoomIn	0x010000f6
        # Qt.Key.Key_ZoomOut	0x010000f7
        # Qt.Key.Key_Away	0x010000f8
        # Qt.Key.Key_Messenger	0x010000f9
        # Qt.Key.Key_WebCam	0x010000fa
        # Qt.Key.Key_MailForward	0x010000fb
        # Qt.Key.Key_Pictures	0x010000fc
        # Qt.Key.Key_Music	0x010000fd
        # Qt.Key.Key_Battery	0x010000fe
        # Qt.Key.Key_Bluetooth	0x010000ff
        # Qt.Key.Key_WLAN	0x01000100
        # Qt.Key.Key_UWB	0x01000101
        # Qt.Key.Key_AudioForward	0x01000102
        # Qt.Key.Key_AudioRepeat	0x01000103
        # Qt.Key.Key_AudioRandomPlay	0x01000104
        # Qt.Key.Key_Subtitle	0x01000105
        # Qt.Key.Key_AudioCycleTrack	0x01000106
        # Qt.Key.Key_Time	0x01000107
        # Qt.Key.Key_Hibernate	0x01000108
        # Qt.Key.Key_View	0x01000109
        # Qt.Key.Key_TopMenu	0x0100010a
        # Qt.Key.Key_PowerDown	0x0100010b
        # Qt.Key.Key_Suspend	0x0100010c
        # Qt.Key.Key_ContrastAdjust	0x0100010d
        # Qt.Key.Key_MediaLast	0x0100ffff
        # Qt.Key.Key_unknown	0x01ffffff
        # A key to answer or initiate a call (see Qt.Key.Key_ToggleCallHangup
        # for a key to toggle current call state)
        # Qt.Key.Key_Call	0x01100004
        # A key to activate the camera shutter
        # Qt.Key.Key_Camera	0x01100020
        # Qt.Key.Key_CameraFocus	0x01100021	A key to focus the camera
        # Qt.Key.Key_Context1	0x01100000
        # Qt.Key.Key_Context2	0x01100001
        # Qt.Key.Key_Context3	0x01100002
        # Qt.Key.Key_Context4	0x01100003
        # Qt.Key.Key_Flip	0x01100006
        # A key to end an ongoing call (see Qt.Key.Key_ToggleCallHangup for a
        # key to toggle current call state)
        # Qt.Key.Key_Hangup	0x01100005
        # Qt.Key.Key_No	0x01010002
        # Qt.Key.Key_Select	0x01010000
        # Qt.Key.Key_Yes	0x01010001
        # A key to toggle the current call state (ie. either answer, or
        # hangup) depending on current call state
        # Qt.Key.Key_ToggleCallHangup	0x01100007
        # Qt.Key.Key_VoiceDial	0x01100008
        # Qt.Key.Key_LastNumberRedial	0x01100009
        # Qt.Key.Key_Execute	0x01020003
        # Qt.Key.Key_Printer	0x01020002
        # Qt.Key.Key_Play	0x01020005
        # Qt.Key.Key_Sleep	0x01020004
        # Qt.Key.Key_Zoom	0x01020006
        # Qt.Key.Key_Cancel	0x01020001
    }
    return result
