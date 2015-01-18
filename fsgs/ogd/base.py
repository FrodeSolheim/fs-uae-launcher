import sys
import json
import time
from gzip import GzipFile
from io import StringIO

from urllib.request import HTTPBasicAuthHandler, build_opener, Request
from fsgs.res import gettext
from .client import OGDClient


if sys.version > '3':
    PYTHON3 = True
else:
    PYTHON3 = False


class SynchronizerBase(object):

    def __init__(self, context, on_status=None, stop_check=None):
        self.context = context
        self.on_status = on_status
        self._stop_check = stop_check

    if PYTHON3:
        @staticmethod
        def bytes_to_int(m):
            return m[0] << 24 | m[1] << 16 | m[2] << 8 | m[3]
    else:
        @staticmethod
        def bytes_to_int(m):
            return (ord(m[0]) << 24 | ord(m[1]) << 16 |
                    ord(m[2]) << 8 | ord(m[3]))

    def stop_check(self):
        if self._stop_check:
            return self._stop_check()

    def set_status(self, title, status=""):
        if self.on_status:
            self.on_status((title, status))

    @staticmethod
    def get_server():
        return OGDClient.get_server()

    def get_opener(self):
        server = self.get_server()
        auth_handler = HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm="Open Amiga Game Database",
            uri="http://{0}".format(server),
            user=self.context.username,
            passwd=self.context.password)
        opener = build_opener(auth_handler)
        return opener

    def fetch_json_attempt(self, url):
        data = self.fetch_data_attempt(url, accept_gzip_encoding=True)
        return json.loads(data.decode("UTF-8"))

    def fetch_json(self, url):
        for i in range(20):
            try:
                return self.fetch_json_attempt(url)
            except Exception as e:
                print(e)
                sleep_time = 2.0 + i * 0.3
                # FIXME: change second {0} to {1}
                self.set_status(
                    gettext("Download failed (attempt {0}) - retrying in {0} "
                            "seconds").format(i + 1, int(sleep_time)))
                time.sleep(sleep_time)
                self.set_status(
                    gettext("Retrying last operation (attempt {0})").format(
                        i + 1))
        return self.fetch_json_attempt(url)

    def fetch_data_attempt(self, url, accept_gzip_encoding=False):
        if not url.startswith("http"):
            url = "http://{0}{1}".format(self.get_server(), url)
        opener = self.get_opener()
        print(url)
        request = Request(url)
        if accept_gzip_encoding:
            request.add_header("Accept-Encoding", "gzip")
        response = opener.open(request)
        # print(response.headers)
        data = response.read()

        try:
            getheader = response.headers.getheader
        except AttributeError:
            getheader = response.getheader
        content_encoding = getheader("content-encoding", "").lower()
        if content_encoding == "gzip":
            fake_stream = StringIO(data)
            data = GzipFile(fileobj=fake_stream).read()
        return data

    def fetch_data(self, url):
        for i in range(10):
            try:
                return self.fetch_data_attempt(url)
            except Exception as e:
                print(e)
                sleep_time = 2.0 + i * 0.3
                # FIXME: change second {0} to {1}
                self.set_status(
                    gettext("Download failed (attempt {0}) - retrying in {0} "
                            "seconds").format(i + 1, int(sleep_time)))
                time.sleep(sleep_time)
                self.set_status(
                    gettext("Retrying last operation (attempt {0})").format(
                        i + 1))
        return self.fetch_data_attempt(url)
