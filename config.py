title = "FS-UAE Launcher"
name = "fs-uae-launcher"
py_name = "fs_uae_launcher"
tar_name = "fs-uae-launcher"
version = "9.8.7dummy"
author = "Frode Solheim"
author_email = "frode@fs-uae.net"
package_map = {
    "amitools": ".",
    "arcade": ".",
    "fsbc": ".",
    "fsboot": ".",
    "fsgs": ".",
    "fspy": ".",
    "fstd": ".",
    "fsui": ".",
    "launcher": ".",
    "OpenGL": ".",
    "oyoyo": ".",
    "requests": ".",
    "workspace": ".",
}
packages = sorted(package_map.keys())
scripts = ["fs-uae-launcher"]
