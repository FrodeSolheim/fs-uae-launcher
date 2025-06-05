from OpenGL import GL as gl


class DisplayLists(object):
    display_lists = {}

    @classmethod
    def clear(cls):
        for listid in cls.display_lists.values():
            gl.glDeleteLists(listid, 1)
        cls.display_lists.clear()

    @classmethod
    def call_or_create(cls, *params):
        try:
            gl.glCallList(cls.display_lists[params])
            return False
        except KeyError:
            display_list = gl.glGenLists(1)
            print("creating display list for params", params)
            gl.glNewList(display_list, gl.GL_COMPILE_AND_EXECUTE)
            cls.display_lists[params] = display_list
            return True
