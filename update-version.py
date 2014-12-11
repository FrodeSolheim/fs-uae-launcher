#!/usr/bin/env python

import os
import io
import sys


def update_version(path, strict=False, update_series=False):
    if not os.path.exists(path):
        print(path, "does not exist, not updating version")
        return
    print("updating version number in", path)

    ver = version
    with io.open(path, "r", encoding="ISO-8859-1", newline="") as f:
        data = f.read()

    data = data.replace("9.8.7dummy3", version_3)
    data = data.replace("9.8.7dummy", version)
    data = data.replace("9.8.7", version_3 if strict else version)
    if update_series:
        data = data.replace("unknown", series)
    with io.open(path, "w", encoding="ISO-8859-1", newline="") as f:
        f.write(data)


with io.open("VERSION", "r", encoding="ISO-8859-1", newline="") as f:
    version = f.read().strip()

parts = version.split(".")
parts = parts[:3]
for i, part in enumerate(parts):
    p = ""
    for c in part:
        if c in "0123456789":
            p += c
        else:
            break
    parts[i] = p
version_3 = ".".join(parts)

with io.open("SERIES", "r", encoding="ISO-8859-1", newline="") as f:
    series = f.read().strip()

update_version(
    sys.argv[1], update_series=("--update-series" in sys.argv),
    strict=("--strict" in sys.argv))
