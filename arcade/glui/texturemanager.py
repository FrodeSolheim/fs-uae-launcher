import threading

from OpenGL import GL as gl
from arcade.glui.render import Render
from arcade.glui.texture import Texture

CACHE_SIZE = 50
# QT stores RGBA data in BGRA data (on little-endian platforms at least)
TEXTURE_FORMAT = gl.GL_BGRA


class TextureManager(object):
    _instance = None  # type: TextureManager

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def __init__(self):
        self.lock = threading.Lock()
        self.image_list = []
        self.delay_set = set()
        self.image_dict = {}
        self.texture_dict = {}
        self.transparent = "\x00" * 512 * 512 * 4

    def set_image(self, image_path, image, size):
        with self.lock:
            if image_path not in self.image_dict:
                # no longer interested
                return
            self.image_dict[image_path] = (image, size)

    def load_images(self, image_paths):
        with self.lock:
            for ip in reversed(image_paths):
                if ip in self.image_dict:
                    self.image_list.remove(ip)
                    # self.image_list.insert(0, ip)
                else:
                    # texture = False means not loaded
                    # texture = None means failure loading
                    self.image_dict[ip] = False, None
                    self.texture_dict[ip] = None
                self.image_list.insert(0, ip)

            for ip in self.image_list[CACHE_SIZE:]:
                texture = self.texture_dict[ip]
                if texture is not None:
                    if texture is not Texture.default_item:
                        Render.get().delete_texture_list.append(
                            texture.texture
                        )
                del self.image_dict[ip]
                del self.texture_dict[ip]
            self.image_list = self.image_list[:CACHE_SIZE]

    def get_texture(self, ip):
        if ip is None:
            return None
        with self.lock:
            texture = self.texture_dict[ip]
            if texture:
                if ip in self.delay_set:
                    # do not return the texture the first time we ask for it,
                    # this is to allow the GPU driver time to upload the
                    # texture in the background (DMA transfer) without
                    # blocking for it
                    self.delay_set.remove(ip)
                    return None
            return texture

    def load_textures(self, max_num=10):
        loaded = 0
        target = gl.GL_TEXTURE_2D
        with self.lock:
            try:
                for ip in self.image_list:
                    if loaded == max_num:
                        break
                    texture = self.texture_dict[ip]
                    if texture is not None:
                        continue
                    pixels, size = self.image_dict[ip]
                    if pixels is False:
                        # queued
                        # self.texture_dict[ip] = Texture.default_item
                        continue
                    if pixels is None:
                        # could not load
                        # self.texture_dict[ip] = Texture(0, size=(0, 0))
                        # self.texture_dict[ip] = Texture.default_item
                        self.texture_dict[ip] = Texture.default_item
                        continue

                    texture = gl.glGenTextures(1)
                    self.texture_dict[ip] = Texture(
                        texture, size=(size[0], size[1])
                    )
                    self.delay_set.add(ip)

                    self.lock.release()

                    gl.glBindTexture(target, texture)
                    gl.glTexImage2D(
                        target,
                        0,
                        gl.GL_RGBA,
                        size[0],
                        size[1],
                        0,
                        TEXTURE_FORMAT,
                        gl.GL_UNSIGNED_BYTE,
                        pixels,
                    )
                    gl.glTexParameteri(
                        target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR
                    )
                    gl.glTexParameteri(
                        target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR
                    )
                    gl.glTexParameteri(
                        target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE
                    )
                    gl.glTexParameteri(
                        target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE
                    )
                    loaded += 1

                    self.lock.acquire()
            except Exception as e:
                print(e)

    def unload_textures(self):
        print("TextureManager.unload_textures")
        with self.lock:
            for ip in self.image_list:
                texture = self.texture_dict[ip]
                if texture is not None:
                    if texture is not Texture.default_item:
                        Render.get().delete_texture_list.append(
                            texture.texture
                        )
                self.texture_dict[ip] = None
