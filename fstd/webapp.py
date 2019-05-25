import bottle
import threading


class Request(object):
    def __init__(self):
        pass


def get_request():
    return _thread_local.request


class Proxy(object):
    def __init__(self, func):
        self._func = func

    def __getattr__(self, name):
        return getattr(self._func(), name)

    def __setattr__(self, name, value):
        return setattr(self._func(), name, value)


class WebApp(object):
    def __init__(self):
        pass

    def route(self, path):
        def wrapper(func):
            def wrapper2():
                print("wrapper", func)
                return func()

            return bottle.route(path)(wrapper2)

        return wrapper


_thread_local = threading.local()
# request = Proxy(get_request)
