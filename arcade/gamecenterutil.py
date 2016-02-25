import os
import shutil
import subprocess
import zipfile

from fsbc.path import unicode_path, str_path
from fsbc.system import windows, macosx
from fsbc.util import chained_exception


class GameCenterUtil(object):
    @classmethod
    def get_program_path(cls, name):

        def search(search_path):
            print("search", search_path)
            if not os.path.exists(search_path):
                return None
            if macosx:
                p = os.path.join(
                    search_path, name + ".app", "Contents", "MacOS", name)
                if os.path.exists(p):
                    return p
            for item in [name] + os.listdir(search_path):
                dp = os.path.join(search_path, item)
                if item == name:
                    p = dp
                    if windows:
                        p += u".exe"
                    if os.path.exists(p):
                        return p
                if os.path.isdir(dp):
                    p = os.path.join(dp, name)
                    if windows:
                        p += u".exe"
                    print("checking", p)
                    if os.path.exists(p):
                        return p

        # try to find emulator in its own project directory
        path = search(os.path.join("..//", name, "out"))
        if path and os.path.exists(path):
            return path

        # try to find packaged emulator in a platform workspace dir

        # if fs.windows:
        #     path = search("../fs-game-center-windows/lib")
        #     if path and os.path.exists(path):
        #         return path
        # if fs.macosx:
        #     path = search("../fs-game-center-macosx/lib")
        #     if not path or not os.path.exists(path):
        #         path = search(os.path.expanduser(
        # "~/git/fs-game-center-macosx/lib"))
        #     if path and os.path.exists(path):
        #         return os.path.join(os.getcwd(), path)

        # try to find the emulator in game center's lib dir

        # path = search(fs.get_lib_dir())
        # if path and os.path.exists(path):
        #     return path

        # if not on Windows, try to find a system-installed emulator
        if not windows:
            path = "/usr/bin/" + name
            if os.path.exists(path):
                print("checking", path)
                return path
            path = "/usr/local/bin/" + name
            if os.path.exists(path):
                print("checking", path)
                return path

        # or on Mac, search Applications dir for bundle
        if macosx:
            path = search("/Applications")
            if path and os.path.exists(path):
                return path

    @classmethod
    def run_program(cls, name, **kwargs):
        path = cls.get_program_path(name)
        if not path:
            raise Exception("Could not find program {0}".format(name))
        print("program", name, "at", path)
        path = os.path.join(os.getcwd(), path)
        path = os.path.normpath(path)
        print("program path (normalized):", path)
        dir_name = os.path.dirname(path)
        kwargs["env"]["LD_LIBRARY_PATH"] = str_path(dir_name)
        kwargs["args"].insert(0, path)
        print("run:", kwargs["args"])
        print("cwd:", kwargs.get("cwd", ""))
        return subprocess.Popen(**kwargs)
        # for entry_point in pkg_resources.iter_entry_points(
        #         "fengestad.program", name):
        #     # return first available, load should return a callable
        #     run_func = entry_point.load()
        #     break
        # else:
        #     raise Exception("Could not find program {0}".format(name))
        # print("run program ", name, "with args", kwargs["args"])
        # #print("run program ", name, "with args", kwargs)
        # return run_func(**kwargs)

    @classmethod
    def copy_folder_tree(cls, source_path, dest_path, overwrite=False):
        for item in os.listdir(source_path):
            if item[0] == ".":
                continue
            item_path = os.path.join(source_path, item)
            dest_item_path = os.path.join(dest_path, item)
            if os.path.isdir(item_path):
                if not os.path.exists(dest_item_path):
                    os.makedirs(dest_item_path)
                cls.copy_folder_tree(item_path, dest_item_path)
            else:
                if overwrite or not os.path.exists(dest_item_path):
                    shutil.copy(item_path, dest_item_path)

    @classmethod
    def unpack(cls, archive, destination):
        if archive.endswith(".7z"):
            cls.unpack_7zip(archive, destination)
        elif archive.endswith(".zip"):
            cls.unpack_zip(archive, destination)
        else:
            raise Exception("do not know how to unpack " + repr(archive))

    @classmethod
    def unpack_zip(cls, archive, destination):
        try:
            print("unpack", archive, "to", destination)
            zip = zipfile.ZipFile(archive, "r")

            def extract_members(z):
                for name in z.namelist():
                    if ".." in name:
                        continue
                    if not os.path.normpath(os.path.join(
                            destination, name)).startswith(destination):
                        raise Exception("Invalid path")
                    yield name

            zip.extractall(path=destination, members=extract_members(zip))
            zip.close()
        except Exception as e:
            print(e)
            raise chained_exception(Exception("Could not unpack game"), e)

    @classmethod
    def unpack_7zip(cls, archive, destination):
        try:
            print("unpack", archive, "to", destination)
            if not os.path.exists(destination):
                os.makedirs(destination)
            # plugin = pyapp.plug.get_plugin("no.fengestad.7zip")
            args = ["x", "-o" + destination, archive]
            process = cls.run_program("7za", args=args,
                                      stdout=subprocess.PIPE)
            # process = plugin.sevenz(args, stdout=subprocess.PIPE)
            line = process.stdout.readline()
            while line:
                print(line[:-1])
                # if fs.windows:
                line = unicode_path(line[:-len(os.linesep)])
                if line.startswith("Extracting  "):
                    parts = line.rsplit(os.sep, 1)
                    if len(parts) == 2:
                        # text = "Extracting " + parts[1]
                        # self.on_status(status="Extracting",
                        # sub_status=parts[1])
                        pass
                line = process.stdout.readline()
            return_code = process.wait()
            if return_code != 0:
                raise Exception("7z return non-zero")
        except Exception as e:
            print(e)
            raise chained_exception(Exception("Could not unpack game"), e)
