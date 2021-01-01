#!/usr/bin/env python3
import sys

from PIL import Image, ImageOps

"""
Tool for changing the color of monochrome icons.

"""


def main():
    print(sys.argv)
    color = sys.argv[1]
    src = sys.argv[2]
    dst = sys.argv[3]
    im = Image.open(src)
    r, g, b, alpha = im.split()
    im = im.convert("L")
    # colorize(im, color)
    im = ImageOps.colorize(im, black=color, white="white")
    im.putalpha(alpha)
    im.save(dst)


if __name__ == "__main__":
    main()
