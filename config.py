title = "FS-UAE Launcher"
name = "fs-uae-launcher"
py_name = "fs_uae_launcher"
tar_name = "fs-uae-launcher"
version = "9.8.7dummy"
author = "Frode Solheim"
author_email = "frode@fs-uae.net"
package_map = {
    "fs_uae_launcher": ".",
    "fs_uae_workspace": ".",
    "fsbc": ".",
    "fsgs": ".",
    "fsui": ".",
    "game_center": ".",
    "OpenGL": ".",
    "six": ".",
    "typing": ".",
}
packages = sorted(package_map.keys())
#import sys
#if sys.platform != "win32":
#    packages.remove("game_center")
scripts = ["fs-uae-launcher"]
