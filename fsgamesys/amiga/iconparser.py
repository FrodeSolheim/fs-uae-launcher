import traceback
from dataclasses import dataclass
from typing import List, Optional, Tuple

"""
Based on information from the following sources:
- http://krashan.ppa.pl/articles/amigaicons/
- http://www.evillabs.net/index.php/Amiga_Icon_Formats
"""


class IconParser:
    def __init__(self, data: bytes):
        self.error = 0
        self._data = data
        self.do_magic = 0
        self.do_version = 0
        self.do_gadget_width = 0
        self.do_gadget_height = 0
        self.do_gadget_flags = 0
        self.do_gadget_gadgetrender = 0
        self.do_gadget_selectrender = 0
        self.do_gadget_userdata = 0
        self.do_type = 0
        self.do_drawerdata = 0
        self.do_toolwindow = 0  # only applies to tools
        # self.do_stacksize = 0 # only applies to tools

        self.defaulttool = ""
        self.tooltypes: List[str] = []

        self.images: List[Optional[ImageInfo]] = [None, None]
        self.newicon_data: List[str] = []
        self.iff_chunks: List[Tuple[str, bytes]] = []
        self.png_images: List[bytes] = []

    def uint8(self, offset: int) -> int:
        return self._data[offset]

    def uint16(self, offset: int) -> int:
        return (self._data[offset] << 8) | (self._data[offset + 1])

    def uint32(self, offset: int) -> int:
        value = (
            (self._data[offset] << 24)
            | (self._data[offset + 1] << 16)
            | (self._data[offset + 2] << 8)
            | (self._data[offset + 3])
        )
        return value

    def read_bytes(self, offset: int, count: int):
        return self._data[offset : offset + count]

    def read_and_skip_string(self, offset: int):
        length = self.uint32(offset)
        # print("string length is 0x{:x}".format(length))
        if length == 0:
            return "", offset + 4 + length
        latin1_string = self._data[offset + 4 : offset + 4 + length]
        # print(repr(latin1_string))
        if latin1_string[-1] != 0:
            print(
                "WARNING: Not null-terminated string ({:02x})".format(
                    latin1_string[-1]
                )
            )
        string = latin1_string[:-1].decode("ISO-8859-1")
        return string, offset + 4 + length

    def parse(self):
        print("parse .info size", len(self._data))
        try:
            offset = self._parse()
        except (IndexError, AssertionError):
            traceback.print_exc()
            self.error = ERROR_EXCEPTION
            return
            # with open(os.path.expanduser("~/debug.info", "wb") as f:
            #     f.write(self._data)
            # sys.exit(1)

        print("Def. tool:", self.defaulttool)
        print("Tooltypes:", self.tooltypes)

        if offset != len(self._data):
            print("WARNING: {} bytes left".format(len(self._data) - offset))
            # sys.exit(1)

    def _parse_png(self, offset: int) -> int:
        offset += 2
        offset += 1
        offset += 1

        png_start = 0

        while offset != len(self._data):
            chunksize = self.uint32(offset)
            offset += 4
            header = self.uint32(offset)
            offset += 4
            chunktype = (
                chr((header >> 24) & 0xFF)
                + chr((header >> 16 & 0xFF))
                + chr((header >> 8) & 0xFF)
                + chr(header & 0xFF)
            )
            print("-------")
            print(chunktype, chunksize)
            print("-------")
            offset += chunksize
            offset += 4  # CRC

            if chunktype == "IEND":
                self.png_images.append(
                    self.read_bytes(png_start, offset - png_start)
                )
                png_start = offset
                if offset < len(self._data):
                    # Skip PNG header, assume we have a dual PNG icon
                    offset += 8
        return offset

    def _parse(self) -> int:
        offset = 0
        if len(self._data) < 4:
            print("WARNING: Not an icon file? No room for header magic")
            self.error = ERROR_DISKOBJECT
            return len(self._data)

        self.do_magic = self.uint16(offset)
        offset += 2
        self.do_version = self.uint16(offset)
        offset += 2

        if self.do_magic == 0x8950 and self.do_version == 0x4E47:
            # PNG
            return self._parse_png(offset)

        if self.do_magic != WB_DISKMAGIC:
            # raise Exception("Not an icon file? Missing WB_DISKMAGIC (0xe310)")
            print("WARNING: Not an icon file? Missing WB_DISKMAGIC (0xe310)")
            self.error = ERROR_MAGIC
            return len(self._data)
        if self.do_version != 1:
            # raise Exception("Not an icon file? Version is not 1")
            print("WARNING: Not an icon file? Version is not 1")
            self.error = ERROR_VERSION
            return len(self._data)

        if len(self._data) < 78:
            # raise Exception("Not an icon file? No room for DiskObject")
            print("WARNING: Not an icon file? No room for DiskObject")
            self.error = ERROR_DISKOBJECT
            return len(self._data)

        self.do_gadget_width = self.uint16(12)
        self.do_gadget_height = self.uint16(14)
        self.do_gadget_flags = self.uint16(16)

        self.do_gadget_gadgetrender = self.uint32(22)
        self.do_gadget_selectrender = self.uint32(26)

        self.do_gadget_userdata = self.uint32(44)
        print("USERDATA", self.do_gadget_userdata)
        print("USERDATA8", self.do_gadget_userdata & 0xFF)
        if self.do_gadget_userdata & 0xFF not in [0, 1]:
            print(
                "WARNING: Unrecognized gadget user data ({:02x})".format(
                    self.do_gadget_userdata & 0xFF
                )
            )

        self.do_type = self.uint8(48)
        # padding byte
        self.do_defaulttool = self.uint32(50)
        self.do_tooltypes = self.uint32(54)

        self.do_drawerdata = self.uint32(66)
        self.do_toolwindow = self.uint32(70)

        has_drawer_data = self.do_drawerdata != 0
        if self.do_type in [WBDISK, WBDRAWER, WBGARBAGE]:
            # FIXME: Necessary?
            has_drawer_data = True
        print(self.do_type, do_type_mapping.get(self.do_type, ""))
        print("has drawer data?", has_drawer_data)
        # has_image1 = self.do_gadget_flags & GFLG_GADGIMAGE
        # has_image2 = self.do_gadget_flags & GFLG_GADGHIMAGE
        # if self.do_gadget_flags & 0x0003 == 0x0002:
        #     # gadget highlight bits are set to 2
        #     has_image2 = True
        has_image1 = False
        has_image2 = False

        # start with end of DiskObject structure
        offset = 78
        if self.do_drawerdata or has_drawer_data:
            print("has drawer data, skipping 56 bytes")
            offset += 56
            print("offset is now", offset)
        if self.do_gadget_gadgetrender or has_image1:
            print("has image1, skipping")
            # offset0 = offset
            offset = self.skip_image(offset, 0)
            # self.imagedata = self.read_bytes(offset, )
            print("offset is now", offset)
        if self.do_gadget_selectrender or has_image2:
            print("has image2, skipping")
            offset = self.skip_image(offset, 1)
            print("offset is now", offset)

        print("offset after images:", offset, "size", len(self._data))
        print(
            self.do_defaulttool != 0,
            self.do_toolwindow != 0,
            self.do_tooltypes != 0,
        )

        if self.do_defaulttool:
            print("- has default tool")
            self.defaulttool, offset = self.read_and_skip_string(offset)

        print(
            "offset before reading tooltypes", offset, "size", len(self._data)
        )
        newicon_format = False

        if self.do_tooltypes:
            size = self.uint32(offset)
            count = (size >> 2) - 1
            print("size is", size, "count is", count)
            offset += 4
            for _ in range(count):
                string, offset = self.read_and_skip_string(offset)
                if string == "*** DON'T EDIT THE FOLLOWING LINES!! ***":
                    # "In a NewIcons file, one of the strings in the table (usually
                    # the first one) is a single space.  The next string is the
                    # message "*** DON'T EDIT THE FOLLOWING LINES!! ***". Later
                    # strings contain the NewIcons data..."
                    newicon_format = True
                    if len(self.tooltypes) > 1 and self.tooltypes[-1] == " ":
                        self.tooltypes.pop()
                    continue
                if newicon_format:
                    self.newicon_data.append(string)
                else:
                    self.tooltypes.append(string)

        if offset == len(self._data):
            # The icon sometimes end here even though drawer/userdata indicates
            # that a DrawerData2 struct should follow
            return offset

        print("do_drawerdata", self.do_drawerdata)
        print("do_gadget_userdata", self.do_gadget_userdata)
        if self.do_drawerdata and self.do_gadget_userdata & 0xFF:
            print("Skipping DrawerData2")
            offset += 6
        elif self.do_drawerdata and offset == len(self._data) - 6:
            print("Skipping DrawerData2 (not declared)")
            offset += 6

        # imagcount = 0

        if offset <= len(self._data) - 4:
            check = self.uint32(offset)
            if check == 0x464F524D:
                print('Found "FORM"')
                offset += 4
                form_size = self.uint32(offset)
                offset += 4
                form_end = offset + form_size
                identifier = self.uint32(offset)
                offset += 4
                print(f"{identifier:x}")
                # ICON
                assert identifier == 0x49434F4E

                while offset < form_end - 8:
                    print("offset", offset, "vs", form_end)
                    header = self.uint32(offset)
                    offset += 4
                    chunktype = (
                        chr((header >> 24) & 0xFF)
                        + chr((header >> 16 & 0xFF))
                        + chr((header >> 8) & 0xFF)
                        + chr(header & 0xFF)
                    )
                    print(chunktype)
                    # if chunktype == "IMAG":
                    #     imagcount += 1
                    #     if imagcount == 2:
                    #         assert False
                    #         import sys

                    #         sys.exit(1)
                    chunk_size = self.uint32(offset)
                    offset += 4
                    self.iff_chunks.append(
                        (chunktype, self.read_bytes(offset, chunk_size))
                    )
                    offset += chunk_size
                    if chunk_size % 2 == 1:
                        # Padding byte
                        offset += 1
                if offset != form_end:
                    print(
                        f"WARNING: FORM DID NOT END {offset} AT EXPECTED OFFSET {form_end}"
                    )
                offset = form_end

        if offset != len(self._data):
            print("WARNING: {} bytes left".format(len(self._data) - offset))
            raise IndexError("Remaining")

        return offset

    def skip_image(self, offset: int, image_index: int) -> int:
        width = self.uint16(offset + 4)
        height = self.uint16(offset + 6)
        bitdepth = self.uint16(offset + 8)
        has_imagedata = self.uint32(offset + 10)
        print("Size", width, "x", height, "bitdepth", bitdepth)
        # Skip to end of Image structure
        offset += 20
        if has_imagedata:
            # Plane rows are padded to 16-bit words
            pitch = ((width + 15) >> 4) << 1
            print("Pitch is", pitch)
            count = pitch * height * bitdepth
            imagedata = self.read_bytes(offset, count)
            offset += count
        else:
            imagedata = b""
        self.images[image_index] = ImageInfo(
            width=width, height=height, depth=bitdepth, data=imagedata
        )
        #     "width": width,
        #     "height": height,
        #     "bitdepth": bitdepth,
        #     "data": imagedata,
        # }
        return offset


