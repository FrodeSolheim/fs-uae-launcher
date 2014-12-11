from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from gzip import GzipFile
from io import StringIO
from fsbc.http import urlencode, quote_plus
from fsbc.http import HTTPBasicAuthHandler, build_opener, Request
from fsgs.ogd.client import OGDClient


class OAGDClient(object):

    def __init__(self):
        self._server = None
        self._opener = None

        # FIXME: we don't want dependency on Settings here
        from fs_uae_launcher.Settings import Settings
        self.username = "auth_token"
        self.password = Settings.get("database_auth")

    def server(self):
        return OGDClient.get_server()

    def opener(self):
        if self._opener:
            return self._opener
        server = self.server()
        auth_handler = HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm="Open Amiga Game Database",
            uri="http://{0}".format(server), user=self.username,
            passwd=self.password)
        self._opener = build_opener(auth_handler)
        return self._opener

    def build_url(self, path, **kwargs):
        url = "http://{0}{1}".format(self.server(), path)
        if kwargs:
            url += "?" + urlencode(kwargs)
        return url

    def handle_response(self, response):
        self._json = None
        self.data = response.read()

        #print(dir(response.headers))
        try:
            getheader = response.headers.getheader
        except AttributeError:
            getheader = response.getheader
        content_encoding = getheader("content-encoding", "").lower()
        if content_encoding == "gzip":
            #data = zlib.decompress(data)
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
        opener = self.opener()
        request = Request(url)
        print("get_request:", url)
        request.add_header("Accept-Encoding", "gzip")
        response = opener.open(request)
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
