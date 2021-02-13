#!/usr/bin/env python3

import json
import sqlite3
import sys
import zlib
from binascii import hexlify


def main():
    databasepath = sys.argv[1]
    database = sqlite3.connect(databasepath)
    cursor = database.cursor()
    cursor.execute("SELECT uuid, data FROM game")
    print("{", end="")
    count = 0
    for row in cursor:
        s = hexlify(row[0]).decode("ASCII")
        uuid = f"{s[0:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:32]}"
        if row[1]:
            data = zlib.decompress(row[1])
            jsonstr = data.decode("UTF-8")
            print("," if count > 0 else "")
            print(f'    "{uuid}": {jsonstr}', end="")
            count += 1
    print("\n}")
    print(f"Exported {count} entries", file=sys.stderr)


if __name__ == "__main__":
    main()
