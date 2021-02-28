import os

from fsboot import executable_dir
from fscore.system import System


def launcher_data_file_path(relative):
    paths = []
    # Check the same directory as the executable first
    path = os.path.join(executable_dir(), relative)
    paths.append(path)
    if os.path.exists(path):
        return path

    # FIXME: check development mode
    development_mode = True
    if development_mode:
        # Check in the data dir (during development and testing)
        path = os.path.join(executable_dir(), "data", relative)
        paths.append(path)
        if os.path.exists(path):
            return path

    # Check in the plugin data dir
    # FIXME: check plugin mode
    plugin_mode = True
    if plugin_mode:
        if System.macos:
            # Need to go further up in the hierarchy due to being bundled
            # insidean application bundle.
            path = os.path.join(
                executable_dir(),
                "..",
                "..",
                "..",
                "..",
                "..",
                "Data",
                relative,
            )
        else:
            path = os.path.join(executable_dir(), "..", "..", "Data", relative)
        paths.append(path)
        if os.path.exists(path):
            return path

    # FIXME: Move up?
    if System.macos:
        path = os.path.join(executable_dir(), "..", "Resources", "Data", relative)
    else:
        path = os.path.join(
            executable_dir(), "..", "share", "fs-uae-launcher", relative
        )
    paths.append(path)
    if os.path.exists(path):
        return path
    print("No data file in any of these locations:", paths)
    raise FileNotFoundError(relative)


def launcher_data_file(filename):
    return open(launcher_data_file_path(filename), "rb")
