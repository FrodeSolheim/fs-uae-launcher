import os
import threading
import time
from urllib.request import urlopen
from uuid import uuid4

from arcade.glui.texturemanager import TextureManager
from arcade.resources import logger
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.ogd.client import OGDClient
from fsui.qt import QImage

error_set = set()


def get_file_for_sha1(sha1):
    sha1, size_arg = sha1.split("?")
    if size_arg == "s=1x":
        cache_ext = "_1x.png"
    elif size_arg == "s=512&f=jpg":
        cache_ext = "_512.jpg"
    elif size_arg == "w=480&h=640&t=lbcover&f=jpg":
        cache_ext = "_480x640_lbcover.jpg"
    else:
        raise Exception("unrecognized size")

    cache_dir = FSGSDirectories.images_dir_for_sha1(sha1)
    cache_file = os.path.join(cache_dir, sha1 + cache_ext)
    if os.path.exists(cache_file):
        return cache_file

    server = OGDClient.get_server()
    cache_file_partial = cache_file + ".{0}.partial".format(str(uuid4())[:8])
    with open(cache_file_partial, "wb") as f:
        url = "http://{0}/image/{1}?{2}".format(server, sha1, size_arg)
        print(url)
        r = urlopen(url)
        data = r.read()
        f.write(data)
    os.rename(cache_file_partial, cache_file)
    return cache_file


def load_image(relative_path):
    path = ""
    try:
        if relative_path.startswith("sha1:"):
            sha1 = relative_path[5:]
            path = get_file_for_sha1(sha1)
        else:
            path = relative_path

        if path in error_set:
            return None, (0, 0)
        if not os.path.exists(path):
            return None, (0, 0)

        im = QImage(path)
        if im.format() != QImage.Format_ARGB32:
            im = im.convertToFormat(QImage.Format_ARGB32)
        bits = im.bits()
        try:
            pixels = bits.tobytes()
        except AttributeError:
            bits.setsize(im.byteCount())
            pixels = bytes(bits)
        return pixels, (im.width(), im.height())

    except Exception as e:
        print("error loading", repr(relative_path), repr(path), repr(e))
        error_set.add(path)
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
        threading.Thread(target=self.image_loader_thread,
                         name="GameCenterImageLoaderThread").start()
        pass

    def image_loader_thread(self):
        logger.debug("Image loader started")
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
        print("ImageLoader.stop()")
        self._stop_flag = True
