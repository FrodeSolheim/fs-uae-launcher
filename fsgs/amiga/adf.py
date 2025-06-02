#!/usr/bin/env python3

import hashlib
import os
import sys
from io import BytesIO
# noinspection PyUnresolvedReferences
from typing import Dict, List

B_SIZE = 512
B_COUNT = 880 * 2
T_HEADER = 2
T_DATA = 8
T_LIST = 16
ST_ROOT = 1
ST_USERDIR = 2
ST_FILE = 0xFFFFFFFF - 3 + 1


def char(block: bytes, pos: int) -> str:
    return block[pos : pos + 1].decode("ISO-8859-1")


def ubyte(block: bytes, pos: int) -> int:
    return block[pos]


def ulong(block: bytes, pos: int) -> int:
    a = block[pos]
    b = block[pos + 1]
    c = block[pos + 2]
    d = block[pos + 3]
    return (a << 24) | (b << 16) | (c << 8) | d


def checksum_block(block: bytes) -> int:
    # clear checksum field
    data = block[:20] + b"\0\0\0\0" + block[24:]
    sum = 0
    for pos in range(0, B_SIZE, 4):
        sum += ulong(data, pos)
        sum &= 0xFFFFFFFF
    sum = -sum
    sum &= 0xFFFFFFFF
    return sum


def verify_block(data: bytes) -> bool:
    sum = 0
    for pos in range(0, B_SIZE, 4):
        sum += ulong(data, pos)
        sum &= 0xFFFFFFFF
    return sum == 0


class Block(object):
    def __init__(self, data: bytes) -> None:
        self.data = data

    def char(self, pos: int) -> str:
        return char(self.data, pos)

    def string(self, pos: int, len: int) -> str:
        return self.data[pos : pos + len].decode("ISO-8859-1")

    def ubyte(self, pos: int) -> int:
        return ubyte(self.data, pos)

    def ulong(self, pos: int) -> int:
        return ulong(self.data, pos)


class FileInfo(object):
    def __init__(self):
        self.block_list = []
        self.header_block = -1
        self.name = ""
        self.path = ""
        self.comment = None
        self.time = ""
        self.mode = 0
        self.size = 0


