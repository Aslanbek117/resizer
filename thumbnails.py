import os

import image_slicer
from PIL import Image, ImageFilter
import urllib
import wget
import ssl
import pandas as pd
import openpyxl
from transliterate import translit, get_available_language_codes
import psycopg2
from psycopg2 import sql

def getImageSizes(fileIn):
    img =Image.open(fileIn)
    return img.size


def dropShadow(fileName, image, offset=(1,1), background=0xffffff, shadow=0x444444,
               border=8, iterations=3):
    """
    Add a gaussian blur drop shadow to an image.

    image       - The image to overlay on top of the shadow.
    offset      - Offset of the shadow from the image as an (x,y) tuple.  Can be
                  positive or negative.
    background  - Background colour behind the image.
    shadow      - Shadow colour (darkness).
    border      - Width of the border around the image.  This must be wide
                  enough to account for the blurring of the shadow.
    iterations  - Number of times to apply the filter.  More iterations
                  produce a more blurred shadow, but increase processing time.
    """

    # Create the backdrop image -- a box in the background colour with a
    # shadow on it.
    totalWidth = image.size[0] + abs(offset[0]) + 2 * border
    totalHeight = image.size[1] + abs(offset[1]) + 2 * border
    back = Image.new(image.mode, (totalWidth, totalHeight), background)

    # Place the shadow, taking into account the offset from the image
    shadowLeft = border + max(offset[0], 0)
    shadowTop = border + max(offset[1], 0)
    back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0],
                        shadowTop + image.size[1]])

    # Apply the filter to blur the edges of the shadow.  Since a small kernel
    # is used, the filter must be applied repeatedly to get a decent blur.
    n = 0
    while n < iterations:
        back = back.filter(ImageFilter.BLUR)
        n += 1

    # Paste the input image onto the shadow backdrop
    imageLeft = border - min(offset[0], 0)
    imageTop = border - min(offset[1], 0)
    back.paste(image, (imageLeft, imageTop))
    back.save(fileName)
    return back

def crop(directory, fileIn, fileOut, area):
    im = Image.open(fileIn).convert('RGB')
    im = im.crop(area)
    name = fileOut + "_crop.jpg"
    im.save(directory + name)

def thumbnail(directory, file_path_in, file_path_out, width, heigth):
    image = Image.open(directory + file_path_in)
    image.thumbnail(size=(width, heigth))
    dropShadow(directory + file_path_out + "_shadow.jpg", image, background=0xeeeeee, shadow=0x444444, offset=(0, 5))
    name = directory +file_path_out +"_thumbnail.jpg"
    image.save(name, optimize=True, quality=100)
    return image.size

def putToBack(directory, path_to_background, path_to_image, from_x, from_y, path_to_background_out):
    img = Image.open(directory + path_to_image).convert("RGB")
    background = Image.open(path_to_background).convert("RGB")
    offset = (from_x, from_y)
    background.paste(img, offset)
    background.save(directory +path_to_background_out)


