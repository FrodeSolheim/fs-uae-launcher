import atexit
import json
import os
import subprocess


def reset_gnome_extensions(extensions):
    print("reset_gnome_extensions", extensions)
    p = subprocess.Popen(
        ["gsettings", "set", "org.gnome.shell", "enabled-extensions",
         json.dumps(extensions).replace("\"", "'")])
    return p.wait() == 0


def handle_gnome_extensions():||||||||||||||||||||||||||
    original_extensions = []
    try:
        p = subprocess.Popen(
            ["gsettings", "get", "org.gnome.shell", "enabled-extensions"],
            stdout=subprocess.PIPE)
        # noinspection PyUnresolvedReferences
        data = p.stdout.read().decode("UTF-8", errors="replace")
        if p.wait() == 0:
            print("enabled-extensions:")
            print(data)
            if data.startswith("@as "):
                data = data[4:]
            original_extensions = json.loads(data.replace("'", "\""))
            print(original_extensions)
    except FileNotFoundError:
        print("no gsettings program found")
        return
    except ValueError as e:
        print(repr(e))
        print("could not decode enabled-exceptions")
        return

    new_extensions = original_extensions.copy()
    if "window-list@gnome-shell-extensions.gcampax.github.com" \
            in original_extensions:
        new_extensions.remove(
            "window-list@gnome-shell-extensions.gcampax.github.com")
    if "hidetopbar@mathieu.bidon.ca" not in original_extensions:
        new_extensions.append("hidetopbar@mathieu.bidon.ca")

    if new_extensions != original_extensions:
        p = subprocess.Popen(
            ["gsettings", "set", "org.gnome.shell", "enabled-extensions",
             json.dumps(new_extensions).replace("\"", "'")])
        if p.wait() == 0:
            print("atexit.register reset_gnome_extensions")
            atexit.register(reset_gnome_extensions, original_extensions)

    # sys.exit(1)


def running_in_gnome_3():
    value = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
    if value:
        return value == "GNOME"
    value = os.environ.get("DESKTOP_SESSION", "").upper()
    if value:
        return value == "GNOME"
    return False
