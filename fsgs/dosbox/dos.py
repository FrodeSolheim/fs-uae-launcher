# FSGS - Common functionality for Fengestad Game System.
# Copyright (C) 2013  Frode Solheim <frode-code@fengestad.no>
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
Game Runner for DOS.

"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import io
import json
import shutil
import hashlib
from fsbc.path import str_path
from fsbc.system import windows
from fsgs.runner import GameRunner


#noinspection PyAttributeOutsideInit
class DOSRunner(GameRunner):

    def prepare(self):
        self.temp_dir = self.create_temp_dir("dosbox")
        self.drives_dir = self.create_temp_dir("dosbox-drives")
        config_file = os.path.join(self.temp_dir.path, "dosbox.cfg")
        self.drives = []
        self.prepare_media()
        with io.open(config_file, "w", encoding="UTF-8") as f:
            self.configure(f)
        self.add_arg("-conf", config_file)

    def prepare_media(self):
        file_list = json.loads(self.config["file_list"])
        self.unpack_game_hard_drives(file_list)

    def unpack_game_hard_drives(self, file_list):
        # dir_path = os.path.join(self.temp_dir, dir_name)
        drives_added = set()
        dir_path = self.drives_dir.path
        for file_entry in file_list:
            #if self.stop_flag:
            #    return
            name = file_entry["name"].upper()
            drives_added.add(name[0])

            # extract relative path and convert each path component
            # to host file name (where needed).

            rel_path = name
            print("rel_path", rel_path)
            rel_parts = rel_path.split("/")
            #for i, part in enumerate(rel_parts):
            #    # part can be blank if rel_parts is a directory
            #    # (ending with /)
            #    if part:
            #        rel_parts[i] = amiga_filename_to_host_filename(part)
            rel_path = "/".join(rel_parts)

            dst_file = os.path.join(dir_path, rel_path)
            print(repr(dst_file))
            if name.endswith("/"):
                os.makedirs(str_path(dst_file))
                continue
            sha1 = file_entry["sha1"]
            src_file = self.fsgs.file.find_by_sha1(sha1)
            if not os.path.exists(os.path.dirname(dst_file)):
                os.makedirs(os.path.dirname(dst_file))
            stream = self.fsgs.file.open(src_file)
            # archive = Archive(src_file)
            # f = archive.open(src_file)
            data = stream.read()
            assert hashlib.sha1(data).hexdigest() == sha1

            with open(dst_file, "wb") as out_file:
                out_file.write(data)

        for drive in sorted(drives_added):
            self.drives.append((drive, os.path.join(dir_path, drive)))

    def configure(self, f):
        f.write("# automatically generated\n")
        f.write("\n[sdl]\n")
        f.write("output=opengl\n")

        if self.use_fullscreen():
            f.write("fullscreen=true\n")
        else:
            f.write("fullscreen=false\n")
        f.write("fullresolution={0}x{1}\n".format(*self.screen_size()))

        f.write("\n[render]\n")
        f.write("frameskip=0\n")
        if self.use_stretching():
            # FIXME: this option does not stretch, merely does not correct
            # aspect for non-square pixels resolutions, e.g. 320x200
            f.write("aspect=false\n")
            self.set_env("FSGS_STRETCH", "1")
        else:
            f.write("aspect=true\n")

        f.write("\n[cpu]\n")
        cpu_core = "auto"
        f.write("core={0}\n".format(cpu_core))
        cpu_cycles = "auto"
        f.write("cycles={0}\n".format(cpu_cycles))

        f.write("\n[autoexec]\n")
        f.write("@echo off\n")
        #for drive, drive_path in self.drives:
        #    pass
        for name in os.listdir(self.drives_dir.path):
            if name in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                if name in "DEF":
                    f.write('MOUNT {0} "{1}" -t cdrom\n'.format(name,
                            os.path.join(self.drives_dir.path, name)))
                else:
                    f.write('MOUNT {0} "{1}"\n'.format(name,
                            os.path.join(self.drives_dir.path, name)))
        f.write("C:\n")
        f.write("CLS\n")
        #for i in range(25):
        #    f.write("echo.\n")
        for command in self.config["hd_startup"].split(";"):
            command = command.strip()
            f.write("{0}\n".format(command))
        f.write("exit\n")

        if windows:
            # we don't want to open the separate console window on windows
            self.add_arg("-noconsole")

    def run(self):
        # return self.start_emulator("fs-dosbox/dosbox")
        return self.start_emulator_from_plugin_resource("dosbox")

    def finish(self):
        pass
