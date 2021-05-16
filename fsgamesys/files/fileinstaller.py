import hashlib
import os
from dataclasses import dataclass
from io import BytesIO
from typing import Callable, List, Optional, Tuple, cast

from fsgamesys.amiga.adffile import ADFFile
from fsgamesys.amiga.amigaconstants import AmigaConstants
from fsgamesys.amiga.rommanager import PatchableRom, ROMManager
from fsgamesys.amiga.workbenchdata import workbench_disks_with_setpatch_39_6
from fsgamesys.archive import Archive
from fsgamesys.files.installablefiles import InstallableFiles
from fsgamesys.files.types import ByteStream

CHUNK_SIZE = 65536


@dataclass
class InstalledFile:
    name: str
    sha1: str
    size: int

    def __getitem__(self, key: str):
        # FIXME: Can remove soon
        if key == "name":
            return self.name
        if key == "sha1":
            return self.sha1
        if key == "size":
            return self.size
        raise KeyError(key)


class FileInstaller:
    def __init__(self, files: InstallableFiles):
        self.files = files

    def install(
        self,
        installDir: str,
        getStreamForFileSha1: Callable[[str], Optional[ByteStream]],
    ) -> List[InstalledFile]:
        """Install files needed to run a game.

        The return value of this function is a list of installed files with
        checksum. This list can be used to implemented efficient change handler
        (no need to re-index files before launch).
        """
        installedFiles: List[InstalledFile] = []

        print("-" * 79)
        for relativePath, file in self.files.items():
            path = os.path.join(installDir, relativePath)
            print(path)
            print("   ", file)
        print("-" * 79)

        for relativePath, file in self.files.items():
            path = os.path.join(installDir, relativePath)
            print(path)
            print(file)
            # FIXME: Normalize and stuff?
            if relativePath.endswith(os.sep):
                if not os.path.exists(path):
                    os.makedirs(path)
                continue
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            assert file.sha1 is not None

            downloadable = False
            # optional = file_info.get("optional", False)
            if file.data is not None:
                # sha1 = file_info.get("sha1", None)
                stream = BytesIO(file.data)
            else:
                # sha1 = file_info["sha1"]

                # This isn't very nicely done, but it is a special case
                if file.sha1 == AmigaConstants.SETPATCH_39_6_SHA1:
                    stream = setpatch_stream(getStreamForFileSha1)
                    # stream = None
                    if stream is None:
                        if file.optional:
                            print(
                                "SetPatch was not found, but was marked as "
                                "optional"
                            )
                        else:
                            raise Exception(
                                "Could not find a suitable Workbench 3.0 disk "
                                "to extract SetPatch from. Please make sure "
                                "you have scanned a Workbench 3.0 disk."
                            )
                else:
                    stream = getStreamForFileSha1(file.sha1)
                # if stream is None:
                #     stream = downloadable_file_sha1_to_stream(sha1)

            if stream is None and canDownloadFileSha1(file.sha1):
                # Maybe downloading should be handled transparently in
                # file_sha1_to_stream instead...
                downloadable = True

            if stream is not None:
                writtenSha1, writtenSize = writeStream(
                    stream, path, sha1=file.sha1
                )
            elif downloadable:
                writtenSha1, writtenSize = Downloader.install_file_by_sha1(
                    file.sha1, os.path.basename(path), path
                )
            else:
                if file.optional:
                    print("Option file {sha1} not found")
                    continue
                raise Exception(
                    f"Could not install file {relativePath}: "
                    f"Did not find file with SHA-1 checksum {file.sha1}"
                )

            # with open(path, "wb") as f:
            #     while True:
            #         chunk_size = 65536
            #         data = stream.read(chunk_size)
            #         if not data:
            #             break
            #         f.write(data)
            installedFiles.append(
                InstalledFile(
                    name=relativePath, sha1=writtenSha1, size=writtenSize
                )
            )

        return installedFiles
        # raise NotImplementedError("aaa")


def writeStream(
    stream: ByteStream, path: str, sha1: Optional[str] = None
) -> Tuple[str, int]:
    dst = path
    dst_partial = os.path.join(
        os.path.dirname(dst), "~" + os.path.basename(dst) + ".tmp"
    )
    sha1_obj = hashlib.sha1()
    writtenSize = 0
    with open(dst_partial, "wb") as f:
        while True:
            data = stream.read(CHUNK_SIZE)
            if data.startswith(b"AMIROMTYPE1"):
                # FIXME: Better to implement this properly with archive
                # filters...
                stream = decrypt_amiromtype1_stream(stream, data)
                data = stream.read(CHUNK_SIZE)
            if not data:
                break
            f.write(data)
            sha1_obj.update(data)
            writtenSize += len(data)
    writtenSha1 = sha1_obj.hexdigest()

    # If SHA-1 did not match, see if the written file matches one of the ROMs
    # than ROMManager can transform into the correct one.
    if (
        sha1 is not None
        and writtenSha1 != sha1
        and (writtenSha1, sha1) in ROMManager.rom_transformations
    ):
        print(f"Patching ROM {writtenSha1} -> {sha1}")
        rom = PatchableRom(data=b"", sha1=writtenSha1)
        with open(dst_partial, "rb") as f:
            rom.data = f.read()
        ROMManager.patchRom(rom)
        with open(dst_partial, "wb") as f:
            f.write(rom.data)
        writtenSha1 = rom.sha1

    if sha1 is not None:
        if writtenSha1 != sha1:
            raise Exception(
                f"Written SHA-1 ({writtenSha1}) does not match expected "
                f"SHA-1 ({sha1})"
            )
    os.rename(dst_partial, dst)
    return writtenSha1, writtenSize


