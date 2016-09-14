import os
from functools import lru_cache
from http.client import HTTPConnection, HTTPSConnection
from urllib.request import build_opener, HTTPBasicAuthHandler

from fsbc.application import app
from fsgs.FSGSDirectories import FSGSDirectories


@lru_cache()
def default_openretro_server_from_file():
    server = None
    p = os.path.join(
        FSGSDirectories.get_data_dir(), "Settings", "database-server")
    if os.path.exists(p):
        with open(p, "r", encoding="UTF-8") as f:
            server = f.read().strip()
    return server


def default_openretro_server():
    return "http://openretro.org"


def fs_uae_url_from_sha1_and_name(sha1, name):
    return "http://fs-uae.net/s/sha1/{0}/{1}".format(sha1, name)


def openretro_server():
    server = app.settings["database_server"]
    if not server:
        server = default_openretro_server_from_file()
    if not server:
        server = default_openretro_server()
    if "://" in server:
        scheme, host = server.split("://")
    else:
        scheme = "http"
        host = server
    return scheme, host


def openretro_scheme():
    # if openretro_host() == default_openretro_host():
    #     return "https"
    return "http"


def openretro_url_prefix():
    scheme, host = openretro_server()
    return "{}://{}".format(scheme, host)


def openretro_http_connection():
    scheme, host = openretro_server()
    if scheme == "https":
        connection = HTTPSConnection(host, timeout=30)
    else:
        connection = HTTPConnection(host, timeout=30)
    return connection


def opener_for_url_prefix(
        url_prefix, username=None, password=None, cache_dict=None):
    if cache_dict is not None:
        cache_key = (url_prefix, username, password)
        try:
            return cache_dict[cache_key]
        except KeyError:
            pass
    if username or password:
        auth_handler = HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm="Open Amiga Game Database", uri="{0}".format(url_prefix),
            user=username, passwd=password)
        auth_handler.add_password(
            realm="OpenRetro", uri="{0}".format(url_prefix),
            user=username, passwd=password)
        opener = build_opener(auth_handler)
    else:
        opener = build_opener()
    if cache_dict is not None:
        cache_key = (url_prefix, username, password)
        cache_dict[cache_key] = opener
    return opener


def is_http_url(url):
    return url.startswith("http://") or url.startswith("https://")
