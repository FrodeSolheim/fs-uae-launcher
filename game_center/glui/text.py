class TextRenderer(object):

    def __init__(self, font):
        self.font = font

    def render_text(self, text, color):
        data, size = self.font.render(text, True, color)

        # swap channels

        # a = numpy.fromstring(data, dtype=numpy.uint8)
        # temp = numpy.array(a[0::4])
        # a[0::4] = numpy.array(a[2::4])
        # a[2::4] = temp
        # return a.tostring(), size

        # edit: no need to swap channels when using GL_BGRA for pixel format

        return data, size

    def get_size(self, text):
        return self.font.rendered_size(text)
