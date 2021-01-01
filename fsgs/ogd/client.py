import platform
import time
from functools import wraps
from urllib.error import HTTPError
from urllib.parse import urlencode
from uuid import uuid4

import requests

from fsbc.settings import Settings
from fsbc.task import Task
from fsgs.network import openretro_url_prefix


class NonRetryableHTTPError(HTTPError):
    pass


class BadRequestError(NonRetryableHTTPError):
    pass


class UnauthorizedError(NonRetryableHTTPError):
    pass


class ForbiddenError(NonRetryableHTTPError):
    pass


class NotFoundError(NonRetryableHTTPError):
    pass


def retry(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        for i in range(10):
            if i > 0:
                print("retrying...")
            try:
                return f(*args, **kwargs)
            except NonRetryableHTTPError as e:
                raise e
            except Exception as e:
                print(repr(e))
                time.sleep(i * 0.5)
        return f(*args, **kwargs)

    return wrapper


class OGDClient(object):
    HTTPError = HTTPError
    BadRequestError = BadRequestError
    UnauthorizedError = UnauthorizedError
    ForbiddenError = ForbiddenError
    NotFoundError = NotFoundError
    NonRetryableHTTPError = NonRetryableHTTPError

    def __init__(self):
        self._json = None
        self.data = b""

    @staticmethod
    def is_logged_in():
        # non-empty ogd_auth means we are logged in (probably, the
        # authorization can in theory have been invalidated on the server
        return bool(Settings.instance()["database_auth"])

    def login_task(self, username, password):
        return LoginTask(self, username, password)

    def logout_task(self, auth_token):
        return LogoutTask(self, auth_token)

    @retry
    def authorize(self, username, password, device_id, device_name):
        result = self.post(
            "/api/auth",
            {
                "username": username,
                "password": password,
                "device_id": device_id,
                "device_name": device_name,
            },
            auth=False,
        )
        return result

    @retry
    def deauth(self, auth_token):
        result = self.post(
            "/api/deauth", {"auth_token": auth_token}, auth=False
        )
        return result

    @staticmethod
    def url_prefix():
        return openretro_url_prefix()

    @staticmethod
    def auth():
        auth_token = Settings.instance()["database_auth"]
        return ("auth_token", auth_token)

    def post(self, path, params=None, data=None, auth=True):
        headers = {}
        url = "{0}{1}".format(openretro_url_prefix(), path)
        if not data and params:
            data = urlencode(params)
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        print(url, headers)
        r = requests.post(
            url, data, headers=headers, auth=(self.auth() if auth else None)
        )
        r.raise_for_status()
        return r.json()

    def build_url(self, path, **kwargs):
        url = "{0}{1}".format(self.url_prefix(), path)
        if kwargs:
            url += "?" + urlencode(kwargs)
        return url

    def rate_variant(self, variant_uuid, like=None, work=None):
        params = {"game": variant_uuid}
        if like is not None:
            params["like"] = like
        if work is not None:
            params["work"] = work
        url = self.build_url("/api/1/rate_game", **params)
        r = requests.get(url, auth=self.auth())
        r.raise_for_status()
        return r.json()


def get_device_name():
    try:
        return platform.node() or "Unknown Computer"
    except Exception:
        return "Unknown Computer"


class LoginTask(Task):
    def __init__(self, client, username, password):
        Task.__init__(self, "Login Task")
        self.client = client
        self.username = username
        self.password = password

    def run(self):
        self.progressed("Logging into openretro.org...")
        if not Settings.instance()["device_id"]:
            Settings.instance()["device_id"] = str(uuid4())
        try:
            result = self.client.authorize(
                self.username,
                self.password,
                Settings.instance()["device_id"],
                get_device_name(),
            )
        except UnauthorizedError:
            raise Task.Failure("Wrong e-mail address or password")

        Settings.instance()["error_report_user_id"] = result["user_id"]
        Settings.instance()["database_username"] = result["username"]
        Settings.instance()["database_email"] = result["email"]
        Settings.instance()["database_auth"] = result["auth_token"]
        Settings.instance()["database_password"] = ""


class LogoutTask(Task):
    def __init__(self, client, auth_token):
        Task.__init__(self, "Logout Task")
        self.client = client
        self.auth_token = auth_token

    def run(self):
        self.progressed("Logging out from openretro.org...")
        if not Settings.instance()["device_id"]:
            Settings.instance()["device_id"] = str(uuid4())
        self.client.deauth(self.auth_token)

        Settings.instance()["error_report_user_id"] = ""
        Settings.instance()["database_username"] = ""
        # Settings.instance()["database_email"] = ""
        Settings.instance()["database_auth"] = ""
        Settings.instance()["database_password"] = ""
