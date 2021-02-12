import functools
import os
import sys
import unicodedata

import fsboot
from fscore.system import System


class Paths(object):
    @staticmethod
    def str(path):
        return path.encode(sys.getfilesystemencoding())

    @staticmethod
    def encode(path):
        return path.encode(sys.getfilesystemencoding())

    @staticmethod
    def unicode(path):
        if isinstance(path, str):
            return path
        return path.decode(sys.getfilesystemencoding())

    @classmethod
    def join(cls, a, b):
        # if not a:
        #     return b
        # if a[-1] == "/" or a[-1] == "\\":
        #     return a + b
        # return a + "/" + b
        return os.path.join(a, b).replace("\\", "/")

    @classmethod
    def expand_path(cls, path, default_dir=None):
        if path and path[0] == "$":
            cmp_path = path.upper().replace("\\", "/")
            if cmp_path.startswith("$BASE/"):
                return cls.join(cls.get_base_dir(), path[6:])
            if cmp_path.startswith("$CONFIG/"):
                # FIXME: dependency loop, have FS-UAE Launcher register
                # this prefix with this class instead
                from launcher.launcher_settings import LauncherSettings

                config_path = LauncherSettings.get("config_path")
                if config_path:
                    return cls.join(os.path.dirname(config_path), path[8:])
            if cmp_path.startswith("$HOME/"):
                return cls.join(cls.get_home_dir(), path[6:])
            # FIXME: $base_dir is deprecated
            if cmp_path.startswith("$BASE_DIR/"):
                return cls.join(cls.get_base_dir(), path[10:])
        elif not os.path.isabs(path) and default_dir is not None:
            return os.path.join(default_dir, path)
        return path

    @classmethod
    def contract_path(cls, path, default_dir=None, force_real_case=True):
        if path.rfind(":") > 1:
            # Checking against > index 1 to allow for Windows absolute paths
            # with drive letter and colon. If colon is later, we assume this
            # is an URI, and not a path, so we do not do anything with it
            return path
        if force_real_case:
            print("before", path)
            path = cls.get_real_case(path)
            print("after", path)
        # dir, file = os.path.split(path)
        # norm_dir = dir + "/"
        if default_dir is not None:
            default_dir += "/"
            if path.startswith(default_dir):
                return path[len(default_dir) :]
        base_dir = cls.get_base_dir(slash=True)
        if path.startswith(base_dir):
            path = path.replace(base_dir, "$BASE/")
        home_dir = cls.get_home_dir(slash=True)
        if path.startswith(home_dir):
            path = path.replace(home_dir, "$HOME/")
        return path

    @classmethod
    def get_base_dir(cls, slash=False):
        path = fsboot.base_dir()
        path = cls.get_real_case(path)
        if slash:
            path += "/"
        return path

    @classmethod
    @functools.lru_cache()
    def get_home_dir(cls, slash=False):
        path = fsboot.home_dir()
        path = cls.get_real_case(path)
        if slash:
            path += "/"
        return path

    @classmethod
    def get_real_case(cls, path):
        """Check the case for the (case insensitive) path. Used to make the
        database portable across sensitive/insensitive file systems."""

        # get_real_case will fail on Linux if you have "conflicting" paths
        # (differing only by case), unless we check that the specified path
        # is already correct. The reason for not simply returning the path
        # as-is on Linux, is that this function can find files in directories
        # (portable version) when the directory is specified with wrong case.
        if not System.windows and not System.macos:
            if os.path.exists(path):
                return path

        parts = []
        drive, p = os.path.splitdrive(path)
        removed_separator = ""
        if path.startswith("/"):
            drive = "/"
        elif drive:
            # on Windows, add / to make drive a valid path
            drive += "/"
        if len(p) > 1 and (p.endswith("/") or (System.windows and p.endswith("\\"))):
            removed_separator = p[-1]
            p = p[:-1]

        last = ""
        while p != last:
            name = os.path.basename(p)
            if not name:
                break
            parts.append(name)
            last = p
            p = os.path.dirname(p)
        parts.reverse()
        result = [drive]
        result.extend(parts)

        combined = drive
        combined = combined.upper()
        k = 1
        for part in parts:
            part_compare = part
            part_compare = part_compare.lower()
            if System.macos:
                part_compare = unicodedata.normalize("NFC", part_compare)
            # print("part is", part)
            if os.path.isdir(combined):
                # print("checking case of", combined + "/" + part)
                for name in os.listdir(combined):
                    # if part == "Førde":
                    #     print(os.listdir(combined))
                    name_compare = name
                    name_compare = name_compare.lower()
                    if System.macos:
                        name_compare = unicodedata.normalize(
                            "NFC", name_compare
                        )
                    if name_compare == part_compare:
                        # print("found case =", name)
                        if not combined.endswith("/"):
                            combined += "/"
                        combined += name
                        result[k] = name
                        break
                else:
                    raise Exception("could not find case for path " + path)
            k += 1

        # FIXME: could be an idea to always normalize to NFC on OS X too,
        # to make the database even more portable

        # normalizing slashes to forward slash to make the database more
        # portable
        result_path = os.path.join(*result).replace("\\", "/")
        result_path += removed_separator
        return result_path
