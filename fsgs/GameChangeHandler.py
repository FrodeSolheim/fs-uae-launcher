import hashlib
import operator
import os
import shutil

# TODO: review the algorithm and add support for saving information about
# (empty) directories.


class GameChangeHandler(object):
    def __init__(self, path):
        self._preserve_changes_dir = path

    def init(self, state_dir, ignore=[]):
        print("\n" + "-" * 79 + "\n" + "CHANGEHANDLER INIT")
        print(self._preserve_changes_dir)
        path = self._preserve_changes_dir
        if os.path.exists(state_dir):
            print("Merging preserved changes in", state_dir, "to", path)
            if state_dir[-1] == "/" or state_dir[-1] == "\\":
                state_dir = state_dir[:-1]
            lstate_dir = len(state_dir)
            first_iteration = True
            for dirpath, dir_names, file_names in os.walk(state_dir):
                for file_name in file_names:
                    ignore_file = False
                    if first_iteration:
                        for ig in ignore:
                            assert ig[0] == "*"
                            dummy, ext = os.path.splitext(file_name)
                            if ext.lower() == ig[1:]:
                                print("ignoring", file_name)
                                ignore_file = True
                                break
                    if ignore_file:
                        continue
                    sourcepath = os.path.join(dirpath, file_name)
                    destpath = os.path.join(path, sourcepath[lstate_dir + 1 :])
                    if os.path.getsize(sourcepath) == 17:
                        with open(sourcepath, "rb") as f:
                            if f.read() == "FILE_IS_DELETED":
                                print(
                                    "- removing file",
                                    sourcepath[lstate_dir + 1 :],
                                )
                                if os.path.exists(destpath):
                                    os.remove(destpath)
                                else:
                                    print("  (already gone)")
                                continue
                    print("- updating file", sourcepath[lstate_dir + 1 :])
                    if not os.path.isdir(os.path.dirname(destpath)):
                        os.makedirs(os.path.dirname(destpath))
                    shutil.copyfile(sourcepath, destpath)
                first_iteration = False
        else:
            print("no game state")
        self._preserve_changes_files = self.create_file_version_list(path)
        print("done")
        return sorted(self._preserve_changes_files.values(), key=operator.itemgetter("name"))

    def update(self, state_dir):
        print("\n" + "-" * 79 + "\n" + "CHANGEHANDLER UPDATE")
        print("SRC", self._preserve_changes_dir)
        print("DST", state_dir)
        oldfiles = self._preserve_changes_files
        newfiles = self.create_file_version_list(self._preserve_changes_dir)
        print("checking files")
        for filename, newcs in newfiles.items():
            if newcs["name"].endswith("/"):
                # FIXME: Handle directories
                continue
            newcs = newcs["sha1"]
            try:
                oldcs = oldfiles[filename]["sha1"]
            except KeyError:
                print("New file:", filename)
                oldcs = None
            if newcs != oldcs:
                print("File changed:", filename)
                print("-", newcs, "vs", oldcs)
                sourcepath = os.path.join(self._preserve_changes_dir, filename)
                destpath = os.path.join(state_dir, filename)
                print("Writing file", destpath)
                if not os.path.exists(os.path.dirname(destpath)):
                    os.makedirs(os.path.dirname(destpath))
                shutil.copyfile(sourcepath, destpath)

        for filename in oldfiles:
            if filename.endswith("/"):
                # FIXME: Handle directories
                continue
            if not filename in newfiles:
                print("File removed", filename)
                destpath = os.path.join(state_dir, filename)
                if not os.path.exists(os.path.dirname(destpath)):
                    os.makedirs(os.path.dirname(destpath))
                with open(destpath, "wb") as f:
                    f.write("FILE_IS_DELETED")
        print("done")

    def create_file_version_list(self, path):
        print("create_file_version_list")
        if path[-1] == "/" or path[-1] == "\\":
            path = path[:-1]
        lpath = len(path)
        files = {}
        for dirpath, dirnames, filenames in os.walk(path):
            for dirname in dirnames:
                p = os.path.join(dirpath, dirname)
                files[p[lpath + 1:] + "/"] = {
                    "name": p[lpath + 1:] + "/",
                }
            for filename in filenames:
                p = os.path.join(dirpath, filename)
                sha1, size = self.sha1file(p)
                files[p[lpath + 1 :]] = {
                    "name": p[lpath + 1 :],
                    "sha1": sha1,
                    "size": size,
                }
        print(" - found %d files (checksummed)" % len(files))
        return files

    def sha1file(self, file):
        size = 0
        with open(file, "rb") as f:
            m = hashlib.sha1()
            while True:
                buffer = f.read(65536)
                if buffer == b"":
                    break
                m.update(buffer)
                size += len(buffer)
            return m.hexdigest(), size
