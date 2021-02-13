import re
import subprocess
import traceback

from fscore.system import System

if System.windows:
    # noinspection PyUnresolvedReferences
    try:
        import win32api  # type: ignore
    except ImportError:
        win32api = None
    # noinspection PyUnresolvedReferences
    try:
        import win32con  # type: ignore
    except ImportError:
        win32con = None
    EDS_RAWMODE = 2
elif System.macos:
    # noinspection PyUnresolvedReferences
    try:
        import Quartz  # type: ignore
    except ImportError:
        Quartz = None


class RefreshRateTool(object):
    def __init__(self, game_platform=None, game_refresh=None):
        self.game_platform = game_platform
        self.game_refresh = game_refresh

    def set_best_mode(self):
        print("RefreshRateTool.set_best_mode")
        current = self.get_current_mode()
        print("REFRESH RATE CONTROL: current mode is", current)
        modes = self.get_all_modes()
        mode_score_list = []
        for mode in modes:
            # print(mode)
            # for now, only consider same resolution
            if mode["width"] != current["width"]:
                continue
            if mode["height"] != current["height"]:
                continue
            # only consider modes with the same bpp
            if mode["bpp"] != current["bpp"]:
                continue
            score = self.calculate_mode_score(mode)
            if score is not None:
                mode_score_list.append((score, mode))
        if len(mode_score_list) == 0:
            print("REFRESH RATE TOOL: mode_score_list is empty")
            return
        print("REFRESH RATE TOOL:", mode_score_list)
        best_mode = mode_score_list[0][1]
        if best_mode == current:
            print("REFRESH RATE TOOL: using current mode")
        else:
            self.set_mode(best_mode)

    def calculate_mode_score(self, mode, debug=False):
        game_refresh = self.game_refresh
        if not self.game_refresh:
            if debug:
                print("REFRESH RATE TOOL: game refresh not specified")
            return None
        # in case of values such as -1 etc
        if game_refresh < 1:
            if debug:
                print("REFRESH RATE TOOL: game refresh not specified")
            return None
        display_refresh = mode["refresh"]
        if not display_refresh:
            if debug:
                print("REFRESH RATE TOOL: display refresh not found")
            return None
        # in case of values such as -1 etc
        if display_refresh < 1:
            if debug:
                print("REFRESH RATE TOOL: display refresh not found")
            return None
        diff = game_refresh - display_refresh
        # FIXME: configurable?
        # FIXME: configurable per platform?
        allowable_pos_diff = 1.01
        allowable_neg_diff = 1.01
        if debug:
            print(
                "REFRESH RATE TOOL: game refresh: {0} vs "
                "display refresh: {1}".format(game_refresh, display_refresh)
            )
            print(
                "REFRESH RATE TOOL: allow +{0}/-{1}".format(
                    allowable_pos_diff, allowable_neg_diff
                )
            )
            print("REFRESH RATE TOOL: diff: {0}".format(diff))
        if allowable_pos_diff > diff > -allowable_neg_diff:
            if debug:
                print("REFRESH RATE TOOL: allow vsync")
            return diff
        if debug:
            print("REFRESH RATE TOOL: deny vsync")
        return None

    def allow_vsync(self):
        """
        game_refresh = self.game_refresh
        if not self.game_refresh:
            print("REFRESH RATE TOOL: game refresh not specified")
            return False
        # in case of values such as -1 etc
        if game_refresh < 1:
            print("REFRESH RATE TOOL: game refresh not specified")
            return False
        display_refresh = self.get_display_refresh()
        if not display_refresh:
            print("REFRESH RATE TOOL: display refresh not found")
            return False
        # in case of values such as -1 etc
        if display_refresh < 1:
            print("REFRESH RATE TOOL: display refresh not found")
            return False
        diff = game_refresh - display_refresh
        # FIXME: configurable?
        # FIXME: configurable per platform?
        allowable_pos_diff = 1.01
        allowable_neg_diff = 1.01
        print("REFRESH RATE TOOL: game refresh: {0} vs "
                "display refresh: {1}".format(game_refresh,
                display_refresh))
        print("REFRESH RATE TOOL: allow +{0}/-{1}".format(allowable_pos_diff,
                allowable_neg_diff))
        print("REFRESH RATE TOOL: diff: {0}".format(diff))
        if diff < allowable_pos_diff and diff > -allowable_neg_diff:
            print("REFRESH RATE TOOL: allow vsync")
            return True
        print("REFRESH RATE TOOL: deny vsync")
        """
        current = self.get_current_mode()
        return self.calculate_mode_score(current, debug=True) is not None

    def get_display_refresh(self):
        # # FIXME:
        # if macosx:
        #     return 60.0
        # elif windows:
        #     import win32api
        #     device = win32api.EnumDisplayDevices()
        #     settings = win32api.EnumDisplaySettings(device.DeviceName, 0)
        #     return settings.DisplayFrequency()
        # # FIXME:
        # return 50.0
        # return None
        return self.get_current_mode()["refresh"]

    def get_current_mode(self):
        refresh = 0
        width = 640
        height = 480
        bpp = 0
        flags = 0

        if System.windows:
            if win32api:
                settings = win32api.EnumDisplaySettings(
                    None, win32con.ENUM_CURRENT_SETTINGS
                )
                refresh = float(settings.DisplayFrequency)
                width = int(settings.PelsWidth)
                height = int(settings.PelsHeight)
                bpp = int(settings.BitsPerPel)
                flags = int(settings.DisplayFlags)
        elif System.macosx:
            main_display = Quartz.CGMainDisplayID()
            current_display = Quartz.CGDisplayPrimaryDisplay(main_display)
            current_mode = Quartz.CGDisplayCopyDisplayMode(current_display)
            width = Quartz.CGDisplayModeGetWidth(current_mode)
            height = Quartz.CGDisplayModeGetHeight(current_mode)
            refresh = Quartz.CGDisplayModeGetRefreshRate(current_mode)
            if not refresh:
                print("WARNING: returned refresh rate was 0. assuming 60 Hz")
                refresh = 60
            # A bit weird that it crashes, since this is supposed to be a
            # copy of the mode...?
            print(
                "FIXME: Not calling Quartz.CGDisplayModeRelease("
                "current_mode), seems to crash pygame on exit..."
            )
            # Quartz.CGDisplayModeRelease(current_mode)
            flags = 0
            bpp = None
        else:
            return self._get_current_mode_x()

        return {
            "width": width,
            "height": height,
            "refresh": refresh,
            "bpp": bpp,
            "flags": flags,
        }

    def get_all_modes(self):
        modes = []
        if System.windows:
            k = 0
            while True:
                try:
                    settings = win32api.EnumDisplaySettingsEx(
                        None, k, EDS_RAWMODE
                    )
                except win32api.error:
                    break
                refresh = float(settings.DisplayFrequency)
                width = int(settings.PelsWidth)
                height = int(settings.PelsHeight)
                bpp = int(settings.BitsPerPel)
                flags = int(settings.DisplayFlags)
                # print(width, height, refresh, bpp, flags)
                modes.append(
                    {
                        "width": width,
                        "height": height,
                        "refresh": refresh,
                        "bpp": bpp,
                        "flags": flags,
                    }
                )
                k += 1
        elif System.macos:
            # FIXME:
            pass
        else:
            modes = self._get_all_modes_x()
        # modes.extend(self.get_override_modes())
        return modes

    # def get_override_modes(self):
    #     modes = []
    #     k = 0
    #     while True:
    #         mode_string = pyapp.user.ini.get('ForceDisplayModes/%d' % k)
    #         if not mode_string:
    #             break
    #         mode_string = mode_string.lower()
    #         mode = {}
    #         w, rest = mode_string.split('x')
    #         h, rest = rest.split('@')
    #         r, rest = rest.split('hz')
    #         mode['width'] = int(w)
    #         mode['height'] = int(h)
    #         mode['bpp'] = 32
    #         mode['refresh'] = int(r)
    #         mode['flags'] = 0
    #         modes.append(mode)
    #         k += 1
    #     print("get_override_modes returning", modes)
    #     return modes

    def set_mode(self, mode):
        # if windows:
        #     self._set_mode_windows(mode)
        # elif macosx:
        #     # FIXME:
        #     print("WARNING: mode settings is not supported on this "
        #             "platform yet")
        # else:
        #     self._set_mode_x(mode)

        print("FIXME: Currently disabled set_mode")
        return

    def _set_mode_windows(self, mode):
        print("REFRESH RATE TOOL: setting mode", mode)
        if not win32api:
            print("win32api not available, returning")
            return False
        k = 0
        while True:
            try:
                settings = win32api.EnumDisplaySettingsEx(None, k, EDS_RAWMODE)
            except win32api.error:
                break
            refresh = float(settings.DisplayFrequency)
            width = int(settings.PelsWidth)
            height = int(settings.PelsHeight)
            bpp = int(settings.BitsPerPel)
            flags = int(settings.DisplayFlags)
            # print(width, height, refresh, bpp, flags)
            # modes.append({'width': width, 'height': height,
            #        'refresh': refresh, 'bpp': bpp, 'flags': flags})
            if (
                width == mode["width"]
                and height == mode["height"]
                and refresh == mode["refresh"]
                and bpp == mode["bpp"]
                and flags == mode["flags"]
            ):

                # print("trying to override with refresh", int(round(self.game_refresh)))
                # #refresh == mode['refresh'] and \
                # settings.DisplayFrequency = int(round(self.game_refresh))
                # result = win32api.ChangeDisplaySettings(settings,
                #         win32con.CDS_UPDATEREGISTRY) #win32con.CDS_FULLSCREEN)
                #         #0) #win32con.CDS_FULLSCREEN)
                # if result == win32con.DISP_CHANGE_SUCCESSFUL:
                #     print("display change was successful")
                #     return True
                # print("failed, falling back to ", mode['refresh'])
                # settings.DisplayFrequency = mode['refresh']
                print("found windows mode, changing display settings")
                result = win32api.ChangeDisplaySettings(
                    settings, win32con.CDS_UPDATEREGISTRY
                )
                # win32con.CDS_FULLSCREEN)

                if result == win32con.DISP_CHANGE_SUCCESSFUL:
                    print("display change was successful")
                    return True
                else:
                    print("display change failed, result =", result)
                    return False
            k += 1

        # for omode in self.get_override_modes():
        #     print("trying override mode", omode)
        #     if omode['width'] == mode['width'] and \
        #             omode['height'] == mode['height'] and \
        #             omode['refresh'] == mode['refresh'] and \
        #             omode['bpp'] == mode['bpp'] and \
        #             omode['flags'] == mode['flags']:
        #         settings.PelsWidth = omode['width']
        #         settings.PelsHeight = omode['height']
        #         settings.BitsPerPel = omode['bpp']
        #         settings.DisplayFlags = omode['flags']
        #         settings.DisplayFrequency = omode['refresh']
        #         result = win32api.ChangeDisplaySettings(settings,
        #                 win32con.CDS_UPDATEREGISTRY) #win32con.CDS_FULLSCREEN)
        #                 #0) #win32con.CDS_FULLSCREEN)
        #         if result == win32con.DISP_CHANGE_SUCCESSFUL:
        #             print("display change was successful")
        #             return True
        #         else:
        #             print("display change failed, result =", result)
        #             return False
        return False

    def _set_mode_x(self, mode):
        print("REFRESH RATE TOOL: setting mode", mode)
        args = [
            "/usr/bin/env",
            "xrandr",
            "-s",
            "{0}x{1}".format(mode["width"], mode["height"]),
            "-r",
            str(mode["refresh"]),
        ]
        p = subprocess.Popen(args)
        p.wait()

    def _get_all_modes_x(self):
        modes = []
        self._get_current_mode_x(modes=modes)
        return modes

    def _get_current_mode_x(self, modes=[]):
        modes[:] = []
        mode = {"width": 0, "height": 0, "refresh": 0.0, "bpp": 0, "flags": 0}
        args = ["/usr/bin/env", "xrandr", "-q"]
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in p.stdout:
            line = line.decode("ISO-8859-1")
            if not line.startswith(" "):
                continue
            line = line.strip()
            line = line.replace("+", "")
            # collapse multiple spaces
            line = re.sub(" +", " ", line).strip()
            parts = line.split(" ")
            resolution = parts[0]
            rates = parts[1:]
            width, height = resolution.split("x")
            width = int(width)
            height = int(height)
            print(rates)
            for rate in rates:
                if rate[-1] == "*":
                    refresh = float(rate[:-1])
                    mode["width"] = width
                    mode["height"] = height
                    mode["refresh"] = refresh
                    modes.append(
                        {
                            "width": width,
                            "height": height,
                            "refresh": float(rate[:-1]),
                            "bpp": 0,
                            "flags": 0,
                        }
                    )
                else:
                    modes.append(
                        {
                            "width": width,
                            "height": height,
                            "refresh": float(rate),
                            "bpp": 0,
                            "flags": 0,
                        }
                    )
        return mode

    def screens_xrandr(self):
        try:
            return self._screens_xrandr()
        except Exception:
            traceback.print_exc()
            return {}

    @staticmethod
    def _screens_xrandr():
        screens = {}
        screen = {"modes": []}
        args = ["/usr/bin/env", "xrandr", "-q"]
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        data = p.stdout.read().decode("ISO-8859-1")
        # data = XRANDR_TEST_DATA
        for line in data.split("\n"):
            last_refresh_rate = 0.0
            if line.startswith(" "):
                line = line.replace("*", " * ")
                line = line.replace("+", " + ")
                line = re.sub(" +", " ", line).strip()
                parts = line.split(" ")
                # May not always have a resolution here, could be
                # a named mode instead
                # resolution_str = parts[0]
                # w, h = resolution_str.split("x")
                # w = int(w)
                # h = int(h)
                for part in parts[1:]:
                    if part == "*":
                        screen["refresh_rate"] = last_refresh_rate
                    elif part == "+":
                        pass
                    else:
                        last_refresh_rate = float(part)
                        # screen["modes"].append({
                        #     "width": w,
                        #     "height": h,
                        #     "refresh_rate": last_refresh_rate
                        # })
                        pass
            else:
                line = re.sub(" +", " ", line).strip()
                parts = line.split(" ")
                for part in parts:
                    if "x" not in part or "+" not in part:
                        continue
                    geom = part.replace("x", " ").replace("+", " ")
                    print(geom)
                    w, h, x, y = geom.split(" ")
                    w = int(w)
                    h = int(h)
                    x = int(x)
                    y = int(y)
                    screen = {
                        "x": x,
                        "y": x,
                        "width": x,
                        "height": x,
                        "modes": [],
                        "refresh_rate": 0.0,
                    }
                    screens[(x, y, w, h)] = screen
        print(screens)
        return screens


