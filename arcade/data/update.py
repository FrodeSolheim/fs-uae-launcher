#!/usr/bin/env python3

import json

from PIL import Image

# def fix(name, w, h):
#    with open(name + ".raw", "rb") as f:
#        data = f.read()
#    im = Image.fromstring("RGBA", (w, h), data)
#    im.save(name + ".png")
#
#
# fix("title_font", 1024, 132)
# fix("menu_font", 1024, 132)


def white(pixels, x, y):
    # print(pixels[x, y])
    return pixels[x, y][0] > 128


def calculate(name):
    char_x = []
    char_y = []
    char_w = []
    char_h = []
    im = Image.open(name + ".png")
    pixels = im.load()
    x, y = 0, 0
    w, h = im.size
    char = -1
    in_x = False
    in_y = False
    rows = []
    y = 1
    while y < h:
        if not in_y and white(pixels, x, y):
            in_y = True
            rows.append([y])
        elif in_y and not white(pixels, x, y):
            in_y = False
            rows[-1].append(y - rows[-1][0])
        y += 1
    if len(rows[-1]) == 1:
        rows[-1].append(y - rows[-1][0])
    print(rows)
    for row in rows:
        x = 1
        y = row[0] - 1
        while x < w:
            if not in_x and white(pixels, x, y):
                in_x = True
                char += 1
                char_x.append(x)
                char_y.append(y + 1)
                char_h.append(row[1])
            elif in_x and not white(pixels, x, y):
                in_x = False
                char_w.append(x - char_x[-1])
            x += 1
    with open(name + ".json", "w") as f:
        json.dump({"x": char_x, "y": char_y, "w": char_w, "h": char_h}, f)


def main():
    calculate("title_font")
    calculate("menu_font")


if __name__ == "__main__":
    main()
