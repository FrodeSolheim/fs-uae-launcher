# FSGS - Common functionality for FS Game System.
# Copyright (C) 2013-2019  Frode Solheim <frode@solheim.dev>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
FSGS Game driver for Atari ST family.

TODO:

* Support saving disk changes.
* Support (persistent) save states.
* Check and/or fix support for vsync.
* NTSC vs PAL?.
* Proper joystick support and keyboard joystick emulation.
* Mouse in port 0.
* Multiple floppies and floppy swapping.
* Screenshots are saved to the (temp) current working directory, not the
  global screenshots directory.

"""
import os

from fscore.system import System
from fsgamesys.drivers.gamedriver import GameDriver
from fsgamesys.knownfiles import KnownFile
from fsgamesys.options.option import Option
from fsgamesys.platforms import PLATFORM_ATARI

ST_PLATFORM_ID = "st"
ST_PLATFORM_NAME = "Atari ST"
ST_JOYSTICK_CONTROLLER_TYPE = "joystick"
ST_JOYSTICK_CONTROLLER = {
    "type": ST_JOYSTICK_CONTROLLER_TYPE,
    "description": "Joystick",
    "mapping_name": "atari",
}
NO_CONTROLLER_TYPE = "none"
NO_CONTROLLER = {
    "type": NO_CONTROLLER_TYPE,
    "description": "None",
    "mapping_name": "",
}
ST_PORTS = [
    {
        "description": "Port 1",
        "types": [ST_JOYSTICK_CONTROLLER, NO_CONTROLLER],
        "type_option": "st_port_1_type",
        "device_option": "st_port_1",
    },
    {
        "description": "Port 2",
        "types": [ST_JOYSTICK_CONTROLLER, NO_CONTROLLER],
        "type_option": "st_port_2_type",
        "device_option": "st_port_2",
    },
]
ST_MODEL_520ST = "520st"
ST_MODEL_520STFM = "520stfm"
ST_MODEL_520STE = "520ste"
ST_MODEL_1040ST = "1040st"
ST_MODEL_1040STFM = "1040stfm"
ST_MODEL_1040STE = "1040ste"
ST_WIDTH = 832
# ST_HEIGHT = 576
ST_HEIGHT = 552
# noinspection SpellCheckingInspection
ST_TOS_102_UK = KnownFile(
    "87900a40a890fdf03bd08be6c60cc645855cbce5",
    PLATFORM_ATARI,
    "TOS v1.02 (1987)(Atari Corp)(Mega ST)(GB)[MEGA TOS].img",
)
# noinspection SpellCheckingInspection
ST_TOS_104_UK = KnownFile(
    "9526ef63b9cb1d2a7109e278547ae78a5c1db6c6",
    PLATFORM_ATARI,
    "TOS v1.04 (1989)(Atari Corp)(Mega ST)(GB)[Rainbow TOS].img",
)
# noinspection SpellCheckingInspection
ST_TOS_1062_UK = KnownFile(
    "70db24a7c252392755849f78940a41bfaebace71",
    PLATFORM_ATARI,
    "TOS v1.62 (1990)(Atari)(GB)[STE TOS, Rev 2][STE].img",
)


class HatariDriver(GameDriver):
    PORTS = ST_PORTS

    def __init__(self, fsgc, fsemu=False):
        super().__init__(fsgc)
        if fsemu:
            self.emulator.name = "hatari-fs"
        else:
            self.emulator.name = "hatari"
        self.floppies_dir = self.temp_dir("Media")
        self.tos_file = self.temp_file("tos.img")
        self.config_file = self.temp_file("hatari.cfg")
        self.helper = AtariHelper(self.config)
        self.floppies = []

    def prepare(self):
        super().prepare()
        self.prepare_tos()
        self.prepare_floppies()
        with open(self.config_file.path, "w", encoding="UTF-8") as f:
            self.write_config_file(f)
        self.emulator.args.extend(["--configfile", self.config_file.path])

    def install(self):
        super().install()

    def run(self):
        super().run()

    def finish(self):
        super().finish()

    def prepare_floppies(self):
        original_floppies = []
        if self.config["floppy_drive_0"]:
            original_floppies.append(self.config["floppy_drive_0"])
        floppies = []
        for p in original_floppies:
            dest_path = os.path.join(
                self.floppies_dir.path, os.path.basename(p)
            )
            self.files.add(dest_path, source=p)
            floppies.append(dest_path)
        self.floppies = floppies

    def prepare_tos(self):
        tos_file = self.helper.tos_file()
        self.files.add(
            self.tos_file.path, sha1=tos_file.sha1, description=tos_file.name
        )

    def write_config_file(self, f):
        f.write("[Screen]\n")
        # f.write("nMonitorType = 1\n")
        # f.write("nFrameSkips = 5\n")
        if self.use_fullscreen():
            f.write("bFullScreen = TRUE\n")
        else:
            f.write("bFullScreen = FALSE\n")
        # f.write("bKeepResolution = TRUE\n")
        f.write("bAllowOverscan = FALSE\n")
        # f.write("nSpec512Threshold = 1\n")
        # f.write("nForceBpp = 0\n")
        # f.write("bAspectCorrect = TRUE\n")
        # f.write("bAspectCorrect = FALSE\n")
        # f.write("bUseExtVdiResolutions = FALSE\n")
        # f.write("nVdiWidth = 640\n")
        # f.write("nVdiHeight = 480\n")
        # f.write("nVdiColors = 2\n")
        # f.write("bMouseWarp = TRUE\n")
        f.write("bShowStatusbar = FALSE\n")
        f.write("bShowDriveLed = FALSE\n")
        # f.write("bCrop = FALSE\n")
        # f.write("bForceMax = FALSE\n")
        # f.write("nMaxWidth = 832\n")
        # f.write("nMaxHeight = 588\n")
        f.write("nRenderScaleQuality = 1\n")

        # FIXME: vsync
        f.write("bUseVsync = 0\n")

        f.write("\n[Sound]\n")
        if self.use_audio_frequency():
            f.write("nPlaybackFreq = {0}\n".format(self.use_audio_frequency()))

        f.write("\n[Floppy]\n")
        num_floppy_drives = 2
        inserted_floppies = self.floppies[:num_floppy_drives]
        if len(inserted_floppies) > 0:
            f.write(
                "szDiskAFileName = {path}\n".format(path=inserted_floppies[0])
            )
        if len(inserted_floppies) > 1:
            f.write(
                "szDiskBFileName = {path}\n".format(path=inserted_floppies[1])
            )

        f.write("\n[ROM]\n")
        f.write("szTosImageFileName = {}\n".format(self.tos_file.path))
        f.write("bPatchTOS = FALSE\n")

        f.write("\n[System]\n")
        if self.helper.model_family() == "ST":
            f.write("nModelType = 0\n")
        elif self.helper.model_family() == "STE":
            f.write("nModelType = 2\n")
        else:
            print("WARNING: UNKNOWN ST MODEL FAMILY")
        accuracy = self.helper.accuracy()
        if accuracy == 1:
            f.write("bCycleExactCpu = TRUE\n")
            f.write("bCompatibleCpu = TRUE\n")
            f.write("bPatchTimerD = FALSE\n")
        elif accuracy == 0:
            f.write("bCycleExactCpu = FALSE\n")
            f.write("bCompatibleCpu = TRUE\n")
            f.write("bPatchTimerD = TRUE\n")
        else:
            f.write("bCycleExactCpu = FALSE\n")
            f.write("bCompatibleCpu = FALSE\n")
            f.write("bPatchTimerD = TRUE\n")
        f.write("bFastBoot = FALSE\n")
        f.write("bBlitter = FALSE\n")

        # if self.use_stretching():
        #     self.env["FSGS_STRETCH"] = "1"
        # else:
        #     self.env["FSGS_STRETCH"] = "0"

        f.write("\n[Memory]\n")
        memory = self.helper.memory()
        if memory == 1024:
            f.write("nMemorySize = 1\n")
        elif memory == 512:
            f.write("nMemorySize = 0\n")
        else:
            print("WARNING: UNKNOWN ST MEMORY SIZE")

        self.configure_input(f)

    def configure_input(self, f):

        for port in self.ports:

            # for i in range(6):
            # port_index = i
            # joystick_mode = 0
            # joystick_mode = 1  # Real joystick

            joystick_index = 0
            if port.device.type == "keyboard":
                joystick_mode = 2  # Keyboard emulation
            elif port.device.type == "mouse":
                joystick_mode = 0
            elif port.device.type == "none":
                joystick_mode = 0
            else:
                joystick_mode = 1
                joystick_index = port.device.index

            hatari_port = port.index
            if hatari_port < 2:
                hatari_port = 1 - hatari_port  # Swap 0 and 1
            f.write("\n[Joystick{}]\n".format(hatari_port))
            f.write("nJoystickMode = {}]\n".format(joystick_mode))
            f.write("bEnableAutoFire = FALSE\n")
            f.write("bEnableJumpOnFire2 = FALSE\n")
            f.write("nJoyId = {}\n".format(joystick_index))
            f.write("kUp = Up\n")
            f.write("kDown = Down\n")
            f.write("kLeft = Left\n")
            f.write("kRight = Right\n")
            if System.macos:
                f.write("kFire = Right Alt\n")
            else:
                f.write("kFire = Right Ctrl\n")

    # def configure_fullscreen_scaling(self):
    #     """Configure scaling for the SDL 1.x version of Hatari-FS.

    #     Not (currently) used with the SDL 2.x version of Hatari-FS.
    #     """
    #     sx, sy, sw, sh = 0, 0, ST_WIDTH, ST_HEIGHT
    #     try:
    #         viewport = self.config["viewport"]
    #         if viewport:
    #             sx, sy, sw, sh = viewport.rsplit("=", 1)[-1].strip().split(" ")
    #             sx, sy, sw, sh = int(sx), int(sy), int(sw), int(sh)
    #     except Exception:
    #         traceback.print_exc("Could not get viewport information")
    #     screen_w, screen_h = self.screen_size()
    #     print("viewport is", sx, sy, sw, sh)
    #     if self.use_stretching():
    #         target_w = screen_w
    #         target_h = screen_h
    #     else:
    #         scale = min(screen_w / sw, screen_h / sh)
    #         target_w = sw * scale
    #         target_h = sh * scale
    #     scale_x = target_w / sw
    #     scale_y = target_h / sh
    #     print("scale", scale_x, scale_y)
    #     orig_scale_x = min(screen_w / ST_WIDTH, screen_h / ST_HEIGHT)
    #     orig_scale_y = orig_scale_x
    #     print("org_scale = ", orig_scale_x, orig_scale_y)
    #     offset_x = -(sx + (sw / 2.0) - ST_WIDTH / 2.0) / (ST_WIDTH / 2.0)
    #     offset_y = -(sy + (sh / 2.0) - ST_HEIGHT / 2.0) / (
    #         ST_HEIGHT / 2.0
    #     )
    #     hz = scale_x / orig_scale_x
    #     vz = scale_y / orig_scale_y
    #     print("horizontal zoom:", hz / 100000000.0)
    #     print("vertical zoom:", vz / 100000000.0)
    #     self.env["FILTER_VERT_OFFSET"] = str(offset_y)
    #     self.env["FILTER_HORIZ_OFFSET"] = str(offset_x)
    #     self.env["FILTER_VERT_ZOOM"] = str(vz)
    #     self.env["FILTER_HORIZ_ZOOM"] = str(hz)


