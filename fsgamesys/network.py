import os
from functools import lru_cache
from typing import Optional, Tuple

from fsbc.settings import Settings
from fsgamesys.FSGSDirectories import FSGSDirectories


@lru_cache()
def default_openretro_server_from_file() -> Optional[str]:
    server = None
    p = os.path.join(
        FSGSDirectories.get_data_dir(), "Settings", "database-server"
    )
    if os.path.exists(p):
        with open(p, "r", encoding="UTF-8") as f:
            server = f.read().strip()
    return server


def default_openretro_server() -> str:
    return "https://openretro.org"


def fs_uae_url_from_sha1_and_name(sha1: str, name: str) -> str:
    return "https://fs-uae.net/s/sha1/{0}/{1}".format(sha1, name)


def openretro_server() -> Tuple[str, str]:
    server = Settings.instance()["database_server"]
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


def openretro_scheme() -> str:
    # if openretro_host() == default_openretro_host():
    #     return "https"
    return "http"


def openretro_url_prefix() -> str:
    scheme, host = openretro_server()
    return "{}://{}".format(scheme, host)


def is_http_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")