def make_1(id, directory, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    width, height = getImageSizes(file_in)
    file_out = module + "_" + file_out
    crop(directory, file_in, file_out + "_1", (0,0, width / 2, height))
    crop(directory, file_in, file_out + "_2", (width /2 ,0, width, height))
    thumbnail(directory, file_out +"_1_crop.jpg", file_out +"_1", from_x, from_y)
    thumbnail(directory, file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbName = "complex_1.jpg"
    putToBack(directory, background_in,file_out + "_1_shadow.jpg", 625, 150, thumbName)
    putToBack(directory, background_out, file_out + "_2_shadow.jpg", 950, 150, thumbName)


def make_2(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    width, height = getImageSizes(file_in)
    file_out = module + "_" + file_out
    crop(file_in, file_out + "_1", (0,0, width / 3, height))
    crop(file_in, file_out + "_2", (width /3,0, width - width / 3 , height))
    crop(file_in, file_out+ "_3", (width - width /3, 0, width, height))
    thumbnail(file_out +"_1_crop.jpg", file_out +"_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbName = "complex_2.jpg"
    putToBack(background_in,file_out + "_1_shadow.jpg", initial, 150, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 150, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance *2, 150, thumbName)
    # putToBack(background_out, file_out + "_3_shadow.jpg", 950, 150, background_out)

def make_3(id,module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    width, height = getImageSizes(file_in)
    file_out = module + "_" + file_out
    crop(file_in, file_out + "_1", (0,0, width / 3, height))
    crop(file_in, file_out + "_2", (width /3,0, width - width / 3 , height))
    crop(file_in, file_out+ "_3", (width - width /3, 0, width, height))
    thumbnail(file_out +"_1_crop.jpg", file_out +"_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbName = "complex_3.jpg"
    putToBack(background_in,file_out + "_1_shadow.jpg", initial, 50, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 100, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance *2, 150, thumbName)


def make_4(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    width, height = getImageSizes(file_in)
    file_out = module + "_" + file_out
    crop(file_in, file_out + "_1", (0,0, width / 3, height))
    crop(file_in, file_out + "_2", (width /3,0, width - width / 3 , height))
    crop(file_in, file_out+ "_3", (width - width /3, 0, width, height))
    thumbnail(file_out +"_1_crop.jpg", file_out +"_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbName = "complex_4.jpg"
    putToBack(background_in,file_out + "_1_shadow.jpg", initial, 150, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 100, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance *2, 50, thumbName)


def make_5(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 2, height))
    crop(file_in, file_out + "_2", (width / 2, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbName = "complex_5.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 150, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 100, thumbName)

def make_6(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 2, height))
    crop(file_in, file_out + "_2", (width / 2, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbName = "complex_6.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 150, thumbName)
#
# def make_7(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
#     initial = 625
#     distance = 220
#     file_out = module + "_" + file_out
#     width, height = getImageSizes(file_in)
#     crop(file_in, file_out + "_1", (0, 0, width / 2, height))
#     crop(file_in, file_out + "_2", (width / 2, 0, width, height))
#     size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
#     thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
#     thumbName = "complex_7.jpg"
#     distance = size_w + 25
#     putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
#     putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 150, thumbName)

def make_8(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 3, height))
    crop(file_in, file_out + "_2", (width / 3, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbName = "complex_8.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 150, thumbName)

def make_9(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 3, height))
    crop(file_in, file_out + "_2", (width / 3, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbName = "complex_9.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 150, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 100, thumbName)

def make_10(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 3, height))
    crop(file_in, file_out + "_2", (width / 3, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbName = "complex_10.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 100, thumbName)


def make_11(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 1.5, height))
    crop(file_in, file_out + "_2", (width / 1.5, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbName = "complex_11.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 100, thumbName)


def make_12(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 1.5, height))
    crop(file_in, file_out + "_2", (width / 1.5, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbName = "complex_12.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 150, thumbName)

def make_13(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 1.5, height))
    crop(file_in, file_out + "_2", (width / 1.5, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbName = "complex_13.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 150, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 100, thumbName)

def make_14(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 4, height))
    crop(file_in, file_out + "_2", (width / 4, 0, width / 2, height))
    crop(file_in, file_out + "_3", (width / 2, 0, width / 2 + width / 4, height))
    crop(file_in, file_out + "_4", (width / 2 + width / 4 , 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbnail(file_out + "_4_crop.jpg", file_out + "_4", from_x, from_y)
    thumbName = "complex_14.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 100, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance * 2, 100, thumbName)
    putToBack(background_out, file_out + "_4_shadow.jpg", initial + distance * 3, 100, thumbName)


def make_15(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 4, height))
    crop(file_in, file_out + "_2", (width / 4, 0, width / 2, height))
    crop(file_in, file_out + "_3", (width / 2, 0, width / 2 + width / 4, height))
    crop(file_in, file_out + "_4", (width / 2 + width / 4 , 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbnail(file_out + "_4_crop.jpg", file_out + "_4", from_x, from_y)
    thumbName = "complex_15.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 120, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance * 2, 140, thumbName)
    putToBack(background_out, file_out + "_4_shadow.jpg", initial + distance * 3, 160, thumbName)


def make_16(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 4, height))
    crop(file_in, file_out + "_2", (width / 4, 0, width / 2, height))
    crop(file_in, file_out + "_3", (width / 2, 0, width / 2 + width / 4, height))
    crop(file_in, file_out + "_4", (width / 2 + width / 4 , 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbnail(file_out + "_4_crop.jpg", file_out + "_4", from_x, from_y)
    thumbName = "complex_16.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 160, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 140, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance * 2, 120, thumbName)
    putToBack(background_out, file_out + "_4_shadow.jpg", initial + distance * 3, 100, thumbName)


def make_17(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 5, height))
    crop(file_in, file_out + "_2", (width / 5, 0, width / 2 + width / 3 , height))
    crop(file_in, file_out + "_3", (width / 2 + width / 3, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbName = "complex_17.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 100, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance * 3 + 115, 100, thumbName)


def make_18(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 5, height))
    crop(file_in, file_out + "_2", (width / 5, 0, width / 2 + width / 3 , height))
    crop(file_in, file_out + "_3", (width / 2 + width / 3, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbName = "complex_18.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 150, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance * 3 + 115, 100, thumbName)


def make_19(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 5, height))
    crop(file_in, file_out + "_2", (width / 5, 0, width / 2 + width / 3 , height))
    crop(file_in, file_out + "_3", (width / 2 + width / 3, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbName = "complex_19.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 200, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 150, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance * 3 + 115, 200, thumbName)


def make_20(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 5, height))
    crop(file_in, file_out + "_2", (width / 5, 0, width / 2 + width / 3 , height))
    crop(file_in, file_out + "_3", (width / 2 + width / 3, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbName = "complex_20.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 100, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 150, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance * 3 + 115, 200, thumbName)


def make_21(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 5, height))
    crop(file_in, file_out + "_2", (width / 5, 0, width / 2 + width / 3 , height))
    crop(file_in, file_out + "_3", (width / 2 + width / 3, 0, width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", from_x, from_y)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", from_x, from_y)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbName = "complex_21.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 200, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial + distance, 150, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance * 3 + 115, 100, thumbName)


def make_22(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 5, height/2))
    crop(file_in, file_out + "_2", (0, height / 2, width / 5, height))
    crop(file_in, file_out + "_3", (width / 5, 0, width / 2 + width / 5, height))
    crop(file_in, file_out + "_4", (width / 2 + width / 5, 0, width, height / 2))
    crop(file_in, file_out + "_5", (width / 2 + width / 5, height /2 , width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", 200, 200)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", 200, 200)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbnail(file_out + "_4_crop.jpg", file_out + "_4", 200, 200)
    thumbnail(file_out + "_5_crop.jpg", file_out + "_5", 200,200)
    thumbName = "complex_22.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 160, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial, 160 + size_h, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance , 160, thumbName)
    putToBack(background_out, file_out + "_4_shadow.jpg", initial + distance * 3 + 25, 160, thumbName)
    putToBack(background_out, file_out + "_5_shadow.jpg", initial + distance * 3 + 25, 160 + size_h, thumbName)


def make_23(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 5, height/2))
    crop(file_in, file_out + "_2", (0, height / 2, width / 5, height))
    crop(file_in, file_out + "_3", (width / 5, 0, width / 2 + width / 5, height))
    crop(file_in, file_out + "_4", (width / 2 + width / 5, 0, width, height / 2))
    crop(file_in, file_out + "_5", (width / 2 + width / 5, height /2 , width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", 200, 200)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", 200, 200)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbnail(file_out + "_4_crop.jpg", file_out + "_4", 200, 200)
    thumbnail(file_out + "_5_crop.jpg", file_out + "_5", 200,200)
    thumbName = "complex_23.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 200, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial, 200 + size_h + 20, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance , 160, thumbName)
    putToBack(background_out, file_out + "_4_shadow.jpg", initial + distance * 3 + 25, 120, thumbName)
    putToBack(background_out, file_out + "_5_shadow.jpg", initial + distance * 3 + 25, 120 + size_h + 20, thumbName)


def make_24(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 5, height/2))
    crop(file_in, file_out + "_2", (0, height / 2, width / 5, height))
    crop(file_in, file_out + "_3", (width / 5, 0, width / 2 + width / 5, height))
    crop(file_in, file_out + "_4", (width / 2 + width / 5, 0, width, height / 2))
    crop(file_in, file_out + "_5", (width / 2 + width / 5, height /2 , width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", 200, 200)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", 200, 200)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbnail(file_out + "_4_crop.jpg", file_out + "_4", 200, 200)
    thumbnail(file_out + "_5_crop.jpg", file_out + "_5", 200,200)
    thumbName = "complex_24.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 120, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial, 120 + size_h + 20, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance , 160, thumbName)
    putToBack(background_out, file_out + "_4_shadow.jpg", initial + distance * 3 + 25, 200, thumbName)
    putToBack(background_out, file_out + "_5_shadow.jpg", initial + distance * 3 + 25, 200 + size_h + 20, thumbName)


def make_24(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 5, height/2))
    crop(file_in, file_out + "_2", (0, height / 2, width / 5, height))
    crop(file_in, file_out + "_3", (width / 5, 0, width / 2 + width / 5, height))
    crop(file_in, file_out + "_4", (width / 2 + width / 5, 0, width, height / 2))
    crop(file_in, file_out + "_5", (width / 2 + width / 5, height /2 , width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", 200, 200)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", 200, 200)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", from_x, from_y)
    thumbnail(file_out + "_4_crop.jpg", file_out + "_4", 200, 200)
    thumbnail(file_out + "_5_crop.jpg", file_out + "_5", 200,200)
    thumbName = "complex_24.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 120, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial, 120 + size_h + 20, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance , 160, thumbName)
    putToBack(background_out, file_out + "_4_shadow.jpg", initial + distance * 3 + 25, 200, thumbName)
    putToBack(background_out, file_out + "_5_shadow.jpg", initial + distance * 3 + 25, 200 + size_h + 20, thumbName)


def make_25(id, module, file_in, file_out, from_x, from_y, background_in,  background_out, from_x_b, from_y_b):
    initial = 625
    distance = 220
    file_out = module + "_" + file_out
    width, height = getImageSizes(file_in)
    crop(file_in, file_out + "_1", (0, 0, width / 5, height/2))
    crop(file_in, file_out + "_2", (0, height / 2, width / 5, height))
    crop(file_in, file_out + "_3", (width / 5, 0, width / 2 + width / 5, height/2))
    crop(file_in, file_out + "_4", (width / 5, height / 2, width / 2 + width / 5, height))
    crop(file_in, file_out + "_5", (width / 2 + width / 5, 0, width, height / 2))
    crop(file_in, file_out + "_6", (width / 2 + width / 5, height / 2 , width, height))
    size_w, size_h = thumbnail(file_out + "_1_crop.jpg", file_out + "_1", 200, 200)
    thumbnail(file_out + "_2_crop.jpg", file_out + "_2", 200, 200)
    thumbnail(file_out + "_3_crop.jpg", file_out + "_3", 300,300)
    thumbnail(file_out + "_4_crop.jpg", file_out + "_4", 300, 300)
    thumbnail(file_out + "_5_crop.jpg", file_out + "_5", 200, 200)
    thumbnail(file_out + "_6_crop.jpg", file_out + "_6", 200,200)
    thumbName = "complex_25.jpg"
    distance = size_w + 25
    putToBack(background_in, file_out + "_1_shadow.jpg", initial, 160, thumbName)
    putToBack(background_out, file_out + "_2_shadow.jpg", initial, 160 + size_h + 20, thumbName)
    putToBack(background_out, file_out + "_3_shadow.jpg", initial + distance, 160, thumbName)
    putToBack(background_out, file_out + "_4_shadow.jpg", initial + distance, 160 + size_h + 20, thumbName)
    putToBack(background_out, file_out + "_5_shadow.jpg", initial + distance * 3 + 25, 160, thumbName)
    putToBack(background_out, file_out + "_6_shadow.jpg", initial + distance * 3 + 25, 160 + size_h + 20, thumbName)

make_1(1, "./test/", "make_1", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background_3.jpg", "./test/complex_1.jpg", 100, 100)
# make_2(2, "make_2", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_2.jpg", 100, 100)
# make_3(3, "make_3", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_3.jpg", 100, 100)
# make_4(4, "make_4", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_4.jpg", 100, 100)
# make_5(4, "make_5", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_5.jpg", 100, 100)
# make_6(4, "make_6", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_6.jpg", 100, 100)
# # make_7(4, "make_7", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_7.jpg", 100, 100)
# make_8(5, "make_8", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_8.jpg", 100, 100)
# make_9(5, "make_9", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_9.jpg", 100, 100)
# make_10(5, "make_10", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_10.jpg", 100, 100)
# make_11(5, "make_11", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_11.jpg", 100, 100)
# make_12(5, "make_12", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_12.jpg", 100, 100)
# make_13(5, "make_13", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_13.jpg", 100, 100)
# make_14(5, "make_14", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_14.jpg", 100, 100)
# make_15(5, "make_15", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_15.jpg", 100, 100)
# make_16(5, "make_16", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_16.jpg", 100, 100)
# make_17(5, "make_17", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_17.jpg", 100, 100)
# make_18(5, "make_18", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_18.jpg", 100, 100)
# make_19(5, "make_19", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_19.jpg", 100, 100)
# make_20(5, "make_20", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_20.jpg", 100, 100)
# make_21(5, "make_21", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_21.jpg", 100, 100)
# make_22(5, "make_22", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_22.jpg", 100, 100)
# make_23(5, "make_23", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_23.jpg", 100, 100)
# make_24(5, "make_24", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_24.jpg", 100, 100)
# make_25(5, "make_25", "./bridges/bridge-2767545_1920.jpg", "xui", 400, 400, "./background.jpg", "complex_25.jpg", 100, 100)
