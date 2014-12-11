from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
from uuid import uuid4, uuid5, NAMESPACE_URL
import shutil
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import hashlib

# FIXME: temporary package dependency cycle, must be fixed
from fsgs.FSGSDirectories import FSGSDirectories


class Downloader(object):

    @classmethod
    def check_terms_accepted(cls, download_file, download_terms):
        print("check_terms_accepted", download_file, download_terms)
        uuid = str(uuid5(
            NAMESPACE_URL, (download_file + download_terms).encode("UTF-8")))
        path = cls.get_cache_path(uuid)
        print("check_terms_accepted", path)
        return os.path.exists(path)

    @classmethod
    def set_terms_accepted(cls, download_file, download_terms):
        print("set_terms_accepted", repr(download_file), repr(download_terms))
        uuid = str(uuid5(
            NAMESPACE_URL, (download_file + download_terms).encode("UTF-8")))
        path = cls.get_cache_path(uuid)
        print("set_terms_accepted", path)
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
    def cache_file_from_url(cls, url, download=True, opener=None):
        print("DownloadService.cache_file_from_url", url)

        cache_path = cls.get_url_cache_path(url)
        if os.path.exists(cache_path):
            print("(in cache)")
            # so we later can delete least accessed files in cache...
            os.utime(cache_path, None)
            return cache_path
        if not download:
            return None
        if opener:
            ifs = opener.open(url)
        else:
            ifs = urlopen(url)
        cache_path_temp = cache_path + ".partial." + str(uuid4())
        with open(cache_path_temp, "wb") as ofs:
            while True:
                data = ifs.read(65536)
                if not data:
                    break
                ofs.write(data)
        os.rename(cache_path_temp, cache_path)
        return cache_path

    @classmethod
    def install_file_from_url(cls, url, path):
        print("DownloadService.install_file_from_url", url)
        print(repr(path))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        cache_path = cls.cache_file_from_url(url)
        temp_path = path + ".partial"
        shutil.copy(cache_path, temp_path)
        os.rename(temp_path, path)

    @classmethod
    def install_file_by_sha1(cls, sha1, name, path):
        print("DownloadService.install_file_by_sha1", sha1)
        print(repr(path))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        cache_path = cls.get_cache_path(sha1)
        if os.path.exists(cache_path):
            print("(in cache)")
            shutil.copy(cache_path, path)
            # so we later can delete least accessed files in cache...
            os.utime(cache_path, None)
            return
        url = cls.sha1_to_url(sha1, name)
        ifile = urlopen(url)
        temp_path = path + ".partial." + str(uuid4())
        h = hashlib.sha1()
        with open(temp_path, "wb") as ofile:
            while True:
                data = ifile.read(65536)
                if not data:
                    break
                h.update(data)
                ofile.write(data)
        if h.hexdigest() != sha1:
            print("error: downloaded sha1 is", sha1)
            raise Exception("sha1 of downloaded file does not match")
        temp_cache_path = cache_path + ".partial." + str(uuid4())
        shutil.copy(temp_path, temp_cache_path)
        os.rename(temp_cache_path, cache_path)
        os.rename(temp_path, path)

    @classmethod
    def sha1_to_url(cls, sha1, name):
        url = "http://fs-uae.net/s/sha1/{0}/{1}".format(sha1, name)
        print(url)
        return url

    @classmethod
    def get_cache_path(cls, sha1_or_uuid):
        path = os.path.join(
            FSGSDirectories.get_cache_dir(), "Downloads", sha1_or_uuid[:3])
        if not os.path.exists(path):
            os.makedirs(path)
        return os.path.join(path, sha1_or_uuid)

    @classmethod
    def get_url_cache_path(cls, url):
        if isinstance(url, str):
            # Python 3
            return cls.get_cache_path(str(uuid5(NAMESPACE_URL, url)))
        else:
            # Python 2 / unicode
            return cls.get_cache_path(
                str(uuid5(NAMESPACE_URL, url.encode("UTF-8"))))
