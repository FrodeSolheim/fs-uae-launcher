from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import six
import subprocess
from fsbc.path import unicode_path
from fsbc.system import windows, macosx
from fsbc.util import memoize
if windows:
    # noinspection PyUnresolvedReferences
    from win32com.shell import shell, shellcon
    # noinspection PyUnresolvedReferences
    import win32api
else:
    import getpass


@memoize
def get_user_name():
    if windows:
        user_name = win32api.GetUserName()
        encoding = "mbcs"
    else:
        user_name = getpass.getuser()
        encoding = "UTF-8"
    if isinstance(user_name, six.text_type):
        return user_name
    return six.text_type(user_name, encoding, "replace")


@memoize
def xdg_user_dir(name):
    if windows or macosx:
        return
    try:
        process = subprocess.Popen(["xdg-user-dir", name],
                                   stdout=subprocess.PIPE)
        path = process.stdout.read().strip()
        path = path.decode("UTF-8")
        print("XDG user dir {0} => {1}".format(name, repr(path)))
    except Exception:
        path = None
    return path


@memoize
def get_desktop_dir(allow_create=True):
    if windows:
        path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, 0, 0)
    else:
        path = xdg_user_dir("DESKTOP")
        if not path:
            path = os.path.join(get_home_dir(), 'Desktop')
    path = unicode_path(path)
    if allow_create and not os.path.isdir(path):
        os.makedirs(path)
    return path


@memoize
def get_documents_dir(create=False):
    if windows:
        path = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, 0, 0)
    elif macosx:
        path = os.path.join(get_home_dir(), 'Documents')
    else:
        path = xdg_user_dir("DOCUMENTS")
        if not path:
            path = get_home_dir()
    path = unicode_path(path)
    if create and not os.path.isdir(path):
        os.makedirs(path)
    return path


@memoize
def get_pictures_dir(allow_create=True):
    if windows:
        path = shell.SHGetFolderPath(0, shellcon.CSIDL_MYPICTURES, 0, 0)
    else:
        path = xdg_user_dir("PICTURES")
        if not path:
            path = os.path.join(get_home_dir(), 'Pictures')
    path = unicode_path(path)
    if allow_create and not os.path.isdir(path):
        os.makedirs(path)
    return path


@memoize
def get_home_dir():
    if windows:
        path = shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, 0, 0)
        return path
    return unicode_path(os.path.expanduser("~"))
