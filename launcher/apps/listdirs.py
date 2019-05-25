from fsbc.settings import Settings
from fsgs.FSGSDirectories import FSGSDirectories

"""
Debug script used to dump information about detected plugins
"""


def app_main():
    FSGSDirectories.initialize()
    Settings.instance().verbose = False
    Settings.instance().load()
    print("base_dir", FSGSDirectories.get_base_dir())
    print("cache_dir", FSGSDirectories.get_cache_dir())
    print("cdroms_dir", FSGSDirectories.get_cdroms_dir())
    print("configurations_dir", FSGSDirectories.get_configurations_dir())
    print("controllers_dir", FSGSDirectories.get_controllers_dir())
    print("covers_dir", FSGSDirectories.get_covers_dir())
    print("data_dir", FSGSDirectories.get_data_dir())
    print("downloads_dir", FSGSDirectories.downloads_dir())
    print("floppies_dir", FSGSDirectories.get_floppies_dir())
    print("hard_drives_dir", FSGSDirectories.get_hard_drives_dir())
    # print("images_dir", FSGSDirectories.get_images_dir())
    print("kickstarts_dir", FSGSDirectories.get_kickstarts_dir())
    print("launcher_dir", FSGSDirectories.get_launcher_dir())
    print("logs_dir", FSGSDirectories.get_logs_dir())
    print("plugins_dir", FSGSDirectories.get_plugins_dir())
    # print("portable_dir", FSGSDirectories.portable_dir())
    print("save_states_dir", FSGSDirectories.get_save_states_dir())
    print("screenshots_dir", FSGSDirectories.get_screenshots_dir())
    print("screenshots_output_dir =", FSGSDirectories.screenshots_output_dir())
    print("themes_dir", FSGSDirectories.get_themes_dir())
    print("titles_dir", FSGSDirectories.get_titles_dir())