# noinspection SpellCheckingInspection
XRANDR_TEST_DATA = """\
Screen 0: minimum 8 x 8, current 1920 x 1080, maximum 32767 x 32767
DP1 disconnected (normal left inverted right x axis y axis)
DP2 disconnected (normal left inverted right x axis y axis)
DP3 disconnected (normal left inverted right x axis y axis)
HDMI1 connected primary 1920x1080+0+0 (normal left inverted right x \
axis y axis)\ 531mm x 298mm
   1920x1080     60.00*+
   Amiga         50.02
   1680x1050     59.88
   1600x900      60.00
   1280x1024     75.02    60.02
   1280x800      59.91
   1152x864      75.00
   1280x720      60.00
   1024x768      75.08    60.00
   832x624       74.55
   800x600       75.00    60.32
   640x480       75.00    60.00
   720x400       70.08
HDMI2 disconnected (normal left inverted right x axis y axis)
HDMI3 disconnected (normal left inverted right x axis y axis)
VGA1 connected (normal left inverted right x axis y axis)
   1680x1050     59.95 +
   AmigaVGA      49.97
   1600x1000     60.01
   1280x1024     75.02
   1440x900      59.89
   1280x960      60.00
   1152x864      75.00
   1152x720      59.97
   1024x768      75.08    60.00
   832x624       74.55
   800x600       75.00    60.32
   640x480       75.00    60.00
   720x400       70.08
VIRTUAL1 disconnected (normal left inverted right x axis y axis)
"""
