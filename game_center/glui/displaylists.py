from game_center.glui.opengl import glDeleteLists, glCallList, glNewList, glGenLists
from game_center.glui.opengl import GL_COMPILE_AND_EXECUTE


class DisplayLists(object):

    display_lists = {}

    @classmethod
    def clear(cls):
        for listid in cls.display_lists.values():
            glDeleteLists(listid, 1)
        cls.display_lists.clear()

    @classmethod
    def call_or_create(cls, *params):
        try:
            glCallList(cls.display_lists[params])
            return False
        except KeyError:
            display_list = glGenLists(1)
            print("creating display list for params", params)
            glNewList(display_list, GL_COMPILE_AND_EXECUTE)
            cls.display_lists[params] = display_list
            return True
