import re
import json
import traceback
from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server
from fsgs.FSGameSystemContext import FSGameSystemContext
from fsgs.session import Session
from fsgs.http.request import Request

"""

POST /sessions

GET /sessions
{
    "id": "00000000-0000-0000-0000-000000000000"
}

"""


class ClientError(Exception):
    def __init__(self, message, code=400):
        Exception.__init__(self, message)
        self.code = code


default_fsgs = FSGameSystemContext()


def fsgs_from_session(session_id):
    assert session_id == "default"
    return default_fsgs


def configure_session(request, session_id):
    assert session_id == "default"
    request.session_id = session_id
    request.fsgs = fsgs_from_session(session_id)


# def get_sessions_handler(request):
#     return {}


def json_list(the_list):
    return {"list_hack": the_list}


def get_platforms_handler(request):
    return json_list(
        [
            {"id": "amiga", "name": "Amiga", "type": "Home Computer"},
            {"id": "arcade", "name": "Arcade", "type": "Arcade Machines"},
            {
                "id": "cd32",
                "name": "CD32",
                # "name": "Amiga CD32",
                "type": "TV Console",
            },
            {
                "id": "cdtv",
                "name": "CDTV",
                # "name": "Commodore CDTV",
                "type": "TV Console",
            },
            {
                "id": "dos",
                "name": "DOS",
                # "name": "DOS (PC)",
                "type": "Home Computer",
            },
            {
                "id": "gba",
                "name": "Game Boy Advance",
                "type": "Handheld Console",
            },
            {"id": "nes", "name": "Nintendo (NES)", "type": "TV Console"},
            {"id": "snes", "name": "Super Nintendo", "type": "TV Console"},
        ]
    )


def get_games_handler(request):
    fsgs = FSGameSystemContext()
    # game_database = fsgs.get_game_database()
    # return {"platform:": request.params.platform}

    terms = []
    if request.params.platform:
        platform = request.params.platform
        # FIXME
        if platform == "snes":
            platform = "super-nintendo"
        elif platform == "gba":
            platform = "game-boy-advance"
        terms.append("platform:{}".format(platform))

    terms.append("t:thumb")

    database_items = fsgs.database().find_games_new(" ".join(terms))
    result = []
    for item in database_items:

        # query = "SELECT DISTINCT uuid, name, platform, year, publisher, " \
        #         "front_image, title_image, screen1_image, screen2_image, " \
        #         "screen3_image, screen4_image, screen5_image, have, path, " \
        #         "sort_key, subtitle FROM game"

        # backdrop = item[17].replace("sha1:", "")
        # if backdrop:
        #    # backdrop, hs, vs, ha, va = backdrop.split("/")

        result.append(
            {
                "uuid": item[0],
                "platform": item[2],
                "name": item[1],
                "subtitle": item[15],
                "year": item[3],
                "publisher": item[4],
                # "title_image": item[6].replace("sha1:", ""),
                # "screen1_image": item[7].replace("sha1:", ""),
                "thumb": item[16].replace("sha1:", ""),
                # "backdrop": backdrop,
                "backdrop": item[17],
            }
        )
    return json_list(result)


def get_session_handler(request, session_id):
    configure_session(request, session_id)
    return {}


def post_session_init_handler(request, session_id):
    configure_session(request, session_id)
    print(request.params.game_uuid)
    request.fsgs.load_game_by_uuid(request.params.game_uuid)

    from fsbc.application import app

    if request.params.fullscreen:
        # print("setting fullscreen to", repr(request.params.fullscreen))
        # request.fsgs.config.set("fullscreen", request.params.fullscreen)
        app.settings.set("fullscreen", request.params.fullscreen)
    if request.params.fullscreen_mode:
        app.settings.set("fullscreen_mode", request.params.fullscreen_mode)
    if request.params.window_border:
        app.settings.set("window_border", request.params.window_border)
    return {}


instances = {}


def post_session_instances_handler(request, session_id):
    configure_session(request, session_id)

    print(request.params.game_uuid)

    session = Session(request.fsgs)
    instance = session.create_instance()
    instances[instance.uuid] = instance
    instance.start()

    return {"instance_id": instance.uuid}


def get_instance_handler(request, session_id, instance_id):
    configure_session(request, session_id)
    try:
        instance = instances[instance_id]
    except KeyError:
        raise ClientError("Instance not found", code=404)
    return {"instance_id": instance.uuid, "state": instance.state}


