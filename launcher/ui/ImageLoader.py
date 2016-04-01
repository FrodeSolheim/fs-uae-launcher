import threading
import traceback
import weakref

import fsui as fsui
from .Constants import Constants
from ..launcher_signal import LauncherSignal

# FIXME: Remove dependency on arcade package (move stuff into fsgs instead)
from arcade.glui.imageloader import get_file_for_sha1_cached


class ImageLoader(object):
    def __init__(self):
        self.stop_flag = False
        self.requests = []
        self.requests_lock = threading.Lock()
        self.requests_condition = threading.Condition(self.requests_lock)
        threading.Thread(target=self.image_loader_thread,
                         name="ImageLoaderThread").start()
        LauncherSignal.add_listener("quit", self)

    def stop(self):
        print("[IMAGES] ImageLoader.stop")
        with self.requests_lock:
            self.stop_flag = True
            self.requests_condition.notify()

    def on_quit_signal(self):
        print("[IMAGES] ImageLoader.on_quit_signal")
        self.stop_flag = True

    def image_loader_thread(self):
        try:
            self._image_loader_thread()
        except Exception:
            traceback.print_exc()

    def load_image(self, path="", sha1="", size=None, on_load=None, **kwargs):
        request = ImageLoadRequest()
        request.path = path
        request.sha1 = sha1
        request.image = None
        request.size = size
        request.on_load = on_load
        request.args = kwargs
        with self.requests_lock:
            self.requests.append(weakref.ref(request))
            self.requests_condition.notify()
        return request

    def _image_loader_thread(self):
        while True:
            request = None
            with self.requests_lock:
                if self.stop_flag:
                    break
                while len(self.requests) > 0:
                    request = self.requests.pop(0)()
                    if request is not None:
                        break
            if request:
                self.fill_request(request)
                request.notify()
            else:
                with self.requests_lock:
                    if self.stop_flag:
                        break
                    self.requests_condition.wait()

    def fill_request(self, request):
        try:
            self._fill_request(request)
        except Exception:
            traceback.print_exc()

    def get_cache_path_for_sha1(self, request, sha1):
        cover = request.args.get("is_cover", False)
        if cover:
            size_arg = "?w={0}&h={1}&t=lbcover".format(
                Constants.COVER_SIZE[0], Constants.COVER_SIZE[1])
            cache_ext = "_{0}x{1}_lbcover.png".format(
                Constants.COVER_SIZE[0], Constants.COVER_SIZE[1])
        elif request.size:
            size_arg = "?s=1x"
            cache_ext = "_1x.png"
        else:
            size_arg = ""
            cache_ext = ""
        return get_file_for_sha1_cached(sha1, size_arg, cache_ext)

    def _fill_request(self, request):
        if request.path is None:
            return
        cover = request.args.get("is_cover", False)
        if request.path.startswith("sha1:"):
            path = self.get_cache_path_for_sha1(request, request.path[5:])
        else:
            path = request.path
        if not path:
            return
        print("[IMAGES] Loading", request.path)
        image = fsui.Image(path)
        print(image.size, request.size)
        if request.size is not None:
            dest_size = request.size
        else:
            dest_size = image.size
        if image.size == dest_size:
            request.image = image
            return
        if cover:
            try:
                ratio = image.size[0] / image.size[1]
            except Exception:
                ratio = 1.0
            if 0.85 < ratio < 1.20:
                min_length = min(request.size)
                dest_size = (min_length, min_length)
            double_size = False
        else:
            double_size = True

        if double_size and image.size[0] < 400:
            image.resize(
                (image.size[0] * 2, image.size[1] * 2), fsui.Image.NEAREST)
        image.resize(dest_size)
        request.image = image


class ImageLoadRequest(object):
    def __init__(self):
        self.on_load = self._dummy_on_load_function
        self.size = None
        self.args = {}

    def notify(self):
        def on_load_function():
            self.on_load(self)

        fsui.call_after(on_load_function)

    def _dummy_on_load_function(self, obj):
        pass
