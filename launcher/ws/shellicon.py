import zlib

from fsgamesys.amiga.iconparser import IconParser
from fsui import Image


# FIXME: Add support for GlowIcons with palette data ONLY in the first image
# FIXME: When scaling icons to 150%, maybe a transparent row and/or column to
# make the icon size a multiple of two before scaling - could give slightly
# crisper result?


class ShellIconImage(Image):
    def __init__(self, qimage):
        from fsui.qt import Qt

        height = qimage.height()
        if height <= 46:
            width = qimage.width()
            width = int(width * 1.5)
            height = int(height * 1.5)
            qimage = qimage.scaled(
                width, height, transformMode=Qt.SmoothTransformation
            )
        super().__init__(qimage=qimage)


class ShellIcon:
    def __init__(self, path):
        self.parser = IconParser(open(path, "rb").read())
        self.parser.parse()

    def defaulttool(self):
        return self.parser.defaulttool

    def tooltypes(self):
        return self.parser.tooltypes

    def normal_image(self):
        if self.parser.png_images:
            return self._pngicon_image(0)
        if self.parser.iff_chunks:
            return self._glowicon_image(0)
        if self.parser.newicon_data:
            return self._newicon_image(0)
        return self._image(self.parser.images[0])

    def selected_image(self):
        if self.parser.png_images:
            return self._pngicon_image(1)
        if self.parser.iff_chunks:
            return self._glowicon_image(1)
        if self.parser.newicon_data:
            return self._newicon_image(1)
        return self._image(self.parser.images[1])

    def _missing_icon(self):
        from fsui.qt import QImage, QSize

        return Image(qimage=QImage(QSize(1, 1), QImage.Format_RGBA8888))

    def _image(self, info):
        from fsui.qt import QColor, QImage, QPoint, QSize

        # width = self.uint16(offset + 4)
        # height = self.uint16(offset + 6)
        # bitdepth = self.uint16(offset + 8)
        # has_imagedata = self.uint32(offset + 10)

        if not "width" in info:
            return self._missing_icon()

        width = info["width"]
        height = info["height"]
        bitdepth = info["bitdepth"]
        data = info["data"]

        pitch = ((width + 15) >> 4) << 1
        planebytesize = pitch * height
        planes = []
        for i in range(bitdepth):
            planes.append(data[planebytesize * i : planebytesize * (i + 1)])

        height_factor = 1
        image = QImage(
            QSize(width, height * height_factor), QImage.Format_RGBA8888
        )

        # image.fill(0xFFFFFFFF)

        for y in range(height):
            for x in range(width):
                value = 0
                bytenum = y * pitch + x // 8
                bitnum = 7 - x % 8
                for plane in range(bitdepth):
                    value = (
                        value | (planes[plane][bytenum] >> bitnum & 1) << plane
                    )
                a = 0xFF
                if value == 0:
                    rgb = 0x959595
                    a = 0x00
                elif value == 1:
                    rgb = 0x000000
                elif value == 2:
                    rgb = 0xFFFFFF
                elif value == 3:
                    rgb = 0x3B67A2
                elif value == 4:
                    rgb = 0x7B7B7B
                elif value == 5:
                    rgb = 0xAFAFAF
                elif value == 6:
                    rgb = 0xAA907C
                elif value == 7:
                    rgb = 0xFFA997
                else:
                    # raise Exception("Unsupported color")
                    print(value)
                    color = 0xFF0000
                color = QColor(rgb >> 16, (rgb >> 8) & 0xFF, rgb & 0xFF, a)
                # if height_factor == 2:
                #     image.setPixelColor(QPoint(x, y * 2), color)
                #     image.setPixelColor(QPoint(x, y * 2 + 1), color)
                # else:
                image.setPixelColor(QPoint(x, y), color)

        return ShellIconImage(image)

    def _linedata_for_index(self, index):
        linedata = []
        for line in self.parser.newicon_data:
            linestart = "IM2=" if index == 1 else "IM1="
            if line.startswith(linestart):
                print(len(line))
                linedata.append(line[4:].encode("ISO-8859-1"))
        return linedata

    def _newicon_image(self, index):
        from fsui.qt import QColor, QImage, QPoint, QSize

        linedata = self._linedata_for_index(index)
        dark = False
        if not linedata:
            if index == 1:
                dark = True
                linedata = self._linedata_for_index(0)
            if not linedata:
                return self._missing_icon()

        # line = strdata[0].encode("ISO-8859-1")
        line = linedata[0]
        if line[0:1] not in [b"B", b"C"]:
            print("WARNING: Newion data does not start with B or C")
        transparency = line[0:1] == b"B"
        width = line[1] - 0x21
        height = line[2] - 0x21
        colors = ((line[3] - 0x21) << 6) + (line[4] - 0x21)
        bitdepth = 1
        while 2 ** bitdepth < colors:
            bitdepth += 1
        print("colors", colors, "=> bitdepth", bitdepth)

        print(width, height, transparency, colors)

        image = QImage(QSize(width, height), QImage.Format_RGBA8888)

        # image.fill(0xFFFFFFFF)

        palette = []

        # offset = 5
        # for i in range(colors):
        #     r = line[offset]
        #     g = line[offset + 1]
        #     b = line[offset + 2]
        #     a = 0xFF
        #     palette.append(QColor(r, g, b, a))
        #     offset += 3
        # print(len(line), "vs", offset)

        # parser = []
        # ly = 0
        # lx = 5

        class ParseData:
            bits = []
            ly = 0
            ly = 0
            line = b""
            palette = True
            color = []
            done = False
            x = 0
            y = 0

        parsedata = ParseData()
        parsedata.ly = 0
        parsedata.lx = 5
        parsedata.line = line

        def pushbit(bit):
            parsedata.bits.append(bit)
            if parsedata.palette:
                if len(parsedata.bits) == 8:
                    # parsedata.color.append(bits_to_value(parsedata.bits[0:8]))
                    parsedata.color.append(bits_to_value(parsedata.bits))
                    # r = bits_to_value(parsedata.bits[0:8])
                    # g = bits_to_value(parsedata.bits[8:16])
                    # b = bits_to_value(parsedata.bits[16:24])
                    if len(parsedata.color) == 3:
                        # pylint: disable=unbalanced-tuple-unpacking
                        r, g, b = parsedata.color
                        a = 0xFF
                        print(
                            f"PALETTE{len(palette):02d} 0x{r:02x}{g:02x}{b:02x}"
                        )
                        if dark:
                            palette.append(
                                QColor(r * 0.67, g * 0.67, b * 0.67, a)
                            )
                        else:
                            palette.append(QColor(r, g, b, a))
                        parsedata.color = []
                    # FIXME: More efficient
                    # parsedata.bits = parsedata.bits[8:]
                    parsedata.bits.clear()

                    # if parsedata.palette and len(palette) >= colors:
                    #     parsedata.palette = False
            elif parsedata.done:
                pass
            else:
                if len(parsedata.bits) == bitdepth:
                    # palette_index = bits_to_value(parsedata.bits[0:bitdepth])
                    palette_index = bits_to_value(parsedata.bits)
                    # FIXME: Maybe only subtract 1 etc when transparency is True
                    # print("palette", palette_index)
                    # FIXME: Transparency... correct?
                    if palette_index == 0 and transparency:
                        color = QColor(0x00, 0x00, 0x00, 0x00)
                    elif palette_index >= len(palette):
                        color = QColor(0xFF, 0x00, 0x00, 0xFF)
                        print("WARNING, palette_index is", palette_index)
                    else:
                        color = palette[palette_index]
                    image.setPixelColor(
                        QPoint(parsedata.x, parsedata.y), color
                    )
                    # FIXME: More efficient
                    # parsedata.bits = parsedata.bits[bitdepth:]
                    parsedata.bits.clear()
                    parsedata.x += 1
                    if parsedata.x == width:
                        parsedata.y += 1
                        parsedata.x = 0
                        if parsedata.y == height:
                            parsedata.done = True

        def flush():
            print("flushing", len(parsedata.bits), "bits")
            parsedata.bits.clear()

        def dobyte():
            val = parsedata.line[parsedata.lx]
            # print(f"in 0x{val:x}")
            val2 = 0
            if val >= 0x20 and val <= 0x6F:
                val2 = val - 0x20
                for i in range(7):
                    pushbit(val2 >> (6 - i) & 1)
            elif val >= 0xA1 and val <= 0xD0:
                val2 = val - 0xA1 + 0x50
                for i in range(7):
                    pushbit(val2 >> (6 - i) & 1)
            elif val >= 0xD1:
                rle = val - 0xD0
                for i in range(rle):
                    for j in range(7):
                        pushbit(0)
                # print("???")
                pass
            else:
                raise Exception("Unexpected newicon byte")
            parsedata.lx += 1
            # print("lx is now", parsedata.lx)
            if parsedata.lx == len(parsedata.line):
                flush()
                parsedata.lx = 0
                parsedata.ly += 1
                if parsedata.ly < len(linedata):
                    parsedata.line = linedata[parsedata.ly]
                else:
                    # We are done
                    parsedata.line = None

                if parsedata.palette and len(palette) >= colors:
                    print("Done parsing palette")
                    if len(palette) > colors:
                        print("WARNING: More colors than expected??")
                    parsedata.palette = False

        # while parsedata.lx < len(parsedata.line):
        #     dobyte()
        while parsedata.ly < len(linedata) and parsedata.lx < len(
            parsedata.line
        ):
            dobyte()
        print(len(parsedata.bits))

        print("x", parsedata.x, "y", parsedata.y)
        if parsedata != height and parsedata.x != 0:
            print("WARNING: Did not decode image according to size")
        # assert parsedata.y == height
        # assert parsedata.x == 0

        # import sys
        # sys.exit(1)

        # pixels = []
        # ly = 1
        # lx = 0
        # line = linedata[ly]
        # while True:
        #     val = line[lx]
        #     val2 = 0
        #     if val >= 0x20 and val <= 0x6F:
        #         val2 = val - 0x20
        #     elif val >= 0xA1 and val <= 0xD0:
        #         val2 = val - 0xA1 + 0x50
        #     else:
        #         print(f"0x{val:x}")
        #         raise Exception("???")

        # for y in range(height):
        #     for x in range(width):
        #         # image.setPixelColor(QPoint(x, y * 2 + 1), color)
        #         pass

        # import sys
        # sys.exit(1)

        return ShellIconImage(image)

    def _glowicon_image(self, index):
        facedata = b""
        imagedata = b""
        imagetype = ""
        # If index is 1 (second image) and we find a second icon in the file,
        # then we set dark to False.
        dark = index == 1
        for chunktype, chunkdata in self.parser.iff_chunks:
            if chunktype == "FACE":
                facedata = chunkdata
            elif chunktype == "ARGB":
                if index == 0:
                    if not imagedata:
                        imagetype = chunktype
                        imagedata = chunkdata
                else:
                    if imagedata:
                        dark = False
                    imagetype = chunktype
                    imagedata = chunkdata
            elif chunktype == "IMAG":
                if index == 0:
                    if not imagedata:
                        imagetype = chunktype
                        imagedata = chunkdata
                else:
                    if imagedata:
                        dark = False
                    imagetype = chunktype
                    imagedata = chunkdata
        if not facedata:
            print("WARNING: Missing facedata")
            return self._missing_icon()

        # 0x00 UBYTE[4] fc_Header      set to "FACE"
        # 0x04 ULONG    fc_Size        size [excluding the first 8 bytes!]
        # 0x08 UBYTE    fc_Width       icon width subtracted by 1
        # 0x09 UBYTE    fc_Height      icon height subtracted by 1
        # 0x0A UBYTE    fc_Flags       flags
        #      bit 0                   icon is frameless
        # 0x0B UBYTE    fc_Aspect      image aspect ratio:
        #      upper 4 bits            x aspect
        #      lower 4 bits            y aspect
        # 0x0C UWORD    fc_MaxPalBytes maximum number of bytes used in image palettes
        #                              subtracted by 1 (i.e. if palette 1 has 17 and
        #                              palette 2 has 45 entries, then this is 45)

        width = facedata[0] + 1
        height = facedata[1] + 1
        _flags = facedata[2]
        _aspect = facedata[3]
        maxpalbytes = facedata[5] + 1
        print("width", width, "height", height, "maxpalbytes", maxpalbytes)

        if imagetype == "ARGB":
            return self._glowicon_image_argb(imagedata, width, height, dark)
        elif imagetype == "IMAG":
            return self._glowicon_image_imag(imagedata, width, height, dark)
        else:
            return self._missing_icon()

    def _glowicon_image_imag(self, data, width, height, dark):
        from fsui.qt import QColor, QImage, QPoint, QSize

        transparent_color = data[0]
        num_colors = data[1] + 1
        flags = data[2]
        transparency = flags & 1 != 0
        has_palette = flags & 2 != 0
        compressed = data[3] != 0
        compressed_palette = data[4] != 0
        bitdepth = data[5]
        image_bytes = data[6] * 256 + data[7] + 1
        palette_bytes = data[8] * 256 + data[9] + 1

        print("transparent_color:", transparent_color)
        print("num colors:", num_colors)
        print("flags:", flags)
        print("- transparency:", transparency)
        print("- has_palette:", has_palette)
        print("compression:", compressed)
        print("palette compression:", compressed_palette)
        print("bit depth:", bitdepth)
        print("image bytes:", image_bytes)
        print("palette bytes:", palette_bytes)

        if not transparency:
            transparent_color = -1

        image = QImage(QSize(width, height), QImage.Format_RGBA8888)
        image.fill(0xFFFFFFFF)

        palette = []

        class ParseData:
            bits = []
            bitdepth = 0
            offset = 0
            # line = b""
            palette = True
            compressed = False
            color = []
            done = False
            x = 0
            y = 0
            copy = 0
            produce = 0

        parsedata = ParseData()
        parsedata.offset = 10 + image_bytes
        parsedata.end = 10 + image_bytes + palette_bytes
        parsedata.compressed = compressed_palette
        parsedata.palette = True
        parsedata.bitdepth = 8

        # parsedata.data = data
        # parsedata.ly = 0
        # parsedata.lx = 5
        # parsedata.line = line

        def pushentry(value):
            if parsedata.palette:
                parsedata.color.append(value)
                if len(parsedata.color) == 3:
                    # pylint: disable=unbalanced-tuple-unpacking
                    r, g, b = parsedata.color
                    a = 0xFF
                    print(f"PALETTE{len(palette):02d} 0x{r:02x}{g:02x}{b:02x}")
                    if dark:
                        palette.append(QColor(r * 0.66, g * 0.66, b * 0.66, a))
                    else:
                        palette.append(QColor(r, g, b, a))
                    parsedata.color = []
                # FIXME: More efficient
                # parsedata.bits = parsedata.bits[8:]
                if parsedata.palette and len(palette) >= num_colors:
                    parsedata.palette = False
            elif parsedata.done:
                pass
            else:
                palette_index = value
                # FIXME: Maybe only subtract 1 etc when transparency is True
                # print("palette", palette_index)
                # FIXME: Transparency... correct?
                if palette_index == transparent_color:
                    color = QColor(0x00, 0x00, 0x00, 0x00)
                elif palette_index >= len(palette):
                    color = QColor(0xFF, 0x00, 0x00, 0xFF)
                    print("WARNING, palette_index is", palette_index)
                else:
                    color = palette[palette_index]
                image.setPixelColor(QPoint(parsedata.x, parsedata.y), color)
                # FIXME: More efficient
                # parsedata.bits = parsedata.bits[bitdepth:]
                parsedata.x += 1
                if parsedata.x == width:
                    parsedata.y += 1
                    parsedata.x = 0
                    if parsedata.y == height:
                        parsedata.done = True

        def pushbit(bit):
            parsedata.bits.append(bit)

            if parsedata.produce:
                if len(parsedata.bits) == parsedata.bitdepth:
                    value = bits_to_value(parsedata.bits)
                    for _i in range(parsedata.produce):
                        pushentry(value)
                    parsedata.produce = 0
                    parsedata.bits.clear()

            elif parsedata.copy:
                if len(parsedata.bits) == parsedata.bitdepth:
                    pushentry(bits_to_value(parsedata.bits))
                    parsedata.copy -= 1
                    parsedata.bits.clear()

            elif parsedata.compressed:
                if len(parsedata.bits) == 8:
                    value = bits_to_value(parsedata.bits)
                    if value <= 0x7F:
                        parsedata.copy = value + 1
                    elif value == 0x80:
                        pass
                    else:
                        parsedata.produce = 256 - value + 1
                    parsedata.bits.clear()

            else:
                if len(parsedata.bits) == 8:
                    value = bits_to_value(parsedata.bits[: parsedata.bitdepth])
                    pushentry(value)
                    parsedata.bits.clear()

            # if parsedata.palette:
            #     if len(parsedata.bits) == 8:
            #         parsedata.color.append(bits_to_value(parsedata.bits[0:8]))
            #         if len(parsedata.color) == 3:
            #             # pylint: disable=unbalanced-tuple-unpacking
            #             r, g, b = parsedata.color
            #             a = 0xFF
            #             print(
            #                 f"PALETTE{len(palette):02d} 0x{r:02x}{g:02x}{b:02x}"
            #             )
            #             if dark:
            #                 palette.append(
            #                     QColor(r * 0.66, g * 0.66, b * 0.66, a)
            #                 )
            #             else:
            #                 palette.append(QColor(r, g, b, a))
            #             parsedata.color = []
            #         # FIXME: More efficient
            #         parsedata.bits = parsedata.bits[8:]

            #         if parsedata.palette and len(palette) >= num_colors:
            #             parsedata.palette = False
            # elif parsedata.done:
            #     pass
            # else:
            #     # print("x")
            #     if len(parsedata.bits) == bitdepth:
            #         palette_index = bits_to_value(parsedata.bits[0:bitdepth])
            #         # FIXME: Maybe only subtract 1 etc when transparency is True
            #         # print("palette", palette_index)
            #         # FIXME: Transparency... correct?
            #         if palette_index == 0 and transparency:
            #             color = QColor(0x00, 0x00, 0x00, 0x00)
            #         elif palette_index >= len(palette):
            #             color = QColor(0xFF, 0x00, 0x00, 0xFF)
            #             print("WARNING, palette_index is", palette_index)
            #         else:
            #             color = palette[palette_index]
            #         image.setPixelColor(
            #             QPoint(parsedata.x, parsedata.y), color
            #         )
            #         # FIXME: More efficient
            #         parsedata.bits = parsedata.bits[bitdepth:]
            #         parsedata.x += 1
            #         if parsedata.x == width:
            #             parsedata.y += 1
            #             parsedata.x = 0
            #             if parsedata.y == height:
            #                 parsedata.done = True

        def pushbyte(value):
            for i in range(8):
                pushbit(value >> (7 - i) & 1)

        # def flush():
        #     print("flushing", len(parsedata.bits), "bits")
        #     parsedata.bits = []

        def dobyte():
            value = data[parsedata.offset]
            # if parsedata.compressed:
            #     # 0x00 .. 0x7F copy the next n entries as they are, where n is "RLE-value"+1
            #     # 0x80         ignore this, do nothing
            #     # 0x81 .. 0xFF produce the next entry n times, where n is 256-"RLE-value"+1
            #     #             (if using signed chars n is "RLE-value"+1)
            #     if parsedata.produce:
            #         for _i in range(parsedata.produce):
            #             pushbyte(value)
            #         parsedata.produce = 0
            #     elif parsedata.copy:
            #         pushbyte(value)
            #         parsedata.copy -= 1
            #     elif value <= 0x7F:
            #         parsedata.copy = value + 1
            #     elif value == 0x80:
            #         pass
            #     else:
            #         parsedata.produce = 256 - value + 1
            # else:
            #     if not parsedata.palette and not parsedata.compressed:
            #         # FIXME: Only push bitdepth bits
            #         raise Exception("TODO: Unsupported")
            #     else:
            #         pushbyte(value)

            pushbyte(value)
            parsedata.offset += 1

        while parsedata.offset < parsedata.end:
            dobyte()
        print(len(parsedata.bits))

        parsedata.offset = 10
        parsedata.end = 10 + image_bytes
        parsedata.compressed = compressed
        parsedata.palette = False
        parsedata.copy = 0
        parsedata.produce = 0
        parsedata.bitdepth = bitdepth

        print(parsedata.offset, parsedata.end)
        while parsedata.offset < parsedata.end:
            dobyte()

        print(width, height)
        print(parsedata.x, parsedata.y)

        # import sys
        # sys.exit(1)
        return ShellIconImage(image)

    def _glowicon_image_argb(self, imagedata, width, height, dark):
        from fsui.qt import QColor, QImage, QPoint, QSize

        # print(repr(imagedata[:16]))
        # print(len(imagedata))

        zlibdata = imagedata[10:]
        data = zlib.decompress(zlibdata)
        offset = 0

        image = QImage(QSize(width, height), QImage.Format_RGBA8888)
        for y in range(height):
            for x in range(width):
                color = QColor(
                    data[offset + 1],
                    data[offset + 2],
                    data[offset + 3],
                    data[offset + 0],
                )
                image.setPixelColor(QPoint(x, y), color)
                offset += 4

        if dark:
            print("FIXME: Make dark version")

        return ShellIconImage(image)

    def _pngicon_image(self, index):
        print("_pngicon_image", index)
        from fsui.qt import QImage, QPoint

        dark = False
        if index == 1 and len(self.parser.png_images) == 1:
            data = self.parser.png_images[0]
            dark = True
        elif index < len(self.parser.png_images):
            data = self.parser.png_images[index]
        else:
            return self._missing_icon()
        image = QImage()
        # print("load from data", data)
        image.loadFromData(data, "PNG")
        print(image.size().width(), image.size().height())
        # FIXME: dark
        if dark:
            for y in range(image.height()):
                for x in range(image.width()):
                    point = QPoint(x, y)
                    color = image.pixelColor(point)
                    color.setRed(color.red() * 0.67)
                    color.setGreen(color.green() * 0.67)
                    color.setBlue(color.blue() * 0.67)
                    image.setPixelColor(point, color)

        return ShellIconImage(image)


def bits_to_value(bits):
    value = 0
    for i, bit in enumerate(reversed(bits)):
        value = value | bit << i
    return value
