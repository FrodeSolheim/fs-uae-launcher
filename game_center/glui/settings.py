import os
# import pygame
from fsbc.user import get_home_dir, get_documents_dir
from fsbc.system import windows
from fsbc.util import memoize


@memoize
def get_fullscreen_size():
    # pygame.display.init()
    # display_info = pygame.display.Info()
    # size = (display_info.current_w, display_info.current_h)
    # print("fullscreen size:", size)
    # return size
    pass


class Settings(object):
    cache_dir_path = None
    games_dir_path = None
    profile_dir_path = None
    # use_fullscreen = False

    if windows:
        # fullscreen_menu = False
        window_decorations = False
    else:
        # fullscreen_menu = True
        window_decorations = True

    fullscreen_menu = True
    fullscreen_game = True
    # windowed_size = (640, 480)
    windowed_size = None  # Maximized
    fullscreen_size = get_fullscreen_size()
    fullscreen_pos = 0, 0

    @classmethod
    def get_games_path(cls):
        path = []
        if cls.games_dir_path:
            path.extend(cls.games_dir_path)
        elif windows:
            path.append(os.path.join(
                get_documents_dir(), "Games (Ku Game System)"))
        else:
            path.append(os.path.join(get_home_dir(), "Games"))
        return path

    @classmethod
    def get_resources_dir(cls):
        path = os.path.join(cls.get_games_path()[0], "Resources")
        return path

    @classmethod
    def get_config_dir(cls):
        pass

    @classmethod
    def get_profile_dir(cls):
        if cls.profile_dir_path:
            return cls.profile_dir_path
        elif windows:
            return os.path.join(
                get_documents_dir(), "Gamer Profile (Ku Game System)")
        else:
            return os.path.join(
                get_home_dir(), "Gamer Profile (Ku Game System)")
