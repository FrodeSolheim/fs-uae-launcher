import hashlib
import os
import shutil
from typing import Optional, Tuple, overload
from uuid import NAMESPACE_URL, uuid4, uuid5

import requests
from typing_extensions import Literal

from fsbc.application import app
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.network import fs_uae_url_from_sha1_and_name
from fsgamesys.options.option import Option
from fsgamesys.plugins.pluginmanager import PluginManager


class OfflineModeException(Exception):
    pass


def offline_mode() -> bool:
    return app.settings[Option.OFFLINE_MODE] == "1"


def raise_exception_in_offline_mode() -> None:
    if offline_mode():
        raise OfflineModeException("Offline mode is enabled")


class Downloader(object):
    @classmethod
    def check_terms_accepted(
        cls, download_file: str, download_terms: str
    ) -> bool:
        print(
            "[DOWNLOADER] check_terms_accepted", download_file, download_terms
        )
        uuid = str(uuid5(NAMESPACE_URL, download_file + download_terms))
        path = cls.get_cache_path(uuid)
        print("[DOWNLOADER] check_terms_accepted", path)
        return os.path.exists(path)

    @classmethod
    def set_terms_accepted(
        cls, download_file: str, download_terms: str
    ) -> None:
        print(
            "[DOWNLOADER] set_terms_accepted",
            repr(download_file),
            repr(download_terms),
        )
        uuid = str(uuid5(NAMESPACE_URL, download_file + download_terms))
        path = cls.get_cache_path(uuid)
        print("[DOWNLOADER] set_terms_accepted", path)
        with open(path, "wb") as _:
            pass

    @classmethod
    def cache_data(cls, data: bytes) -> None:
        sha1 = hashlib.sha1(data).hexdigest()
        cache_path = cls.get_cache_path(sha1)
        if os.path.exists(cache_path):
            return
        cache_path_temp = cache_path + ".partial." + str(uuid4())
        with open(cache_path_temp, "wb") as f:
            f.write(data)
        try:
            os.rename(cache_path_temp, cache_path)
        except Exception as e:
            if os.path.exists(cache_path):
                # file has appeared in the meantime (by another thread?)
                return
            raise e

    @overload
    @classmethod
    def cache_file_from_url(
        cls,
        url: str,
        download: Literal[False],
        auth: Optional[Tuple[str, str]] = None,
    ) -> Optional[str]:
        ...

    @overload
    @classmethod
    def cache_file_from_url(
        cls,
        url: str,
        download: Optional[Literal[True]] = True,
        auth: Optional[Tuple[str, str]] = None,
    ) -> str:
        ...

    @classmethod
    def cache_file_from_url(
        cls,
        url: str,
        download: Optional[bool] = True,
        auth: Optional[Tuple[str, str]] = None,
    ) -> Optional[str]:
        print("[DOWNLOADER] cache_file_from_url", url)
        cache_path = cls.get_url_cache_path(url)
        if os.path.exists(cache_path):
            print("[DOWNLOADER] (in cache)")
            # so we later can delete least accessed files in cache...
            os.utime(cache_path, None)
            return cache_path
        if not download:
            return None
        raise_exception_in_offline_mode()
        r = requests.get(url, auth=auth, stream=True)
        try:
            r.raise_for_status()
            cache_path_temp = cache_path + ".partial." + str(uuid4())
            with open(cache_path_temp, "wb") as ofs:
                for chunk in r.iter_content(chunk_size=65536):
                    ofs.write(chunk)
        finally:
            r.close()
        os.rename(cache_path_temp, cache_path)
        return cache_path

    @classmethod
    def install_file_from_url(cls, url: str, path: str) -> None:
        print("[DOWNLOADER] install_file_from_url", url)
        print(repr(path))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        cache_path = cls.cache_file_from_url(url)
        temp_path = path + ".partial"
        shutil.copy(cache_path, temp_path)
        os.rename(temp_path, path)

    @classmethod
    def install_file_by_sha1(
        cls, sha1: str, name: str, path: str
    ) -> Tuple[str, int]:
        print("[DOWNLOADER] install_file_by_sha1", sha1)
        # FIXME: Also find files from file database / plugins

        print(repr(path))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        written_size = 0
        src = PluginManager.instance().find_file_by_sha1(sha1)
        if src:
            dst = path
            # FIXME: ~name.tmp ?
            dst_partial = dst + ".partial"
            sha1_obj = hashlib.sha1()
            with open(src, "rb") as fin:
                with open(dst_partial, "wb") as fout:
                    while True:
                        data = fin.read(65536)
                        if not data:
                            break
                        fout.write(data)
                        sha1_obj.update(data)
                        written_size += len(data)
            if sha1_obj.hexdigest() != sha1:
                raise Exception("File from plugin does not match SHA-1")
            os.rename(dst_partial, dst)
            return sha1_obj.hexdigest(), written_size

        cache_path = cls.get_cache_path(sha1)
        if os.path.exists(cache_path):
            print("[CACHE]", cache_path)
            # FIXME: Atomic copy utility function?
            # FIXME: Actually, maybe better instead of open stream and copy
            # manually, and verify SHA-1
            shutil.copy(cache_path, path)
            # so we later can delete least accessed files in cache...
            os.utime(cache_path, None)
            written_size = os.path.getsize(path)
            # FIXME: Return actual verified SHA-1 instead
            return sha1, written_size
        url = cls.sha1_to_url(sha1, name)
        print("[DOWNLOADER]", url)
        raise_exception_in_offline_mode()
        r = requests.get(url, stream=True)
        try:
            r.raise_for_status()
            temp_path = path + ".partial." + str(uuid4())
            h = hashlib.sha1()
            with open(temp_path, "wb") as output:
                for chunk in r.iter_content(chunk_size=65536):
                    h.update(chunk)
                    output.write(chunk)
                    written_size += len(chunk)
        finally:
            r.close()
        if h.hexdigest() != sha1:
            print("error: downloaded sha1 is", h.hexdigest(), "- wanted", sha1)
            raise Exception("sha1 of downloaded file does not match")

        # Atomic "copy" to cache location
        temp_cache_path = cache_path + ".partial." + str(uuid4())
        shutil.copy(temp_path, temp_cache_path)
        os.rename(temp_cache_path, cache_path)

        # Move downloaded file into file position (atomic)
        os.rename(temp_path, path)

        return h.hexdigest(), written_size

    @classmethod
    def sha1_to_url(cls, sha1: str, name: str) -> str:
        return fs_uae_url_from_sha1_and_name(sha1, name)

    @classmethod
    def get_cache_path(cls, sha1_or_uuid: str) -> str:
        path = os.path.join(
            FSGSDirectories.get_cache_dir(), "Downloads", sha1_or_uuid[:3]
        )
        if not os.path.exists(path):
            os.makedirs(path)
        return os.path.join(path, sha1_or_uuid)

    @classmethod
    def get_url_cache_path(cls, url: str) -> str:
        return cls.get_cache_path(str(uuid5(NAMESPACE_URL, url)))
