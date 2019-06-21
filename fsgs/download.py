import hashlib
import os
import shutil
from uuid import NAMESPACE_URL, uuid4, uuid5

import requests

from fsbc.application import app
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.network import fs_uae_url_from_sha1_and_name
from fsgs.option import Option
from fsgs.plugins.pluginmanager import PluginManager


class OfflineModeException(Exception):
    pass


def offline_mode():
    return app.settings[Option.OFFLINE_MODE] == "1"


def raise_exception_in_offline_mode():
    if offline_mode():
        raise OfflineModeException("Offline mode is enabled")


class Downloader(object):
    @classmethod
    def check_terms_accepted(cls, download_file, download_terms):
        print(
            "[DOWNLOADER] check_terms_accepted", download_file, download_terms
        )
        uuid = str(uuid5(NAMESPACE_URL, download_file + download_terms))
        path = cls.get_cache_path(uuid)
        print("[DOWNLOADER] check_terms_accepted", path)
        return os.path.exists(path)

    @classmethod
    def set_terms_accepted(cls, download_file, download_terms):
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
    def cache_data(cls, data):
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

    @classmethod
    def cache_file_from_url(cls, url, download=True, auth=None):
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
    def install_file_from_url(cls, url, path):
        print("[DOWNLOADER] install_file_from_url", url)
        print(repr(path))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        cache_path = cls.cache_file_from_url(url)
        temp_path = path + ".partial"
        shutil.copy(cache_path, temp_path)
        os.rename(temp_path, path)

    @classmethod
    def install_file_by_sha1(cls, sha1, name, path):
        print("[DOWNLOADER] install_file_by_sha1", sha1)
        # FIXME: Also find files from file database / plugins

        print(repr(path))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        src = PluginManager.instance().find_file_by_sha1(sha1)
        if src:
            dst = path
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
            if sha1_obj.hexdigest() != sha1:
                raise Exception("File from plugin does not match SHA-1")
            os.rename(dst_partial, dst)
            return

        cache_path = cls.get_cache_path(sha1)
        if os.path.exists(cache_path):
            print("[CACHE]", cache_path)
            # FIXME: Atomic copy utility function?
            shutil.copy(cache_path, path)
            # so we later can delete least accessed files in cache...
            os.utime(cache_path, None)
            return
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

    @classmethod
    def sha1_to_url(cls, sha1, name):
        return fs_uae_url_from_sha1_and_name(sha1, name)

    @classmethod
    def get_cache_path(cls, sha1_or_uuid):
        path = os.path.join(
            FSGSDirectories.get_cache_dir(), "Downloads", sha1_or_uuid[:3]
        )
        if not os.path.exists(path):
            os.makedirs(path)
        return os.path.join(path, sha1_or_uuid)

    @classmethod
    def get_url_cache_path(cls, url):
        return cls.get_cache_path(str(uuid5(NAMESPACE_URL, url)))
