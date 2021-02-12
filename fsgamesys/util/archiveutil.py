import hashlib
import os
import zipfile
from urllib.parse import unquote
from uuid import NAMESPACE_URL, uuid5


class ArchiveUtil:
    TYPE_WHDLOAD = "TYPE_WHDLOAD"
    TYPE_DOS = "TYPE_DOS"

    def __init__(self, path):
        self.path = path
        self.extensions = set()
        self.ignore_extensions = set()
        self.ignore_comments = False

    def create_variant_uuid(self):
        return self.create_variant()["uuid"]

    def create_variant(self, type=None, file_callback=None):
        archive_name = os.path.basename(self.path)
        archive_name, archive_ext = os.path.splitext(archive_name)
        archive_ext = archive_ext.lower()
        if archive_ext == ".zip":
            class_ = zipfile.ZipFile
            # continue
        elif archive_ext == ".lha":
            from lhafile import Lhafile

            class_ = Lhafile
        else:
            print("skipping", archive_name)
            return

        # s = hashlib.sha1()
        # with open(path, "rb") as f:
        #     data = f.read()
        #     s.update(data)
        # archive_sha1 = s.hexdigest()
        variant = {}
        names = []
        icons = []
        lower_to_regular = {}
        archive = class_(self.path)

        for info in archive.infolist():
            name = info.filename
            _, ext = os.path.splitext(name)
            if ext and ext.lower() in self.ignore_extensions:
                continue
            if name.endswith(".uaem"):
                continue
            if "META-INF/" in name:
                continue

            # FIXME: For WHDLoad?
            # if name.startswith(archive_name + "/"):
            #     name = name[len(archive_name) + 1:]

            if info.comment and not self.ignore_comments:
                comment = info.comment
            else:
                comment = None
            try:
                metadata = archive.read(name + ".uaem").decode("UTF-8")
            except KeyError:
                pass
            else:
                # FIXME: Create a uaem metadata helper class
                # print(type(metadata))
                metadata = metadata.split("\n")[0].strip()
                # x_permissions = metadata[0:8]
                # x_date = metadata[9:31]
                comment = metadata[32:]
                comment = unquote(comment)

            lower_to_regular[name.lower()] = name

            if name.lower().endswith(".info"):
                if len(name.split("/")) == 2:
                    # We're at game folder level
                    info_data = archive.read(name)
                    info_data_lower = info_data.lower()
                    # if "whdload" in info_data_lower and \
                    #         "slave=" in info_data_lower:
                    if b"slave=" in info_data_lower:
                        # if ".slav" in info_data.lower():
                        # assert "slave" in info_data
                        icons.append(name)
                # All .info files are skipped, these are generally not identical
                # across installations, and are also not needed.
                continue

            # FIXME: use DOS charset instead...
            # name = name.decode("ISO-8859-1")

            if len(names) > 0:
                if names[-1][0].endswith("/"):
                    if name.startswith(names[-1][0]):
                        # Remove directory entry - we do not need that when
                        # the directory has content.
                        del names[len(names) - 1]
            names.append((name, name, comment))

        names.sort()
        file_sha1s = []
        file_list = []

        for dummy, name, comment in names:
            _, ext = os.path.splitext(name)
            if ext:
                self.extensions.add(ext.lower())
            # name_lower = name.lower()
            # content_hash.update(name.encode("ISO-8859-1"))

            if type == self.TYPE_WHDLOAD:
                list_name = "DH0/ " + name
            elif type == self.TYPE_DOS:
                list_name = "C/" + name.upper()
            else:
                list_name = name

            if list_name.endswith("/"):
                # Directory entry
                file_list.append({"name": list_name})
                continue

            # FIXME: encoding
            # data = archive.read(name.encode("ISO-8859-1"))
            data = archive.read(name)
            # content_hash.update(data)
            # data_hash.update(data)
            member_hash = hashlib.sha1()
            member_hash.update(data)
            file_sha1s.append(member_hash.hexdigest())
            file_list_item = {
                "name": list_name,
                "sha1": member_hash.hexdigest(),
                "size": len(data),
            }
            if comment:
                print(repr(comment))
                assert isinstance(comment, str)
                file_list_item["comment"] = comment
            file_list.append(file_list_item)
            if file_callback is not None:
                file_callback(sha1=member_hash.hexdigest(), data=data)

        url = "http://sha1.fengestad.no/" + "/".join(sorted(file_sha1s))
        variant["uuid"] = str(uuid5(NAMESPACE_URL, url))
        variant["file_list"] = file_list
        return variant
