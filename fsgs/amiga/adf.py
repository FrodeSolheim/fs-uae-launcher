from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import hashlib
from io import BytesIO


BSIZE = 512
BCOUNT = 880 * 2

T_HEADER = 2
T_DATA = 8
T_LIST = 16
ST_ROOT = 1
ST_USERDIR = 2
ST_FILE = 0xffffffff - 3 + 1


def char(block, pos):
    return block[pos:pos + 1].decode("ISO-8859-1")


def ubyte(block, pos):
    #return ord(block[pos])
    return block[pos]


def ulong(block, pos):
    # a = ord(block[pos])
    # b = ord(block[pos + 1])
    # c = ord(block[pos + 2])
    # d = ord(block[pos + 3])
    a = block[pos]
    b = block[pos + 1]
    c = block[pos + 2]
    d = block[pos + 3]
    return (a << 24) | (b << 16) | (c << 8) | d


def checksum_block(block):
    # clear checksum field
    data = block[:20] + b"\0\0\0\0" + block[24:]
    sum = 0
    for pos in range(0, BSIZE, 4):
        sum += ulong(data, pos)
        sum &= 0xffffffff
    sum = -sum
    sum &= 0xffffffff
    return sum


def verify_block(data):
    sum = 0
    for pos in range(0, BSIZE, 4):
        sum += ulong(data, pos)
        sum &= 0xffffffff
    return sum == 0


class Block(object):

    def __init__(self, data):
        self.data = data

    def char(self, pos):
        return char(self.data, pos)

    def string(self, pos, len):
        #return self.data[pos:pos + len]
        return self.data[pos:pos + len].decode("ISO-8859-1")

    def ubyte(self, pos):
        return ubyte(self.data, pos)

    def ulong(self, pos):
        return ulong(self.data, pos)


class FileInfo(object):

    def __init__(self):
        self.block_list = []