@dataclass
class ImageInfo:
    width: int
    height: int
    depth: int
    data: bytes

    def __getitem__(self, key: str):
        """Deprecated, for compatibility with older code."""
        if key == "width":
            return self.width
        elif key == "height":
            return self.height
        elif key == "bitdepth":
            return self.depth
        elif key == "data":
            return self.data
        raise KeyError(key)


WB_DISKMAGIC = 0xE310

WBDISK = 1
WBDRAWER = 2
WBTOOL = 3
WBPROJECT = 4
WBGARBAGE = 5
WBDEVICE = 6
WBKICK = 7
WBAPPICON = 8

GFLG_GADGHIMAGE = 1 << 1
# GFLG_GADGHNONE = 0x0003
# GFLG_GADGHIGHBITS = 0x0003
GFLG_GADGIMAGE = 1 << 2

ERROR_EXCEPTION = 1
ERROR_DISKOBJECT = 2
ERROR_MAGIC = 3
ERROR_VERSION = 4

do_type_mapping = {
    WBDISK: "WBDISK",
    WBDRAWER: "WBDRAWER",
    WBTOOL: "WBTOOL",
    WBPROJECT: "WBPROJECT",
    WBGARBAGE: "WBGARBAGE",
    WBDEVICE: "WBDEVICE",
    WBKICK: "WBKICK",
    WBAPPICON: "WBAPPICON",
}
