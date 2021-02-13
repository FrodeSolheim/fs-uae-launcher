#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, "../git/fs-uae-master/fs-uae-launcher")
# from fsui.qt.qt import QApplication
from fsui.qt.qt import QImage, QPainter, QSvgRenderer
from PIL import Image, ImageFilter

"""
Module for creating glow-icon-alike effects on icons.

Quick and dirty code. No effort has been spent on trying to make the code
efficient or anything like that. The intention is to use this as a
pre-processing step.
"""

# Glowicons are 46x46. The extra radius due to the glow effect is 4 pixels, so
# the actual icons are effectively 38x38. If we scale up the icons to 150%,
# we get 69x69 incl. glow and 57x57 excl. glow.

# Suggest standardizing on 76x76 (64x64 + 4 * 1.5 radius). Icons are encouraged
# to have some space around them, so that the effective bounding area for most
# icons are 56x56 og 58x58 or something like that.
SIZE = (76, 76)

# We need to render temporarily at a slightly bigger size, due to filters and
# edge conditions. Otherwise, the bigger icons will have cutoffs in the glow
# effect. After rendering to a temporarily bigger size, we just trim the image
# down to the desired size.
TEMPSIZE = (86, 86)


def darken(im, factor=0.67):
    pixels = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = pixels[x, y]
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            pixels[x, y] = r, g, b, a


def transparency_threshold(im):
    pixels = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = pixels[x, y]
            if a > 128:
                a = 255
            else:
                a = 0
            pixels[x, y] = r, g, b, a


def dilate_colored(im, c=(0, 0, 0, 0)):
    result = Image.new("RGBA", im.size)
    src = im.load()
    dst = result.load()
    for y in range(1, im.size[1] - 1):
        for x in range(1, im.size[0] - 1):
            p = (c[0], c[1], c[2], 0)
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    p2 = src[x + dx, y + dy]
                    if p2[3] > 0:
                        p = (c[0], c[1], c[2], 255)
                        break
            dst[x, y] = p
    return result


def multiply_alpha(im, factor=0.5):
    pixels = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = pixels[x, y]
            a = int(a * factor)
            pixels[x, y] = r, g, b, a


# def add_glow(orig):
#     base = Image.new("RGBA", TEMPSIZE, (0, 0, 0, 0))
#     base.paste(
#         orig,
#         ((TEMPSIZE[0] - orig.size[0]) // 2, (TEMPSIZE[1] - orig.size[1]) // 2),
#     )

#     dark = base.copy()
#     darken(dark)

#     g1 = base.copy()
#     transparency_threshold(g1)

#     white = dilate_colored(g1, (255, 255, 255, 0))
#     white2 = dilate_colored(white, (255, 255, 255, 0))
#     yellow = dilate_colored(white2, (0xFF, 0xFF, 0x00))
#     orange = dilate_colored(yellow, (0xFF, 0xBB, 0x00))
#     orange2 = dilate_colored(orange, (0xFF, 0x99, 0x00))

#     white = white.filter(ImageFilter.BLUR)
#     white2 = white2.filter(ImageFilter.BLUR)
#     yellow = yellow.filter(ImageFilter.BLUR)
#     orange = orange.filter(ImageFilter.BLUR)
#     orange2 = orange2.filter(ImageFilter.BLUR)

#     multiply_alpha(yellow, 0.67)
#     multiply_alpha(orange2, 0.67)
#     multiply_alpha(orange2, 0.33)

#     glow = Image.new("RGBA", TEMPSIZE, (0, 0, 0, 0))
#     glow = Image.alpha_composite(glow, orange2)
#     glow = Image.alpha_composite(glow, orange)
#     glow = Image.alpha_composite(glow, yellow)
#     glow = Image.alpha_composite(glow, white2)
#     # Render the white twice here is on purpose, to make the thin inner white
#     # area more distinct.
#     glow = Image.alpha_composite(glow, white)
#     glow = Image.alpha_composite(glow, white)
#     glow = Image.alpha_composite(glow, dark)
#     # Cut to final size.
#     glow = glow.crop(
#         (
#             (TEMPSIZE[0] - SIZE[0]) // 2,
#             (TEMPSIZE[1] - SIZE[1]) // 2,
#             SIZE[0] + (TEMPSIZE[0] - SIZE[0]) // 2,
#             SIZE[1] + (TEMPSIZE[1] - SIZE[1]) // 2,
#         )
#     )
#     return glow