def decrypt_amiromtype1_stream(stream: ByteStream, data: bytes):
    # If we open a stream starting with AMIROMTYPE1, we assume that the file
    # has been opened via Archive and stored in the database with the
    # decrypted checksum.
    # FIXME: Better to implement this properly with archive filters...
    if hasattr(stream, "archive_path"):
        path = cast(str, stream.archive_path)
    else:
        raise Exception("Cannot extract rom.key from stream")
    archive = Archive(path)
    key_path = archive.join(archive.dirname(path), "rom.key")
    key_archive = Archive(key_path)
    try:
        f2 = key_archive.open(key_path)
    except Exception:
        raise Exception("Did not find rom.key to decrypt ROM with")
    print("Using key file", key_path)
    key_data: bytes = f2.read()
    f2.close()

    out_data: List[bytes] = []
    f = BytesIO(data[len("AMIROMTYPE1") :] + stream.read())
    sha1_obj = hashlib.sha1()

    while True:
        data = f.read(len(key_data))
        if not data:
            break
        dec: List[int] = []
        for i in range(len(data)):
            dec.append(data[i] ^ key_data[i])
        dec_data = bytes(dec)
        # if file is not None:
        #     file.write(dec_data)
        out_data.append(dec_data)
        # if sha1 is not None:
        sha1_obj.update(dec_data)
    # result["data"] =
    # result["sha1"] =
    result = PatchableRom(data=b"".join(out_data), sha1=sha1_obj.hexdigest())
    # print(result)
    ROMManager.patchRom(result)
    # if file is not None:
    #     file.write(result["data"])
    # return result
    return BytesIO(result.data)


def setpatch_stream(
    getStreamForFileSha1: Callable[[str], Optional[ByteStream]]
) -> Optional[ByteStream]:
    # Uncomment the following line to test how the system behaves when
    # SetPatch is not found.
    # workbench_disks_with_setpatch_39_6 = []

    for sha1 in workbench_disks_with_setpatch_39_6:
        # path = self.fsgs.file.find_by_sha1(checksum)
        stream = getStreamForFileSha1(sha1)
        if stream:
            # print("found WB DISK with SetPatch 39.6 at", stream.path)
            print("found WB DISK with SetPatch 39.6", stream)
            # try:
            #     input_stream = self.fsgs.file.open(path)
            # except Exception:
            #     traceback.print_exc()
            # else:
            adfData = stream.read()
            # archive = Archive(path)
            # if archive.exists(path):
            #     f = archive.open(path)
            #     wb_data = f.read()
            #     f.close()

            return extract_setpatch_39_6(adfData)

            # if self.extract_setpatch_39_6(wb_data, dest):
            #     print("SetPatch installed")
            #     self.setpatch_installed = True
            #     break
            # else:
            #     print("WARNING: extract_setpatch_39_6 returned False")
            # # else:
            # #     print("oops, path does not exist")
    else:
        print("WARNING: did not find SetPatch 39.6")


def extract_setpatch_39_6(adfData: bytes) -> ByteStream:
    try:
        setpatchData = ADFFile(adfData).open("C/SetPatch").read()
    except KeyError as e:
        raise e
    s = hashlib.sha1()
    s.update(setpatchData)
    # print(s.hexdigest())
    # noinspection SpellCheckingInspection
    sha1 = s.hexdigest()
    if sha1 != AmigaConstants.SETPATCH_39_6_SHA1:
        raise Exception(
            f"Extracted SetPatch SHA-1 ({sha1} is not the expected "
            f"{AmigaConstants.SETPATCH_39_6_SHA1}"
        )
    return BytesIO(setpatchData)
    # with open(dest, "wb") as f:
    #     f.write(setpatch_data)
    # return True


from fsgamesys.download import Downloader


def canDownloadFileSha1(sha1: str):
    # FIXME: This lis is not complete. This is currently the minimal set of
    # files needed to launch WHDLoad games.
    return sha1 in {
        "1ad1b55e7226bd5cd66def8370a69f19244da796",
        "1d1c557f4a0f5ea88aeb96d68b09f41990340f70",
        "209c109855f94c935439b60950d049527d2f2484",
        "51a37230cb45fc20fae422b8a60afd7cc8a63ed3",
        "973b42dcaf8d6cb111484b3c4d3b719b15f6792d",
        "d6b706bfbfe637bd98cd657114eea630b7d2dcc7",
        "ebf3a1f53be665bb39a636007fda3b3e640998ba",
    }


# def downloadable_file_sha1_to_stream(sha1):
# def install_whdload_file(sha1, dest_dir, rel_path):
#     abs_path = os.path.join(dest_dir, rel_path)
#     name = os.path.basename(rel_path)
#     # self.on_progress(gettext("Downloading {0}...".format(name)))
#     Downloader.install_file_by_sha1(sha1, name, abs_path)