class ADFFile(object):
    FFS_FLAG = 1
    INTL_ONLY_FLAG = 2
    DIRC_AND_INTL_FLAG = 4

    def __init__(self, stream_or_data_or_file):
        if hasattr(stream_or_data_or_file, "read"):
            data = stream_or_data_or_file.read()
        elif len(stream_or_data_or_file) == B_SIZE * B_COUNT:
            data = stream_or_data_or_file
        else:
            with open(stream_or_data_or_file, "rb") as f:
                data = f.read()
        assert isinstance(data, bytes)
        # print(len(data))
        assert len(data) == B_SIZE * B_COUNT
        self.blocks = []  # type: List[Block]
        for i in range(0, B_SIZE * B_COUNT, B_SIZE):
            self.blocks.append(Block(data[i : i + B_SIZE]))
        assert len(self.blocks) == B_COUNT
        self.block_usage = [["block"] for _ in range(B_COUNT)]
        self.dos = False
        self.ofs = False
        self.ffs = False
        self.warnings = []  # type: List[str]
        self.file_map = {}  # type: Dict[str, FileInfo]
        self.root_block_number = 880
        self.bitmap_pages = []
        self._parse()

    def root_block(self) -> Block:
        return self.blocks[self.root_block_number]

    def _parse(self) -> None:
        b = self.blocks[0]
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
            self.warnings.append(
                "Root block is at position {0}, " "not 880".format(
                    self.root_block_number
                )
            )
            self.root_block_number = 880
            self.warnings.append("Trying 880 anyway...")

        self._parse_root_block()
        self.block_usage[self.root_block_number].append("root block")

        for i, usage in enumerate(self.block_usage):
            if "used" in usage:
                if usage == ["block", "used"]:
                    self.warnings.append(
                        "block {0} marked as used but no actual usage".format(
                            i
                        )
                    )
            if "free" in usage:
                if usage != ["block", "free"]:
                    self.warnings.append(
                        "block {0} marked as used but used for {1}".format(
                            i, repr(usage)
                        )
                    )

    def _parse_root_block(self) -> None:
        b = self.root_block()
        type = b.ulong(0)
        secondary_type = b.ulong(B_SIZE - 4)
        if type != T_HEADER:
            print(type, T_HEADER)
            self.warnings.append("root block does not have T_HEADER type")
        if secondary_type != ST_ROOT:
            self.warnings.append(
                "root block does not have ST_ROOT secondary " "type"
            )

        days = b.ulong(B_SIZE - 92)
        mins = b.ulong(B_SIZE - 88)
        ticks = b.ulong(B_SIZE - 84)
        self.root_mtime = "{0:05d}:{1:04d}:{2:03d}".format(days, mins, ticks)

        days = b.ulong(B_SIZE - 40)
        mins = b.ulong(B_SIZE - 36)
        ticks = b.ulong(B_SIZE - 32)
        self.disk_mtime = "{0:05d}:{1:04d}:{2:03d}".format(days, mins, ticks)

        days = b.ulong(B_SIZE - 28)
        mins = b.ulong(B_SIZE - 24)
        ticks = b.ulong(B_SIZE - 20)
        self.disk_ctime = "{0:05d}:{1:04d}:{2:03d}".format(days, mins, ticks)

        bm_flag = b.ulong(B_SIZE - 200)
        if bm_flag != 0xFFFFFFFF:
            self.warnings.append(
                "bm_flag != 0xffffffff ({0:8x})".format(bm_flag)
            )
            if bm_flag == 0:
                self.warnings.append("bm_flag is ZERO")
        for i in range(25):
            self.bitmap_pages.append(b.ulong(B_SIZE - 196 + 4 * i))
        self._parse_used_blocks()

        name_len = b.ubyte(B_SIZE - 80)
        self.volume_name = b.string(B_SIZE - 79, name_len)
        # self.volume_name = self.volume_name.decode("ISO-8859-1")
        self._parse_directory_content("", self.root_block_number)
        if not verify_block(b.data):
            self.warnings.append("bad root checksum")

    def _parse_used_blocks(self) -> None:
        for i in range(len(self.bitmap_pages)):
            block_number = self.bitmap_pages[i]
            if block_number:
                if block_number >= B_COUNT:
                    self.warnings.append(
                        "invalid block number {0} in bitmap pages".format(
                            block_number
                        )
                    )
                    continue
                self.block_usage[block_number].append("bitmap block")

            if i == 0:
                if not block_number:
                    self.warnings.append("no bitmap block for disk")
                    continue
            else:
                if block_number:
                    self.warnings.append(
                        "unexpected additional bitmap block..."
                    )
                continue

            b = self.blocks[block_number]
            if not verify_block(b.data):
                self.warnings.append(
                    "bitmap block checksum is invalid (" "ignoring this block)"
                )
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

    def _parse_directory_content(self, path: str, block_number: int) -> None:
        d_b = self.blocks[block_number]
        d_secondary_type = d_b.ulong(B_SIZE - 4)
        if d_secondary_type == ST_ROOT:
            ht_size = d_b.ulong(12)
            assert ht_size == (B_SIZE // 4) - 56

        for i in range((B_SIZE // 4) - 56):
            entry = d_b.ulong(24 + i * 4)
            while entry:
                # print(entry)
                if entry >= B_COUNT:
                    self.warnings.append(
                        "directory entry refers to an invalid block "
                        "number {0}".format(entry)
                    )
                    entry = 0
                    continue
                b = self.blocks[entry]
                type = b.ulong(0)
                secondary_type = b.ulong(B_SIZE - 4)
                parent = b.ulong(B_SIZE - 12)
                assert type == T_HEADER
                assert secondary_type in [ST_USERDIR, ST_FILE]
                assert parent == block_number

                if secondary_type == ST_USERDIR:
                    self._parse_directory(path, entry)
                elif secondary_type == ST_FILE:
                    self._parse_file(path, entry)
                else:
                    raise Exception("neither ST_USERDIR or ST_FILE")

                entry = b.ulong(B_SIZE - 16)

    def _parse_file(self, path: str, block_number: int) -> None:
        b = self.blocks[block_number]
        header_key = b.ulong(4)
        assert header_key == block_number

        file_info = FileInfo()
        file_info.header_block = block_number

        name_len = b.ubyte(B_SIZE - 80)
        file_info.name = b.string(B_SIZE - 79, name_len)
        file_info.path = path + file_info.name
        # print(file_info.path)
        file_key = file_info.path.lower()
        if file_key in self.file_map:
            self.warnings.append(
                "duplicate entries for file name " "{0}".format(file_key)
            )
        self.file_map[file_key] = file_info

        self.block_usage[block_number].append(
            "header block for file " + file_info.path
        )
        if not verify_block(b.data):
            self.warnings.append(
                "bad checksum for header for " + file_info.path
            )

        file_info.mode = b.ulong(B_SIZE - 192)
        file_info.size = b.ulong(B_SIZE - 188)
        comment_len = b.ubyte(B_SIZE - 184)
        file_info.comment = b.string(B_SIZE - 183, comment_len)

        days = b.ulong(B_SIZE - 92)
        mins = b.ulong(B_SIZE - 88)
        ticks = b.ulong(B_SIZE - 84)
        file_info.time = "{0:05d}:{1:04d}:{2:03d}".format(days, mins, ticks)

        first_data = b.ulong(16)
        next_data = first_data
        file_blocks_1 = []  # type: List[int]
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
                    "file {3}".format(
                        next_data, len(file_blocks_1), seq_num, file_info.path
                    )
                )
            data_size = data_b.ulong(12)
            ofs_accum_size += data_size

            if not verify_block(data_b.data):
                self.warnings.append(
                    "block {1:04d} - bad checksum for data block #{0} for "
                    "file {2}".format(k + 1, next_data, file_info.path)
                )
            # self.block_usage[next_data].append(
            #     "block {2:04d} - data block #{0} for file {1}".format(
            #         k + 1, file_info.path, next_data))

            next_data = data_b.ulong(16)
            k += 1

        file_blocks_2 = []  # type: List[int]
        extension = block_number
        k = 0
        while extension:
            ext_b = self.blocks[extension]
            ext_type = ext_b.ulong(0)
            ext_secondary_type = ext_b.ulong(B_SIZE - 4)
            if extension != block_number:
                assert ext_type == T_LIST
            assert ext_secondary_type == ST_FILE
            high_seq = ext_b.ulong(8)
            for i in range(high_seq):
                file_blocks_2.append(ext_b.ulong(B_SIZE - 204 - i * 4))

            parent = ext_b.ulong(B_SIZE - 12)
            if k > 0 and parent != block_number:
                self.warnings.append(
                    "block {3:04d} - expected parent {0} (found {1} for OFS "
                    "extension block #{2} for file {4}".format(
                        block_number, parent, k, extension, file_info.path
                    )
                )

            if not verify_block(ext_b.data):
                self.warnings.append(
                    "block {2:04d} - bad checksum for extension block #{0} "
                    "for file {1}".format(k, file_info.path, extension)
                )
            extension = ext_b.ulong(B_SIZE - 8)
            if extension:
                self.block_usage[extension].append(
                    "file extension block #{0} for file {1}".format(
                        k, file_info.path
                    )
                )
            k += 1

        if self.ofs:
            if file_blocks_1 != file_blocks_2:
                self.warnings.append(
                    "block list mismatch (extension vs OFS headers) for "
                    "file {0}".format(file_info.path)
                )
            if len(file_blocks_1) != len(file_blocks_2):
                self.warnings.append(
                    "block list length mismatch (extension {0} vs OFS "
                    "headers {1}) for file {2}".format(
                        len(file_blocks_2), len(file_blocks_1), file_info.path
                    )
                )
            if ofs_accum_size != file_info.size:
                self.warnings.append(
                    "file size mismatch (file header {0} vs OFS data block "
                    "headers {1}) for file {2}".format(
                        file_info.size, ofs_accum_size, file_info.path
                    )
                )

        file_info.block_list = file_blocks_2

        for i, bn in enumerate(file_blocks_2):
            self.block_usage[bn].append(
                "data block #{0} for file {1}".format(
                    i + 1, file_info.path, bn
                )
            )

    def _parse_directory(self, path: str, block_number: int) -> None:
        b = self.blocks[block_number]
        header_key = b.ulong(4)
        assert header_key == block_number

        file_info = FileInfo()
        file_info.header_block = block_number

        name_len = b.ubyte(B_SIZE - 80)
        file_info.name = b.string(B_SIZE - 79, name_len)
        file_info.path = path + file_info.name + "/"
        # print(file_info.path)
        file_key = file_info.path.lower()
        if file_key[:-1] in self.file_map:
            self.warnings.append(
                "Duplicate entries for file name " "{0}".format(file_key)
            )
        self.file_map[file_key] = file_info

        self.block_usage[block_number].append(
            "header block for file " + file_info.path
        )
        if not verify_block(b.data):
            self.warnings.append(
                "bad checksum for header for " + file_info.path
            )

        file_info.mode = b.ulong(B_SIZE - 192)
        file_info.size = 0
        comment_len = b.ubyte(B_SIZE - 184)
        file_info.comment = b.string(B_SIZE - 183, comment_len)

        days = b.ulong(B_SIZE - 92)
        mins = b.ulong(B_SIZE - 88)
        ticks = b.ulong(B_SIZE - 84)
        file_info.time = "{0:05d}:{1:04d}:{2:03d}".format(days, mins, ticks)

        self._parse_directory_content(file_info.path, block_number)

    def namelist(self) -> List[str]:
        names = []  # type: List[str]
        keys = sorted(self.file_map.keys())
        for key in keys:
            names.append(self.file_map[key].path)
        return names

    def getinfo(self, name: str) -> FileInfo:
        name = name.lower()
        return self.file_map[name]

    def open(self, name: str, mode: str = "r") -> BytesIO:
        assert mode == "r"
        return BytesIO(self.read(name))

    def read(self, name: str) -> bytes:
        name = name.lower()
        # print(repr(self.file_map))
        # print(repr(name))
        file_info = self.file_map[name]
        bytes_left = file_info.size
        data = []  # type: List[bytes]
        for block_number in file_info.block_list:
            if self.ffs:
                start_index = 0
            else:
                start_index = 24
            max_bsize = B_SIZE - start_index
            read_size = min(bytes_left, max_bsize)
            block_data = self.blocks[block_number].data[
                start_index : start_index + read_size
            ]
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
            print("   ", hashlib.sha1(data).hexdigest(), "", len(data))
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
    # for i, usage in enumerate(adf.block_usage):
    #     print(i, usage)
    for name in sys.argv[2:]:
        data = adf.open(name).read()
        with open(name + ".dump", "wb") as f:
            f.write(data)
            print("wrote " + name + ".dump")


if __name__ == "__main__":
    main()
