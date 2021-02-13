import hashlib
import io
import os

from fsgamesys.amiga.rommanager import ROMManager
from fsgamesys.archive import Archive

CHUNK_SIZE = 65536


def install_files(files, install_dir, file_sha1_to_stream):
    """Install files needed to run a game.

    The return value of this function is a list of installed files with
    checksum. This list can be used to implemented efficient change handler
    (no need to re-index files before launch).
    """
    installed_files = []
    for relative_path, file_info in files.items():
        path = os.path.join(install_dir, relative_path)
        print(path)
        print(file_info)
        # FIXME: Normalize and stuff?
        if relative_path.endswith("/"):
            if not os.path.exists(path):
                os.makedirs(path)
            continue
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        if "data" in file_info:
            sha1 = file_info.get("sha1", None)
            stream = io.BytesIO(file_info["data"])
        else:
            sha1 = file_info["sha1"]
            stream = file_sha1_to_stream(sha1)
            if stream is None:
                raise Exception(
                    f"Could not install file {relative_path}: "
                    f"Did not find file with SHA-1 checksum {sha1}"
                )
        written_sha1, written_size = write_stream(stream, path, sha1=sha1)
        # with open(path, "wb") as f:
        #     while True:
        #         chunk_size = 65536
        #         data = stream.read(chunk_size)
        #         if not data:
        #             break
        #         f.write(data)
        installed_files.append(
            {"name": relative_path, "sha1": written_sha1, "size": written_size}
        )

    return installed_files
    # raise NotImplementedError("aaa")


def write_stream(stream, path, sha1=None):
    dst = path
    dst_partial = dst + ".partial"
    sha1_obj = hashlib.sha1()
    written_size = 0
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
            written_size += len(data)
    written_sha1 = sha1_obj.hexdigest()
    if sha1 is not None:
        if written_sha1 != sha1:
            raise Exception(
                f"Written SHA-1 ({written_sha1}) does not match expected SHA-1 ({sha1})"
            )
    os.rename(dst_partial, dst)
    return written_sha1, written_size


def decrypt_amiromtype1_stream(stream, data):
    # If we open a stream starting with AMIROMTYPE1, we assume that the file
    # has been opened via Archive and stored in the database with the
    # decrypted checksum.
    # FIXME: Better to implement this properly with archive filters...
    path = stream.archive_path
    archive = Archive(path)
    key_path = archive.join(archive.dirname(path), "rom.key")
    key_archive = Archive(key_path)
    try:
        f2 = key_archive.open(key_path)
    except Exception:
        raise Exception("Did not find rom.key to decrypt ROM with")
    print("Using key file", key_path)
    key_data = f2.read()
    f2.close()

    out_data = []
    result = {}
    f = io.BytesIO(data[len("AMIROMTYPE1") :] + stream.read())
    sha1_obj = hashlib.sha1()

    while True:
        data = f.read(len(key_data))
        if not data:
            break
        dec = []
        for i in range(len(data)):
            dec.append(data[i] ^ key_data[i])
        dec_data = bytes(dec)
        # if file is not None:
        #     file.write(dec_data)
        out_data.append(dec_data)
        # if sha1 is not None:
        sha1_obj.update(dec_data)
    result["data"] = b"".join(out_data)
    result["sha1"] = sha1_obj.hexdigest()
    # print(result)
    ROMManager.patch_rom(result)
    # if file is not None:
    #     file.write(result["data"])
    # return result
    return io.BytesIO(result["data"])
