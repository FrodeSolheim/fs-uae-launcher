import io
import os
import time
import json
import base64
import platform
from uuid import uuid4
from functools import wraps
from urllib.parse import urlencode
from http.client import HTTPConnection
from urllib.error import HTTPError
from fsbc.Application import app
from fsbc.task import Task
from fsbc.util import memoize
from fsgs.FSGSDirectories import FSGSDirectories


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
        pass

    @staticmethod
    def is_logged_in():
        # non-empty ogd_auth means we are logged in (probably, the
        # authorization can in theory have been invalidated on the server
        return bool(app.settings["database_auth"])

    def login_task(self, username, password):
        return LoginTask(self, username, password)

    def logout_task(self, auth_token):
        return LogoutTask(self, auth_token)

    @retry
    def auth(self, username, password, device_id, device_name):
        result = self.post(
            "/api/auth", {"username": username,
                          "password": password,
                          "device_id": device_id,
                          "device_name": device_name},
            auth=False)
        return result

    @retry
    def deauth(self, auth_token):
        result = self.post(
            "/api/deauth", {"auth_token": auth_token},
            auth=False)
        return result

    @staticmethod
    @memoize
    def get_server():
        server = app.settings["database_server"]
        if not server:
            p = os.path.join(FSGSDirectories.get_data_dir(), "Settings",
                             "database-server")
            if os.path.exists(p):
                with io.open(p, "r", encoding="UTF-8") as f:
                    server = f.read().strip()
        if not server:
            server = "oagd.net"
        return server

    @staticmethod
    def get_credentials():
        auth_token = app.settings["database_auth"]
        return "auth_token", auth_token

    def post(self, path, params=None, data=None, auth=True):
        headers = {
        }
        if auth:
            credentials = self.get_credentials()
            headers[str("Authorization")] = str("Basic " + base64.b64encode(
                "{0}:{1}".format(*credentials).encode("UTF-8")))

        # if data is None:
        #     data = "{}"
        server = self.get_server()
        connection = HTTPConnection(server, timeout=30)
        url = "http://{0}{1}".format(server, path)
        # if params:
        #     url += "?" + urlencode(params)
        if not data and params:
            data = urlencode(params)
            headers[str("Content-Type")] = \
                str("application/x-www-form-urlencoded")

        print(url, headers)
        if isinstance(data, dict):
            data = json.dumps(data)
        # print(data)
        connection.request(str("POST"), str(url), data, headers=headers)
        response = connection.getresponse()
        if response.status not in [200]:
            print(response.status, response.reason)
            if response.status == 400:
                class_ = BadRequestError
            elif response.status == 401:
                class_ = UnauthorizedError
            elif response.status == 403:
                class_ = ForbiddenError
            elif response.status == 404:
                class_ = NotFoundError
            else:
                class_ = HTTPError
            raise class_(url, response.status, response.reason,
                         response.getheaders(), None)
        data = response.read()
        if len(data) > 0 and data[0:1] == b"{":
            doc = json.loads(data.decode("UTF-8"))
            return doc
        return data


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
        self.progressed("Logging into oagd.net...")
        if not app.settings["device_id"]:
            app.settings["device_id"] = str(uuid4())
        try:
            result = self.client.auth(
                self.username, self.password, app.settings["device_id"],
                get_device_name())
        except UnauthorizedError:
            raise Task.Failure("Wrong e-mail address or password")

        app.settings["database_username"] = result["username"]
        app.settings["database_email"] = result["email"]
        app.settings["database_auth"] = result["auth_token"]
        app.settings["database_password"] = ""


class LogoutTask(Task):

    def __init__(self, client, auth_token):
        Task.__init__(self, "Logout Task")
        self.client = client
        self.auth_token = auth_token

    def run(self):
        self.progressed("Logging out from oagd.net...")
        if not app.settings["device_id"]:
            app.settings["device_id"] = str(uuid4())
        self.client.deauth(self.auth_token)

        app.settings["database_username"] = ""
        # app.settings["database_email"] = ""
        app.settings["database_auth"] = ""
        app.settings["database_password"] = ""
