#!/usr/bin/env python3
import sys

from PIL import Image, ImageOps

"""
Tool for changing the color of monochrome icons.

"""


# def add_to_json(argv, glow=False):
#     import os
#     import json
#     path = argv[3]
#     sources = []
#     p1 = os.path.join(os.getcwd(), argv[2])
#     print("p1", p1)
#     p2 = os.path.normpath(os.path.join(os.getcwd(), path.split("/launcher")[0]))
#     print("p2", p2)
#     p = p1[len(p2) + 1 + 10:]
#     print(p)
#     # assert False
#     sources.append(p)
#     with open(path.split("/launcher")[0] + "/src/icons/icons.json") as f:
#         doc = json.load(f)
#     doc["launcher/" + path.split("/launcher/")[1]] = {
#         "type": "colorize",
#         "sources": sources
#     }
#     with open(path.split("/launcher")[0] + "/src/icons/icons.json", "w") as f:
#         json.dump(doc, f, sort_keys=True, indent=4)


def main():
    print(sys.argv)
    # add_to_json(sys.argv)
    color = sys.argv[1]
    dst = sys.argv[2]
    src = sys.argv[3]
    im = Image.open(src)
    r, g, b, alpha = im.split()
    im = im.convert("L")
    # colorize(im, color)
    im = ImageOps.colorize(im, black=color, white="white")
    im.putalpha(alpha)
    im.save(dst)


if __name__ == "__main__":
    main()