def put_instance_handler(request, session_id, instance_id):
    configure_session(request, session_id)
    try:
        instance = instances[instance_id]
    except KeyError:
        raise ClientError("Instance not found", code=404)
    if request.params.state:
        ins = instance
        old = instance.state
        new = request.params.state
        if old == ins.STATE_INITIALIZED and new == ins.STATE_PREPARING:
            instance.state = new
        elif old == ins.STATE_READY and new == ins.STATE_RUNNING:
            instance.state = new
        elif old == ins.STATE_STOPPED and new == ins.STATE_FINALIZING:
            instance.state = new
        else:
            raise ClientError("Illegal state change")
    return {"instance_id": instance.uuid, "state": instance.state}


def delete_instance_handler(request, session_id, instance_id):
    configure_session(request, session_id)
    try:
        instance = instances[instance_id]
    except KeyError:
        raise ClientError("Instance not found", code=404)
    if instance.state != instance.STATE_FINALIZED:
        raise ClientError("Excepted FINALIZED state")
    instance.destroy()
    del instances[instance_id]
    return {}


class URLMapping:
    def __init__(self, method, path, handler):
        self.method = method
        self.path = path
        self.handler = handler

        self.param_names = []
        # quick hack
        # FIXME: must escape some literals, etc
        re_str = path

        if "{session_id}" in re_str:
            re_str = re_str.replace("{session_id}", "(?P<session_id>[^/]+)")
            self.param_names.append("session_id")
        if "{instance_id}" in re_str:
            re_str = re_str.replace("{instance_id}", "(?P<instance_id>[^/]+)")
            self.param_names.append("instance_id")

        re_str = "^" + re_str + "$"
        print(re_str)
        self.re = re.compile(re_str)

    def match(self, environ):
        path = environ["PATH_INFO"]
        # print(environ["REQUEST_METHOD"], path)
        if self.method != environ["REQUEST_METHOD"]:
            return None
        m = self.re.match(path)
        # print(m)
        if m is not None:
            return m.groupdict()
        return None

    def run_handler(self, request, kwargs):
        print("run_handler", self.path, "args =", kwargs)
        return self.handler(request, **kwargs)


url_map = [
    URLMapping("GET", "/games", get_games_handler),
    URLMapping("GET", "/platforms", get_platforms_handler),
    # URLMapping("GET", "/sessions", get_sessions_handler),
    URLMapping("GET", "/sessions/{session_id}", get_session_handler),
    URLMapping(
        "POST", "/sessions/{session_id}/init", post_session_init_handler
    ),
    URLMapping(
        "POST",
        "/sessions/{session_id}/instances",
        post_session_instances_handler,
    ),
    URLMapping(
        "GET",
        "/sessions/{session_id}/instances/{instance_id}",
        get_instance_handler,
    ),
    URLMapping(
        "PUT",
        "/sessions/{session_id}/instances/{instance_id}",
        put_instance_handler,
    ),
    URLMapping(
        "DELETE",
        "/sessions/{session_id}/instances/{instance_id}",
        delete_instance_handler,
    ),
]


def create_application():

    fsgs = FSGameSystemContext()

    # A relatively simple WSGI application. It's going to print out the
    # environment dictionary after being updated by setup_testing_defaults
    def simple_app(environ, start_response):
        # FIXME: remove use of setup_testing_defaults
        setup_testing_defaults(environ)
        environ["fsgs"] = fsgs

        for mapping in url_map:
            kwargs = mapping.match(environ)
            if kwargs is not None:
                request = Request(environ)
                try:
                    result = mapping.run_handler(request, kwargs)
                    status = "200 OK"
                    if isinstance(result, dict):
                        headers = [("Content-type", "application/json")]
                        if "list_hack" in result:
                            result = result["list_hack"]
                        data = json.dumps(result, indent=4).encode("UTF-8")
                    else:
                        raise Exception("unknown result data type")
                    # headers = [("Content-type", "application/octet-stream")]
                    # data = json.dumps(result).encode("UTF-8")
                except Exception as e:
                    traceback.print_exc()
                    status = "500 Internal Server Error"
                    headers = [("Content-type", "text/plain")]
                    data = repr(e).encode("UTF-8")
                start_response(status, headers)
                return [data]

        start_response("404 Not Found", [("Content-type", "text/plain")])
        return [b"The resource was not found"]

    return simple_app


def http_server_main():
    port = 15232
    app = create_application()
    httpd = make_server("127.0.0.1", port, app)
    print("Serving on port {port}...".format(port=port))
    httpd.serve_forever()
