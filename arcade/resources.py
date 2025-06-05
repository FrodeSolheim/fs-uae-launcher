import logging

from fsbc.resources import Resources as BaseResources

logger = logging.getLogger("arcade")


def _(msg):
    return str(msg)


def ngettext(n, msg1, msg2):
    return str(msg1) if n == 1 else str(msg2)


class Resources(BaseResources):
    def __init__(self, package):
        BaseResources.__init__(self, package, "res")
        self.req = package

    def resource_pil_image(self, resource):
        # resource_name = encode_path(u'res/' + resource_name)
        # return resource_pil_image(self.req, resource_name)
        stream = self.stream(resource)
        # noinspection PyUnresolvedReferences
        from PIL import Image

        return Image.open(stream)

    def resource_qt_image(self, resource):
        from fsui.qt import QImage

        stream = self.stream(resource)
        im = QImage()
        im.loadFromData(stream.read())
        return im

    def resource_stream(self, resource):
        return self.stream(resource)

    def resource_filename(self, resource):
        return self.path(resource)


gettext = _

resources = Resources("arcade")