def add_glow(orig):
    base = Image.new("RGBA", TEMPSIZE, (0, 0, 0, 0))
    base.paste(
        orig,
        ((TEMPSIZE[0] - orig.size[0]) // 2, (TEMPSIZE[1] - orig.size[1]) // 2),
    )

    dark = base.copy()
    darken(dark)

    g1 = base.copy()
    transparency_threshold(g1)

    white = dilate_colored(g1, (255, 255, 255, 0))
    # white2 = dilate_colored(white, (255, 255, 255, 0))
    yellow = dilate_colored(white, (0xFF, 0xFF, 0x00))
    orange = dilate_colored(yellow, (0xFF, 0xBB, 0x00))
    orange2 = dilate_colored(orange, (0xFF, 0x99, 0x00))

    white = white.filter(ImageFilter.BLUR)
    # white2 = white2.filter(ImageFilter.BLUR)
    yellow = yellow.filter(ImageFilter.BLUR)
    orange = orange.filter(ImageFilter.BLUR)
    orange2 = orange2.filter(ImageFilter.BLUR)

    multiply_alpha(yellow, 0.67)
    multiply_alpha(orange, 0.50)
    multiply_alpha(orange2, 0.25)

    glow = Image.new("RGBA", TEMPSIZE, (0, 0, 0, 0))
    glow = Image.alpha_composite(glow, orange2)
    glow = Image.alpha_composite(glow, orange)
    glow = Image.alpha_composite(glow, yellow)
    # glow = Image.alpha_composite(glow, white2)
    # Render the white twice here is on purpose, to make the thin inner white
    # area more distinct.
    glow = Image.alpha_composite(glow, white)
    glow = Image.alpha_composite(glow, white)
    glow = Image.alpha_composite(glow, dark)
    # Cut to final size.
    glow = glow.crop(
        (
            (TEMPSIZE[0] - SIZE[0]) // 2,
            (TEMPSIZE[1] - SIZE[1]) // 2,
            SIZE[0] + (TEMPSIZE[0] - SIZE[0]) // 2,
            SIZE[1] + (TEMPSIZE[1] - SIZE[1]) // 2,
        )
    )
    return glow


# _application = None


def open_svg(path):
    # global _application
    # if _application is None:
    #     _application = QApplication(sys.argv)
    renderer = QSvgRenderer(path)
    image = QImage(64, 64, QImage.Format_RGBA8888)
    image.fill(0x00000000)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    # del painter
    return Image.frombytes(
        "RGBA", (64, 64), image.bits().asstring(64 * 64 * 4)
    )


def load_icon_76x76(path, overlay=None):
    if path.endswith(".svg"):
        orig = open_svg(path)
    else:
        orig = Image.open(path)
    new = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    new.paste(
        orig,
        ((SIZE[0] - orig.size[0]) // 2, (SIZE[1] - orig.size[1]) // 2),
    )

    if overlay:
        # print("overlay", overlay)
        # overlay_img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        # return overlay_img

        overlay_org = Image.open(overlay)
        overlay_img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        # return overlay_img
        overlay_img.paste(
            overlay_org,
            (
                (SIZE[0] - overlay_org.size[0]) // 2,
                (SIZE[1] - overlay_org.size[1]) // 2,
            ),
        )
        new = Image.alpha_composite(new, overlay_img)
    # overlay_path = os.path.dirname(path)
    # if os.path.exists(overlay_path)
    return new


def save_icon(im, name):
    im.save(os.path.join(name))


def process_icon_in_directory(dirpath, overlay=None):
    iconname = os.path.basename(dirpath)
    print(iconname)
    src1 = os.path.join(dirpath, iconname + ".svg")
    if not os.path.exists(src1):
        src1 = os.path.join(dirpath, iconname + ".png")
    im1 = load_icon_76x76(src1, overlay=overlay)
    src2 = os.path.join(dirpath, iconname + "_2.png")
    save_icon(im1, os.path.splitext(dirpath)[0] + "_Normal.png")
    if os.path.exists(src2):
        im2 = load_icon_76x76(src2, overlay=overlay)
    else:
        im2 = im1
    im2 = add_glow(im2)
    save_icon(im2, os.path.splitext(dirpath)[0] + "_Selected.png")


def create_icon(output, sources, glow):
    if len(sources) == 1:
        src = sources[0]
        overlay = None
    else:
        src, overlay = sources
    # im = load_icon_76x76(src, overlay=overlay)
    im = load_icon_76x76(src, overlay=False)
    if glow:
        im = add_glow(im)

    if overlay:
        # print("overlay", overlay)
        # overlay_img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        # return overlay_img

        overlay_org = Image.open(overlay)
        overlay_img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        # return overlay_img
        overlay_img.paste(
            overlay_org,
            (
                (SIZE[0] - overlay_org.size[0]) // 2,
                (SIZE[1] - overlay_org.size[1]) // 2,
            ),
        )
        # if glow:
        #     darken(overlay_img)
        im = Image.alpha_composite(im, overlay_img)

    save_icon(im, output)


def main():
    if "--base" in sys.argv:
        sys.argv.remove("--base")
        return create_icon(sys.argv[1], sys.argv[2:], glow=False)
    if "--glow" in sys.argv:
        sys.argv.remove("--glow")
        return create_icon(sys.argv[1], sys.argv[2:], glow=True)

    path = sys.argv[1]
    if len(sys.argv) > 2:
        overlay = sys.argv[2]
    else:
        overlay = None
    if os.path.isdir(path):
        process_icon_in_directory(path, overlay=overlay)


if __name__ == "__main__":
    main()
