import os
import threading
import time
from functools import lru_cache
from typing import Optional
from uuid import uuid4
from zipfile import ZipFile

import requests

from arcade.glui.texturemanager import TextureManager
from arcade.resources import logger
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.network import openretro_url_prefix
from fsui.qt import QImage

error_set = set()


@lru_cache()
def get_cache_zip_for_sha1(sha1: str) -> Optional[ZipFile]:
    zip_path = os.path.join(FSGSDirectories.images_dir(), sha1[:2] + ".zip")
    try:
        return ZipFile(zip_path, "r")
    except Exception:
        return None


def get_file_for_sha1_cached(sha1: str, size_arg: str, cache_ext: str) -> str:
    cache_zip = get_cache_zip_for_sha1(sha1)
    if cache_zip is not None:
        try:
            return cache_zip.open("{}/{}{}".format(sha1[:2], sha1, cache_ext))
        except KeyError:
            pass
    cache_dir = FSGSDirectories.images_dir_for_sha1(sha1)
    cache_file = os.path.join(cache_dir, sha1 + cache_ext)
    if os.path.exists(cache_file):
        # An old bug made it possible for 0-byte files to exist, so
        # we check for that here...
        if os.path.getsize(cache_file) > 0:
            return cache_file

    url = "{}/image/{}{}".format(openretro_url_prefix(), sha1, size_arg)
    print("[IMAGES]", url)

    r = requests.get(url, stream=True)
    try:
        r.raise_for_status()
        cache_file_partial = "{}.{}.partial".format(
            cache_file, str(uuid4())[:8]
        )
        if not os.path.exists(os.path.dirname(cache_file_partial)):
            os.makedirs(os.path.dirname(cache_file_partial))
        with open(cache_file_partial, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
    finally:
        r.close()
    os.rename(cache_file_partial, cache_file)
    return cache_file


def get_file_for_sha1(sha1: str) -> str:
    sha1, size_arg = sha1.split("?")
    if size_arg == "s=1x":
        cache_ext = "_1x.png"
    elif size_arg == "s=512&f=jpg":
        cache_ext = "_512.jpg"
    elif size_arg == "w=480&h=640&t=cc&f=jpg":
        cache_ext = "_480x640_cc.jpg"
    else:
        raise Exception("unrecognized size")
    size_arg = "?" + size_arg
    return get_file_for_sha1_cached(sha1, size_arg, cache_ext)


def load_image(relative_path: str):
    path = ""
    try:
        if relative_path.startswith("sha1:"):
            sha1 = relative_path[5:]
            path = get_file_for_sha1(sha1)
        else:
            path = relative_path

        if relative_path in error_set:
            return None, (0, 0)

        if hasattr(path, "read"):
            im = QImage()
            im.loadFromData(path.read())
        else:
            if not os.path.exists(path):
                return None, (0, 0)
            im = QImage(path)
        if im.format() != QImage.Format.Format_ARGB32:
            im = im.convertToFormat(QImage.Format.Format_ARGB32)
        bits = im.bits()
        try:
            pixels = bits.tobytes()
        except AttributeError:
            bits.setsize(im.byteCount())
            pixels = bytes(bits)
        return pixels, (im.width(), im.height())

    except Exception as e:
        print(
            "[IMAGES] Error loading", repr(relative_path), repr(path), repr(e)
        )
        error_set.add(relative_path)
        return None, (0, 0)


class ImageLoader(object):
    _instance = None

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._stop_flag = False

    def start(self):
        self._stop_flag = False
        threading.Thread(
            target=self.imageLoaderThread, name="GameCenterImageLoaderThread"
        ).start()
        pass

    def imageLoaderThread(self):
        logger.debug("[IMAGES] Image loader started")
        tm = TextureManager().get()
        while not self._stop_flag:
            time.sleep(0.01)

            load_ip = None
            with tm.lock:
                for ip in tm.image_list:
                    if tm.image_dict[ip][0] is False:
                        load_ip = ip
                        break
            if load_ip:
                pixels, size = load_image(load_ip)
                tm.set_image(load_ip, pixels, size)

    def stop(self):
        print("[IMAGES] ImageLoader.stop()")
        self._stop_flag = True
