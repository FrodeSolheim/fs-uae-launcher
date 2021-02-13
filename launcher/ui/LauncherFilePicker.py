import os

import fsui
from fsgamesys.FSGSDirectories import FSGSDirectories

from ..launcher_settings import LauncherSettings


class LauncherFilePicker(object):
    def __init__(
        self,
        parent,
        title,
        media_type,
        last_path="",
        multiple=False,
        dir_mode=False,
    ):
        self.multiple = multiple
        self.dir_mode = dir_mode
        self.parent = parent
        self.title = title
        self.result = None
        self.dir_mode = dir_mode
        self.settings_key = "last_{0}_dir".format(media_type)
        self.directory = ""
        if last_path and last_path not in ["internal"]:
            print("last_path", repr(last_path))
            # if os.path.isdir(last_path):
            #     last_path_dir = last_path
            # else:
            last_path_dir = os.path.dirname(last_path)
            print("last_path_dir", last_path_dir)
            if last_path_dir:
                if os.path.exists(last_path_dir):
                    self.directory = last_path_dir
            else:
                # file was relative to default directory
                self.directory = self.get_default_directory(media_type)
        if not self.directory:
            value = LauncherSettings.get(self.settings_key)
            print(self.settings_key, value)
            if value and os.path.exists(value):
                self.directory = value
        if not self.directory:
            self.directory = self.get_default_directory(media_type)
        # fsui.FileDialog.__init__(
        #     self, parent, title, directory, dir_mode=dir_mode,
        #     multiple=multiple)

    @staticmethod
    def get_default_directory(media_type):
        if media_type == "floppy":
            return FSGSDirectories.get_floppies_dir()
        elif media_type == "cd":
            return FSGSDirectories.get_cdroms_dir()
        elif media_type == "hd":
            return FSGSDirectories.get_hard_drives_dir()
        elif media_type == "rom":
            return FSGSDirectories.get_kickstarts_dir()
        # FIXME: Return new Media directory instead
        return FSGSDirectories.get_base_dir()
        # raise Exception("unknown file dialog type")

    def show_modal(self):
        path = None
        if self.dir_mode:
            self.result = fsui.pick_directory(
                parent=self.parent,
                message=self.title,
                directory=self.directory,
            )
            if self.result:
                path = self.result
        elif self.multiple:
            self.result = fsui.pick_files(
                parent=self.parent,
                message=self.title,
                directory=self.directory,
            )
            if self.result:
                path = self.result[0]
        else:
            self.result = fsui.pick_file(
                parent=self.parent,
                message=self.title,
                directory=self.directory,
            )
            if self.result:
                path = self.result
        if path:
            last_path_dir = os.path.dirname(path)
            LauncherSettings.set(self.settings_key, last_path_dir)
        return bool(self.result)

    def destroy(self):
        pass

    def get_path(self):
        return self.result

    def get_paths(self):
        return self.result
