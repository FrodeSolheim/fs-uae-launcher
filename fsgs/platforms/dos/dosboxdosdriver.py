# FSGS - Common functionality for FS Game System.
# Copyright (C) 2013-2016  Frode Solheim <frode@openretro.org>
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
FSGS Game Driver for DOS.

FIXME: Save data

IMGMOUNT in autoexec can refer to paths beginning with $DRIVES, which will be
replaced by this driver when creating dosbox config.

"""
import hashlib
import json
import os
import shutil

from fsbc.path import str_path
from fsbc.system import System
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.drivers.gamedriver import GameDriver
from fsgs.option import Option
from fsgs.saves import SaveHandler


class DosBoxDosDriver(GameDriver):
    def __init__(self, fsgs):
        super().__init__(fsgs)
        if self.options[Option.DOS_EMULATOR] == "dosbox":
            self.emulator.name = "dosbox"
        elif self.options[Option.DOS_EMULATOR] == "dosbox-svn":
            self.emulator.name = "dosbox-svn"
        else:
            self.emulator.name = "dosbox-fs"

        self.save_handler = SaveHandler(self.fsgc, options=self.options)

        # Right now G-SYNC only works fine with 60Hz modes. There's stuttering
        # when DOSBox outputs 70 fps. Edit: The problem is that G-SYNC is
        # capped to monitors selected refresh rate.
        if self.screen_refresh_rate() < 70.0:
            print("[VIDEO] Screen refresh rate is < 70.0, disabling G-SYNC")
            self.set_allow_gsync(False)

        # self.ultrasnd_drive = None
        self.drives_dir = self.temp_dir("drives")
        self.drives = []

    def __del__(self):
        print("DosBoxDosDriver.__del__")

    def prepare(self):
        config_file = self.temp_file("dosbox.cfg").path
        self.prepare_media()
        with open(config_file, "w", encoding="UTF-8") as f:
            self.configure(f)
        self.emulator.args.extend(["-conf", config_file])

        # FIXME: Move to game driver?
        if self.options[Option.VIEWPORT]:
            self.emulator.env["FSGS_VIEWPORT"] = self.options[Option.VIEWPORT]

        # Must run after game hard drives have been unpacked
        for drive, drive_path in self.drives:
            assert drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            # print(drive)
            # print(drive_path)
            self.save_handler.register_changes(
                drive_path, os.path.join(self.save_handler.save_dir(), drive)
            )
        self.save_handler.prepare()

    def finish(self):
        self.save_handler.finish()

    def prepare_media(self):
        file_list = json.loads(self.options[Option.FILE_LIST])
        self.unpack_game_hard_drives(file_list)

        if self.options["cue_sheets"]:
            cue_sheets = json.loads(self.options["cue_sheets"])
            for cue_sheet in cue_sheets:
                with open(
                    os.path.join(self.drives_dir.path, cue_sheet["name"]), "wb"
                ) as f:
                    f.write(cue_sheet["data"].encode("UTF-8"))

    def unpack_game_hard_drives(self, file_list):
        drives_added = set()
        dir_path = self.drives_dir.path
        for file_entry in file_list:
            # if self.stop_flag:
            #     return

            name = file_entry["name"]
            name = name.upper()

            drives_added.add(name[0])

            # Extract relative path and convert each path component
            # to host file name (where needed).

            rel_path = name
            print("rel_path", rel_path)
            rel_parts = rel_path.split("/")
            # for i, part in enumerate(rel_parts):
            #     # part can be blank if rel_parts is a directory
            #     # (ending with /)
            #     if part:
            #         rel_parts[i] = amiga_filename_to_host_filename(part)
            rel_path = "/".join(rel_parts)

            dst_file = os.path.join(dir_path, rel_path)
            print(repr(dst_file))
            if name.endswith("/"):
                os.makedirs(str_path(dst_file))
                continue
            sha1 = file_entry["sha1"]
            src_file = self.fsgc.file.find_by_sha1(sha1)
            if not os.path.exists(os.path.dirname(dst_file)):
                os.makedirs(os.path.dirname(dst_file))
            stream = self.fsgc.file.open(src_file)
            # archive = Archive(src_file)
            # f = archive.open(src_file)
            data = stream.read()
            assert hashlib.sha1(data).hexdigest() == sha1

            with open(dst_file, "wb") as out_file:
                out_file.write(data)
            if dst_file.endswith(".CUE"):
                with open(dst_file, "r", encoding="ISO-8859-1") as f:
                    data = f.read()
                data = data.upper()
                with open(dst_file, "w", encoding="ISO-8859-1") as f:
                    f.write(data)

        for drive in sorted(drives_added):
            self.drives.append((drive, os.path.join(dir_path, drive)))

    def configure(self, f):
        f.write("# Automatically generated by FSGS\n")
        f.write("\n[sdl]\n")
        f.write("output=opengl\n")

        if self.use_fullscreen():
            f.write("fullscreen=true\n")
        else:
            f.write("fullscreen=false\n")
        f.write("fullresolution={0}x{1}\n".format(*self.screen_size()))

        f.write("\n[render]\n")
        f.write("frameskip=0\n")
        f.write("aspect=true\n")
        # if self.use_stretching():
        #     # This option does not stretch, it merely does not correct
        #     # aspect for non-square pixels resolutions, e.g. 320x200.
        #     # f.write("aspect=false\n")
        #     # This custom environment variable however, does cause stretching.
        #     self.env["FSGS_STRETCH"] = "1"
        # else:
        #     # f.write("aspect=true\n")
        #     self.env["FSGS_STRETCH"] = "0"

        if self.effect() == self.SCALE2X_EFFECT:
            scaler = "advmame2x"
        elif self.effect() == self.HQ2X_EFFECT:
            scaler = "hq2x"
        # elif self.effect() == self.CRT_EFFECT:
        #     scaler = "rgb2x"  # Looks ugly!
        else:
            scaler = "normal2x"

        if scaler:
            f.write("scaler={}\n".format(scaler))

        f.write("\n[cpu]\n")
        cpu_core = "auto"
        if self.options[Option.DOSBOX_CPU_CORE]:
            cpu_core = self.options[Option.DOSBOX_CPU_CORE]
            cpu_core = cpu_core.lower().strip()
        if System.windows and System.x86_64:
            # Dynamic core crashes on Windows x86-64
            print("[DOS] Forcing normal cpu core on Windows x86-64")
            if cpu_core in ["auto", "dynamic"]:
                cpu_core = "normal"
        f.write("core={0}\n".format(cpu_core))
        cpu_cycles = "auto"
        if self.options[Option.DOSBOX_CPU_CPUTYPE]:
            f.write(
                "cputype={0}\n".format(self.options[Option.DOSBOX_CPU_CPUTYPE])
            )
        if self.options[Option.DOSBOX_CPU_CYCLES]:
            cpu_cycles = self.options[Option.DOSBOX_CPU_CYCLES]
            if cpu_cycles.startswith("max "):
                pass
            elif cpu_cycles in ["auto", "max"]:
                pass
            else:
                cpu_cycles = "fixed " + cpu_cycles
        f.write("cycles={0}\n".format(cpu_cycles))

        f.write("\n[dosbox]\n")
        if self.options[Option.DOSBOX_MACHINE]:
            f.write("machine={}\n".format(self.options[Option.DOSBOX_MACHINE]))
        if self.options[Option.DOSBOX_MEMSIZE]:
            f.write("memsize={}\n".format(self.options[Option.DOSBOX_MEMSIZE]))

        self.configure_gus(f)
        self.configure_midi(f)
        self.configure_sblaster(f)

        f.write("\n[autoexec]\n")
        if self.options[Option.AUTO_LOAD] != "0":
            f.write("@ECHO OFF\n")
        # for drive, drive_path in self.drives:
        #     pass
        for name in os.listdir(self.drives_dir.path):
            if name in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                p = os.path.join(self.drives_dir.path, name, "CD", "IMAGE.CUE")
                if os.path.exists(p):
                    f.write('IMGMOUNT {0} "{1}" -t iso\n'.format(name, p))
                    continue
                p = os.path.join(self.drives_dir.path, name, "CD", "IMAGE.ISO")
                if os.path.exists(p):
                    f.write('IMGMOUNT {0} "{1}" -t iso\n'.format(name, p))
                    continue
                if name in "DEF":
                    f.write(
                        'MOUNT {0} "{1}" -t cdrom\n'.format(
                            name, os.path.join(self.drives_dir.path, name)
                        )
                    )
                    continue
                f.write(
                    'MOUNT {0} "{1}"\n'.format(
                        name, os.path.join(self.drives_dir.path, name)
                    )
                )
        f.write("C:\n")
        f.write("CLS\n")
        # for i in range(25):
        #     f.write("echo.\n")
        if self.options[Option.AUTO_LOAD] == "0":
            f.write(
                "@echo Auto-load is disabled. The following is the "
                "normal commands to start this game:\n"
            )
            f.write("@echo.\n")
        for command in self.options[Option.COMMAND].split(";"):
            command = command.strip()
            command = command.replace("$DRIVES", self.drives_dir.path)
            if not self.options[
                Option.AUTO_LOAD
            ] == "0" or command.lower().split(" ")[0].strip("@") in [
                "imgmount",
                "mount",
            ]:
                f.write("{0}\n".format(command))
            else:
                f.write("@echo {0}\n".format(command))
        if self.options[Option.AUTO_LOAD] == "0":
            f.write("@echo.\n")
        else:
            if not self.options[Option.AUTO_QUIT] == "0":
                f.write("exit\n")

        if System.windows:
            # We don't want to open the separate console window on windows.
            self.emulator.args.append("-noconsole")

    def configure_gus(self, f):
        f.write("\n[gus]\n")
        if self.options[Option.DOSBOX_GUS_GUS].lower() == "true":
            f.write("gus=true\n")
            f.write("ultradir=U:\\ULTRASND\n")
            ultrasnd_drive = os.path.join(self.drives_dir.path, "U")
            source_dir = os.path.join(
                FSGSDirectories.get_data_dir(), "ULTRASND"
            )
            dest_dir = os.path.join(ultrasnd_drive, "ULTRASND")
            if os.path.exists(source_dir):
                shutil.copytree(source_dir, dest_dir)
            else:
                # FIXME: ADD ULTRASND WARNING
                pass

    def configure_midi(self, f):
        f.write("\n[midi]\n")
        if True:
            f.write("mpu401=intelligent\n")
            # f.write("mpu401=uart\n")
        if System.windows:
            pass
        elif System.macos:
            pass
        else:
            f.write("mididevice=alsa\n")
            f.write("midiconfig=128:0\n")

    def configure_sblaster(self, f):
        f.write("\n[sblaster]\n")
        if self.options[Option.DOSBOX_SBLASTER_SBTYPE]:
            f.write(
                "sbtype={}\n".format(
                    self.options[Option.DOSBOX_SBLASTER_SBTYPE]
                )
            )
        if self.options[Option.DOSBOX_SBLASTER_SBBASE]:
            f.write(
                "sbbase={}\n".format(
                    self.options[Option.DOSBOX_SBLASTER_SBBASE]
                )
            )
        if self.options[Option.DOSBOX_SBLASTER_IRQ]:
            f.write(
                "irq={}\n".format(self.options[Option.DOSBOX_SBLASTER_IRQ])
            )
        if self.options[Option.DOSBOX_SBLASTER_OPLRATE]:
            f.write(
                "oplrate={}\n".format(
                    self.options[Option.DOSBOX_SBLASTER_OPLRATE]
                )
            )