class HatariFsDriver(HatariDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc, fsemu=True)


class AtariHelper:
    def __init__(self, config):
        self.config = config

    def accuracy(self):
        try:
            accuracy = int(self.config.get(Option.ACCURACY, "1"))
        except ValueError:
            accuracy = 1
        return accuracy

    def model(self):
        model = self.config.get(Option.ST_MODEL)
        if not model:
            model = ST_MODEL_1040STFM
        return model

    def model_family(self):
        model = self.config.get(Option.ST_MODEL, "").upper()
        if model.endswith("ST"):
            return "ST"
        elif model.endswith("STFM"):
            return "ST"
        elif model.endswith("STE"):
            return "STE"
        return ""

    def tos_file(self):
        model = self.model().upper()
        if "STE" in model:
            return ST_TOS_1062_UK
        else:
            return ST_TOS_102_UK

    def memory(self):
        model = self.model().upper()
        if model.startswith("1040"):
            return 1024
        else:
            return 512


"""
[Log]
sLogFileName = stderr
sTraceFileName = stderr
nTextLogLevel = 3
nAlertDlgLogLevel = 1
bConfirmQuit = TRUE
bNatFeats = FALSE
bConsoleWindow = FALSE

[Debugger]
nNumberBase = 10
nSymbolLines = -1
nMemdumpLines = -1
nDisasmLines = -1
nExceptionDebugMask = 515
nDisasmOptions = 15
bDisasmUAE = FALSE
bSymbolsResident = FALSE
bMatchAllSymbols = FALSE

[Screen]
nMonitorType = 1
nFrameSkips = 5
bFullScreen = FALSE
bKeepResolution = TRUE
bResizable = TRUE
bAllowOverscan = TRUE
nSpec512Threshold = 1
nForceBpp = 0
bAspectCorrect = TRUE
bUseExtVdiResolutions = FALSE
nVdiWidth = 640
nVdiHeight = 480
nVdiColors = 2
bMouseWarp = TRUE
bShowStatusbar = TRUE
bShowDriveLed = TRUE
bCrop = FALSE
bForceMax = FALSE
nMaxWidth = 832
nMaxHeight = 588
bUseSdlRenderer = TRUE
nRenderScaleQuality = 0
bUseVsync = FALSE

[Joystick0]
nJoystickMode = 0
bEnableAutoFire = FALSE
bEnableJumpOnFire2 = FALSE
nJoyId = -1
kUp = Up
kDown = Down
kLeft = Left
kRight = Right
kFire = Right Ctrl

[Joystick1]
nJoystickMode = 0
bEnableAutoFire = FALSE
bEnableJumpOnFire2 = FALSE
nJoyId = -1
kUp = Up
kDown = Down
kLeft = Left
kRight = Right
kFire = Right Ctrl

[Joystick2]
nJoystickMode = 0
bEnableAutoFire = FALSE
bEnableJumpOnFire2 = FALSE
nJoyId = -1
kUp = Up
kDown = Down
kLeft = Left
kRight = Right
kFire = Right Ctrl

[Joystick3]
nJoystickMode = 0
bEnableAutoFire = FALSE
bEnableJumpOnFire2 = FALSE
nJoyId = -1
kUp = Up
kDown = Down
kLeft = Left
kRight = Right
kFire = Right Ctrl

[Joystick4]
nJoystickMode = 0
bEnableAutoFire = FALSE
bEnableJumpOnFire2 = FALSE
nJoyId = -1
kUp = Up
kDown = Down
kLeft = Left
kRight = Right
kFire = Right Ctrl

[Joystick5]
nJoystickMode = 0
bEnableAutoFire = FALSE
bEnableJumpOnFire2 = FALSE
nJoyId = -1
kUp = Up
kDown = Down
kLeft = Left
kRight = Right
kFire = Right Ctrl

[Keyboard]
bDisableKeyRepeat = FALSE
nKeymapType = 0
szMappingFileName =

[KeyShortcutsWithMod]
kOptions = O
kFullScreen = F
kBorders = B
kMouseMode = M
kColdReset = C
kWarmReset = R
kScreenShot = G
kBossKey = I
kCursorEmu = J
kFastForward = X
kRecAnim = A
kRecSound = Y
kSound = S
kPause =
kDebugger = Pause
kQuit = Q
kLoadMem = L
kSaveMem = K
kInsertDiskA = D
kSwitchJoy0 = F1
kSwitchJoy1 = F2
kSwitchPadA = F3
kSwitchPadB = F4

[KeyShortcutsWithoutMod]
kOptions = F12
kFullScreen = F11
kBorders =
kMouseMode =
kColdReset =
kWarmReset =
kScreenShot =
kBossKey =
kCursorEmu =
kFastForward =
kRecAnim =
kRecSound =
kSound =
kPause = Pause
kDebugger =
kQuit =
kLoadMem =
kSaveMem =
kInsertDiskA =
kSwitchJoy0 =
kSwitchJoy1 =
kSwitchPadA =
kSwitchPadB =

[Sound]
bEnableMicrophone = TRUE
bEnableSound = TRUE
bEnableSoundSync = FALSE
nPlaybackFreq = 44100
nSdlAudioBufferSize = 0
szYMCaptureFileName = /replace/hatari-fs/hatari.wav
YmVolumeMixing = 2

[Memory]
nMemorySize = 1024
nTTRamSize = 0
bAutoSave = FALSE
szMemoryCaptureFileName = /replace/.hatari/hatari.sav
szAutoSaveFileName = /replace/.hatari/auto.sav

[Floppy]
bAutoInsertDiskB = TRUE
FastFloppy = FALSE
EnableDriveA = TRUE
DriveA_NumberOfHeads = 2
EnableDriveB = TRUE
DriveB_NumberOfHeads = 2
nWriteProtection = 0
szDiskAZipPath =
szDiskAFileName =
szDiskBZipPath =
szDiskBFileName =
szDiskImageDirectory = /replace/hatari-fs/

[HardDisk]
nGemdosDrive = 0
bBootFromHardDisk = FALSE
bUseHardDiskDirectory = FALSE
szHardDiskDirectory = /replace/hatari-fs
nGemdosCase = 0
nWriteProtection = 0
bFilenameConversion = FALSE
bGemdosHostTime = FALSE

[ACSI]
bUseDevice0 = FALSE
sDeviceFile0 = /replace/hatari-fs
nBlockSize0 = 512
bUseDevice1 = FALSE
sDeviceFile1 = /replace/hatari-fs
nBlockSize1 = 512
bUseDevice2 = FALSE
sDeviceFile2 = /replace/hatari-fs
nBlockSize2 = 512
bUseDevice3 = FALSE
sDeviceFile3 = /replace/hatari-fs
nBlockSize3 = 512
bUseDevice4 = FALSE
sDeviceFile4 = /replace/hatari-fs
nBlockSize4 = 512
bUseDevice5 = FALSE
sDeviceFile5 = /replace/hatari-fs
nBlockSize5 = 512
bUseDevice6 = FALSE
sDeviceFile6 = /replace/hatari-fs
nBlockSize6 = 512
bUseDevice7 = FALSE
sDeviceFile7 = /replace/hatari-fs
nBlockSize7 = 512

[SCSI]
bUseDevice0 = FALSE
sDeviceFile0 = /replace/hatari-fs
nBlockSize0 = 512
bUseDevice1 = FALSE
sDeviceFile1 = /replace/hatari-fs
nBlockSize1 = 512
bUseDevice2 = FALSE
sDeviceFile2 = /replace/hatari-fs
nBlockSize2 = 512
bUseDevice3 = FALSE
sDeviceFile3 = /replace/hatari-fs
nBlockSize3 = 512
bUseDevice4 = FALSE
sDeviceFile4 = /replace/hatari-fs
nBlockSize4 = 512
bUseDevice5 = FALSE
sDeviceFile5 = /replace/hatari-fs
nBlockSize5 = 512
bUseDevice6 = FALSE
sDeviceFile6 = /replace/hatari-fs
nBlockSize6 = 512
bUseDevice7 = FALSE
sDeviceFile7 = /replace/hatari-fs
nBlockSize7 = 512

[IDE]
bUseDevice0 = FALSE
nByteSwap0 = 2
sDeviceFile0 = /replace/hatari-fs
nBlockSize0 = 512
nDeviceType0 = 0
bUseDevice1 = FALSE
nByteSwap1 = 2
sDeviceFile1 = /replace/hatari-fs
nBlockSize1 = 512
nDeviceType1 = 0

[ROM]
szTosImageFileName = /replace/hatari/tos.img
bPatchTos = TRUE
szCartridgeImageFileName =

[RS232]
bEnableRS232 = FALSE
szOutFileName = /dev/modem
szInFileName = /dev/modem
bEnableSccB = FALSE
sSccBOutFileName = /dev/modem

[Printer]
bEnablePrinting = FALSE
szPrintToFileName = /replace/.hatari/hatari.prn

[Midi]
bEnableMidi = FALSE
sMidiInFileName = /dev/snd/midiC1D0
sMidiOutFileName = /dev/snd/midiC1D0
sMidiInPortName = Off
sMidiOutPortName = Off

[System]
nCpuLevel = 0
nCpuFreq = 8
bCompatibleCpu = TRUE
nModelType = 0
bBlitter = FALSE
nDSPType = 0
bPatchTimerD = FALSE
bFastBoot = FALSE
bFastForward = FALSE
bAddressSpace24 = TRUE
bCycleExactCpu = TRUE
n_FPUType = 0
bSoftFloatFPU = FALSE
bMMU = FALSE
VideoTiming = 3

[Video]
AviRecordVcodec = 2
AviRecordFps = 0
AviRecordFile = /replace/hatari-fs/hatari.avi
"""