class ADFFile(object):

    FFS_FLAG = 1
    INTL_ONLY_FLAG = 2
    DIRC_AND_INTL_FLAG = 4

    def __init__(self, stream_or_data_or_file):
        if hasattr(stream_or_data_or_file, "read"):
            data = stream_or_data_or_file.read()
        elif len(stream_or_data_or_file) == BSIZE * BCOUNT:
            data = stream_or_data_or_file
        else:
            with open(stream_or_data_or_file, "rb") as f:
                data = f.read()
        # print(len(data))
        assert len(data) == BSIZE * BCOUNT
        self.blocks = []
        for i in range(0, BSIZE * BCOUNT, BSIZE):
            self.blocks.append(Block(data[i:i + BSIZE]))
        assert len(self.blocks) == BCOUNT
        self.block_usage = [[] for _ in range(BCOUNT)]
        self.dos = False
        self.ofs = False
        self.ffs = False
        self.warnings = []
        self.file_map = {}
        self.root_block_number = 880
        self.bitmap_pages = []
        self._parse()

    def root_block(self):
        return self.blocks[self.root_block_number]

    def _parse(self):
        b = self.blocks[0]
        #if b.char(0) == "D" and b.char(1) == "O" and b.char(2) == "S":
        if b.char(0) == "D" and b.char(1) == "O" and b.char(2) == "S":
            self.dos = True
        else:
            return
        flags = b.ubyte(3)
        self.ffs = flags & self.FFS_FLAG
        self.ofs = not self.ffs

        self.root_block_number = b.ulong(8)
        self.bitmap_pages = []
        if self.root_block_number != 880:
            self.warnings.append("Root block is at position {0}, "
                                 "not 880".format(self.root_block_number))
            self.root_block_number = 880
            self.warnings.append("Trying 880 anyway...")

        self._parse_root_block()
        self.block_usage[self.root_block_number].append("root block")

        for i, usage in enumerate(self.block_usage):
            if "used" in usage:
                if len(usage) < 2:
                    self.warnings.append(
                        "block {0} marked as used but no actual usage".format(
                            i))
            if "free" in usage:
                if len(usage) != 1:
                    self.warnings.append(
                        "block {0} marked as used but used for {1}".format(
                            i, repr(usage)))

    def _parse_root_block(self):
        b = self.root_block()
        type = b.ulong(0)
        secondary_type = b.ulong(BSIZE - 4)
        #assert type == T_HEADER
        if type != T_HEADER:
            self.warnings.append("root block does not have T_HEADER type")
        #assert secondary_type == ST_ROOT
        if secondary_type != ST_ROOT:
            self.warnings.append("root block does not have ST_ROOT secondary "
                                 "type")

        days = b.ulong(BSIZE - 92)
        mins = b.ulong(BSIZE - 88)
        ticks = b.ulong(BSIZE - 84)
        self.root_mtime = "{0:05d}:{1:04d}:{2:03d}".format(days, mins, ticks)

        days = b.ulong(BSIZE - 40)
        mins = b.ulong(BSIZE - 36)
        ticks = b.ulong(BSIZE - 32)
        self.disk_mtime = "{0:05d}:{1:04d}:{2:03d}".format(days, mins, ticks)

        days = b.ulong(BSIZE - 28)
        mins = b.ulong(BSIZE - 24)
        ticks = b.ulong(BSIZE - 20)
        self.disk_ctime = "{0:05d}:{1:04d}:{2:03d}".format(days, mins, ticks)

        bm_flag = b.ulong(BSIZE - 200)
        if bm_flag != 0xffffffff:
            self.warnings.append("bm_flag != 0xffffffff ({0:8x})".format(
                bm_flag))
            if bm_flag == 0:
                self.warnings.append("bm_flag is ZERO")
        for i in range(25):
            self.bitmap_pages.append(b.ulong(BSIZE - 196 + 4 * i))
        self._parse_used_blocks()

        name_len = b.ubyte(BSIZE - 80)
        self.volume_name = b.string(BSIZE - 79, name_len)
        #self.volume_name = self.volume_name.decode("ISO-8859-1")
        self._parse_directory_content("", self.root_block_number)
        if not verify_block(b.data):
            self.warnings.append("bad root checksum")

    def _parse_used_blocks(self):
        for i in range(len(self.bitmap_pages)):
            block_number = self.bitmap_pages[i]
            if block_number:
                if block_number >= BCOUNT:
                    self.warnings.append(
                        "invalid block number {0} in bitmap pages".format(
                            block_number))
                    continue
                self.block_usage[block_number].append("bitmap block")

            if i == 0:
                if not block_number:
                    self.warnings.append("no bitmap block for disk")
                    continue
            else:
                if block_number:
                    self.warnings.append(
                        "unexpected additional bitmap block...")
                continue

            b = self.blocks[block_number]
            if not verify_block(b.data):
                self.warnings.append("bitmap block checksum is invalid ("
                                     "ignoring this block)")
                continue
            for bit_index in range(1758):
                long_index = bit_index // 32
                bit = bit_index % 32
                ul = b.ulong(4 + long_index * 4)
                free = ul & (1 << bit)
                if free:
                    self.block_usage[2 + bit_index].append("free")
                else:
                    self.block_usage[2 + bit_index].append("used")

    def _parse_directory_content(self, path, block_number):
        d_b = self.blocks[block_number]
        d_secondary_type = d_b.ulong(BSIZE - 4)
        if d_secondary_type == ST_ROOT:
            ht_size = d_b.ulong(12)
            assert ht_size == (BSIZE // 4) - 56

        for i in range((BSIZE // 4) - 56):
            entry = d_b.ulong(24 + i * 4)
            while entry:
                #print(entry)
                if entry >= BCOUNT:
                    self.warnings.append(
                        "directory entry referes to an invalid block "
                        "number {0}".format(entry))
                    entry = 0
                    continue
                b = self.blocks[entry]
                type = b.ulong(0)
                secondary_type = b.ulong(BSIZE - 4)
                parent = b.ulong(BSIZE - 12)
                assert type == T_HEADER
                assert secondary_type in [ST_USERDIR, ST_FILE]
                assert parent == block_number

                if secondary_type == ST_USERDIR:
                    self._parse_directory(path, entry)
                elif secondary_type == ST_FILE:
                    self._parse_file(path, entry)
                else:
                    raise Exception("neither ST_USERDIR or ST_FILE")

                entry = b.ulong(BSIZE - 16)

    def _parse_file(self, path, block_number):
        b = self.blocks[block_number]
        header_key = b.ulong(4)
        assert header_key == block_number

        file_info = FileInfo()
        file_info.header_block = block_number

        name_len = b.ubyte(BSIZE - 80)
        file_info.name = b.string(BSIZE - 79, name_len)
        #file_info.name = file_info.name.decode("ISO-8859-1")
        file_info.path = path + file_info.name
        # print(file_info.path)
        file_key = file_info.path.lower()
        if file_key in self.file_map:
            self.warnings.append("duplicate entries for file name "
                                 "{0}".format(file_key))
        self.file_map[file_key] = file_info

        self.block_usage[block_number].append(
            "header block for file " + file_info.path)
        if not verify_block(b.data):
            self.warnings.append("bad checksum for header for " +
                                 file_info.path)

        file_info.mode = b.ulong(BSIZE - 192)
        file_info.size = b.ulong(BSIZE - 188)
        comment_len = b.ubyte(BSIZE - 184)
        file_info.comment = b.string(BSIZE - 183, comment_len)

        days = b.ulong(BSIZE - 92)
        mins = b.ulong(BSIZE - 88)
        ticks = b.ulong(BSIZE - 84)
        file_info.time = "{0:05d}:{1:04d}:{2:03d}".format(days, mins, ticks)

        first_data = b.ulong(16)
        next_data = first_data
        file_blocks_1 = []
        ofs_accum_size = 0
        k = 0

        while next_data and self.ofs:
            file_blocks_1.append(next_data)
            data_b = self.blocks[next_data]
            data_type = data_b.ulong(0)
            assert data_type == T_DATA
            header_key = data_b.ulong(4)
            if header_key != block_number:
                self.warnings.append("header_key != block_number")

            seq_num = data_b.ulong(8)
            if seq_num != len(file_blocks_1):
                self.warnings.append(
                    "block {0:04d} expected seq_num {1} (found {2}) for "
                    "file {3}".format(next_data, len(file_blocks_1), seq_num,
                                      file_info.path))
            data_size = data_b.ulong(12)
            ofs_accum_size += data_size

            if not verify_block(data_b.data):
                self.warnings.append(
                    "block {1:04d} - bad checksum for data block #{0} for "
                    "file {2}".format(k + 1, next_data, file_info.path))
            # self.block_usage[next_data].append(
            #     "block {2:04d} - data block #{0} for file {1}".format(
            #         k + 1, file_info.path, next_data))

            next_data = data_b.ulong(16)
            k += 1

        file_blocks_2 = []
        extension = block_number
        k = 0
        while extension:
            ext_b = self.blocks[extension]
            ext_type = ext_b.ulong(0)
            ext_secondary_type = ext_b.ulong(BSIZE - 4)
            if extension != block_number:
                assert ext_type == T_LIST
            assert ext_secondary_type == ST_FILE
            high_seq = ext_b.ulong(8)
            for i in range(high_seq):
                file_blocks_2.append(ext_b.ulong(BSIZE - 204 - i * 4))

            parent = ext_b.ulong(BSIZE - 12)
            if k > 0 and parent != block_number:
                self.warnings.append(
                    "block {3:04d} - expected parent {0} (found {1} for OFS "
                    "extension block #{2} for file {4}".format(
                        block_number, parent, k, extension,
                        file_info.path))

            if not verify_block(ext_b.data):
                self.warnings.append(
                    "block {2:04d} - bad checksum for extension block #{0} "
                    "for file {1}".format(k, file_info.path, extension))
            extension = ext_b.ulong(BSIZE - 8)
            if extension:
                self.block_usage[extension].append(
                    "file extension block #{0} for file {1}".format(
                        k, file_info.path))
            k += 1

        if self.ofs:
            if file_blocks_1 != file_blocks_2:
                self.warnings.append(
                    "block list mismatch (extension vs OFS headers) for "
                    "file {0}".format(file_info.path))
            if len(file_blocks_1) != len(file_blocks_2):
                self.warnings.append(
                    "block list length mismatch (extension {0} vs OFS "
                    "headers {1}) for file {2}".format(len(file_blocks_2),
                    len(file_blocks_1), file_info.path))
            if ofs_accum_size != file_info.size:
                self.warnings.append(
                    "file size mismatch (file header {0} vs OFS data block "
                    "headers {1}) for file {2}".format(
                        file_info.size, ofs_accum_size, file_info.path))

        file_info.block_list = file_blocks_2

        for i, bn in enumerate(file_blocks_2):
            self.block_usage[bn].append(
                "data block #{0} for file {1}".format(
                    i + 1, file_info.path, bn))

    def _parse_directory(self, path, block_number):
        b = self.blocks[block_number]
        header_key = b.ulong(4)
        assert header_key == block_number

        file_info = FileInfo()
        file_info.header_block = block_number

        name_len = b.ubyte(BSIZE - 80)
        file_info.name = b.string(BSIZE - 79, name_len)
        #file_info.name = file_info.name.decode("ISO-8859-1")
        file_info.path = path + file_info.name + "/"
        # print(file_info.path)
        file_key = file_info.path.lower()
        if file_key[:-1] in self.file_map:
            self.warnings.append("Duplicate entries for file name "
                                 "{0}".format(file_key))
        self.file_map[file_key] = file_info

        self.block_usage[block_number].append(
            "header block for file " + file_info.path)
        if not verify_block(b.data):
            self.warnings.append("bad checksum for header for " +
                                 file_info.path)

        file_info.mode = b.ulong(BSIZE - 192)
        file_info.size = 0
        comment_len = b.ubyte(BSIZE - 184)
        file_info.comment = b.string(BSIZE - 183, comment_len)

        days = b.ulong(BSIZE - 92)
        mins = b.ulong(BSIZE - 88)
        ticks = b.ulong(BSIZE - 84)
        file_info.time = "{0:05d}:{1:04d}:{2:03d}".format(days, mins, ticks)

        self._parse_directory_content(file_info.path, block_number)

    def namelist(self):
        names = []
        keys = sorted(self.file_map.keys())
        for key in keys:
            names.append(self.file_map[key].path)
        return names

    def getinfo(self, name):
        name = name.lower()
        return self.file_map[name]

    def open(self, name, mode="r"):
        assert mode == "r"
        return BytesIO(self.read(name))

    def read(self, name):
        name = name.lower()
        print(repr(self.file_map))
        print(repr(name))
        file_info = self.file_map[name]
        bytes_left = file_info.size
        data = []
        for block_number in file_info.block_list:
            if self.ffs:
                start_index = 0
            else:
                start_index = 24
            max_bsize = BSIZE - start_index
            read_size = min(bytes_left, max_bsize)
            block_data = self.blocks[block_number].data[
                start_index:start_index + read_size]
            bytes_left -= len(block_data)
            data.append(block_data)
        assert bytes_left == 0
        return b"".join(data)


def main():
    adf = ADFFile(sys.argv[1])
    print("")
    print(os.path.basename(sys.argv[1]))
    print("Volume:", adf.volume_name, "(OFS)" if adf.ofs else "(FFS)")
    print("")
    for name in adf.namelist():
        print(name)
        if not name.endswith("/"):
            data = adf.open(name).read()
            print(" ", len(data), "bytes")
            print(" ", hashlib.sha1(data).hexdigest())
            # tracks = set()
            # for block in adf.file_map[name.lower()].block_list:
            #     track = block // 11
            #     cylinder = track // 2
            #     side = track % 2
            #     tracks.add((cylinder, side))
            # tracks = sorted(tracks)
            # print(tracks)
    print("")
    for warning in adf.warnings:
        print("WARNING:", warning)
    pass
    #for i, usage in enumerate(adf.block_usage):
    #    print(i, usage)
    for name in sys.argv[2:]:
        data = adf.open(name).read()
        with open(name + ".dump", "wb") as f:
            f.write(data)
            print("wrote " + name + ".dump")


if __name__ == "__main__":
    main()
