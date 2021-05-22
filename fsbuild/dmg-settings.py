_arch = "x86-64"

# filename = "TEST"
# volume_name = "FS-UAE-Launcher"
format = "UDZO"
files = [
    f"fsbuild/_build/FS-UAE-Launcher/macOS/{_arch}/FS-UAE-Launcher.app"
]
symlinks = { 'Applications': '/Applications' }
badge_icon = "icon/fs-uae-launcher.icns"
