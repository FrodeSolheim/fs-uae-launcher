from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import fsbc.fs as fs
from .signal import Signal
import six
from fsbc.configparser import ConfigParser, NoSectionError


class Settings(object):

    #_instance = None
    #
    #@classmethod
    #def instance(cls):
    #    if not cls._instance:
    #        #noinspection PyAttributeOutsideInit
    #        cls._instance = cls()
    #    return cls._instance

    def __init__(self, app):
        self.app = app
        self.values = {}
        self.load()

    def __getitem__(self, key):
        # FIXME: hack
        # from fs_uae_launcher.Settings import Settings as _Settings
        # return _Settings.get(key)
        return self.values.get(key, "")

    def __setitem__(self, key, value):
        # FIXME: hack
        # from fs_uae_launcher.Settings import Settings as _Settings
        # return _Settings.set(key, value)

        if self[key] == value:
            print("set {0} to {1} (no change)".format(key, value))
            return
        if "username" in key or "password" in key or "auth" in key \
            or "email" in key:
            print("set {0} to *CENSORED*".format(key))
        else:
            print("set {0} to {1}".format(key, value))
        self.values[key] = value
        Signal("setting").notify(key, value)

    #@classmethod
    #def get(cls, key):
    #    #return cls.settings.setdefault(key, "")
    #    return cls.settings.get(key, "")
    #
    #@classmethod
    #def set(cls, key, value):
    #    if cls.get(key) == value:
    #        print("set {0} to {1} (no change)".format(key, value))
    #        return
    #    if "username" in key or "password" or "auth" in key:
    #        print("set {0} to *CENSORED*".format(key))
    #    else:
    #        print("set {0} to {1}".format(key, value))
    #    cls.settings[key] = value
    #    #for listener in cls.settings_listeners:
    #    #    listener.on_setting(key, value)
    #    Signal("setting").broadcast(key, value)

    def load(self):
        path = self.app.get_settings_path()
        print("loading settings from " + repr(path))
        if not os.path.exists(path):
            print("settings file does not exist")
        if six.PY3:
            # noinspection PyArgumentList
            cp = ConfigParser(interpolation=None)
        else:
            cp = ConfigParser()
        try:
            cp.read([path])
        except Exception as e:
            print(repr(e))
            return

        settings = {}
        try:
            keys = cp.options("settings")
        except NoSectionError:
            keys = []
        for key in keys:
            settings[key] = fs.from_utf8_str(cp.get("settings", key))
        for key, value in six.iteritems(settings):
            #if key in Settings.settings:
            #    # this setting is already initialized, possibly via
            #    # command line arguments
            #    pass
            #else:

            #Settings.settings[key] = value

            self.values[key] = value

        #Settings.set("config_search", "")
