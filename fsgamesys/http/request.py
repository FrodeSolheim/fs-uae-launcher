import json
from urllib.parse import parse_qsl

from fsgamesys.http.requestparams import RequestParams


class Request:
    def __init__(self, environ):
        self.environ = environ
        self.session_id = ""
        self.fsgs = None
        self.params = RequestParams()

        ct = environ.get("CONTENT_TYPE", "").lower()
        cl = environ.get("CONTENT_LENGTH", "")
        if cl:
            cl = int(cl)
        else:
            cl = 0
        print(ct)
        if ct in ["application/json", "application/json;charset=utf-8"]:
            input = environ["wsgi.input"]
            print("reading...")
            body = input.read(cl)
            print("reading done")
            print(body)
            body_object = json.loads(body.decode("UTF-8"))
            print(body_object)
            if isinstance(body_object, dict):
                for key, value in body_object.items():
                    setattr(self.params, key, value)

        query_string = environ.get("QUERY_STRING", "")
        items = parse_qsl(
            query_string, keep_blank_values=False, strict_parsing=False
        )
        for item in items:
            setattr(self.params, item[0], item[1])
