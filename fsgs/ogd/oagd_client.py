import json
from gzip import GzipFile
from io import StringIO
from urllib.parse import urlencode
from urllib.request import Request

from fsgs.ogd.client import OGDClient


# FIXME: Merge with OGDClient


class OAGDClient(OGDClient):
    def __init__(self):
        super().__init__()
        self._json = None
        self.data = b""

    def build_url(self, path, **kwargs):
        url = "{0}{1}".format(self.url_prefix(), path)
        if kwargs:
            url += "?" + urlencode(kwargs)
        return url

    def handle_response(self, response):
        self._json = None
        self.data = response.read()
        # print(dir(response.headers))
        try:
            getheader = response.headers.getheader
        except AttributeError:
            getheader = response.getheader
        content_encoding = getheader("content-encoding", "").lower()
        if content_encoding == "gzip":
            # data = zlib.decompress(data)
            fake_stream = StringIO(self.data)
            self.data = GzipFile(fileobj=fake_stream).read()

    def json_response(self):
        if self._json is None:
            self._json = json.loads(self.data.decode("UTF-8"))
        return self._json

    def get(self, key, default):
        doc = self.json_response()
        return doc.get(key, default)

    def get_request(self, url):
        request = Request(url)
        print("get_request:", url)
        request.add_header("Accept-Encoding", "gzip")
        response = self.opener().opener.open(request)
        return self.handle_response(response)

    def rate_variant(self, variant_uuid, like=None, work=None):
        params = {
            "game": variant_uuid,
        }
        if like is not None:
            params["like"] = like
        if work is not None:
            params["work"] = work
        url = self.build_url("/api/1/rate_game", **params)
        self.get_request(url)
