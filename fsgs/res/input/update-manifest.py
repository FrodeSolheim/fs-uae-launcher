#!/usr/bin/env python
import os


lines = []
for dir_path, dir_names, file_names in os.walk("."):
    for name in file_names:
        if name in ["manifest.txt", "update-manifest.py"]:
            continue
        path = os.path.join(dir_path, name)
        lines.append(path[2:])
lines.sort()
with open ("manifest.txt", "wb") as f:
    for line in lines:
        f.write(line + "\n")
