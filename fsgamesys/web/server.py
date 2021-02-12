# import http.server


DEFAULT_PORT = 25988
DEFAULT_ADDRESS = "127.0.0.1"

# noinspection PyUnresolvedReferences
import fsgamesys.web.handlers


# class FSGSWebServerHandler(http.server.BaseHTTPRequestHandler):
#
#     # noinspection PyPep8Naming
#     def do_POST(self):
#         pass


class FSGSWebServer(object):
    def run(self):
        # server_class = http.server.HTTPServer
        # handler_class = FSGSWebServerHandler
        # server_address = (DEFAULT_ADDRESS, DEFAULT_PORT)
        print("Listening on {}:{}".format(DEFAULT_ADDRESS, DEFAULT_PORT))
        # httpd = server_class(server_address, handler_class)
        # httpd.serve_forever()

        from bottle import run

        run(host=DEFAULT_ADDRESS, port=DEFAULT_PORT)
