#!/usr/bin/env python3

from PIL import Image, ImageSequence
import numpy as np
import sys

# def effect(i):
#     print(f'{(i + 1) * 10}%')
#     def _effect(rgba):
#         rgba[0] ^= 15
#         rgba[1] = 255
#         rgba[2] = i * 25
#         return rgba
#     return _effect

try:
    path = sys.argv[1]
    with Image.open(path + '.gif') as im:
        pixs = [np.array(frame.copy().convert('RGBA')) for frame in ImageSequence.Iterator(im)]
        frames = [Image.fromarray(np.apply_along_axis(lambda a: ~a, -1, pix)) for pix in pixs[::-1]]
        # frames = [Image.fromarray(np.apply_along_axis(effect(i), -1, pix))
        #           for i, pix in enumerate(pixs[::-1])]
        frames[0].save(path + '-reversed.gif', save_all=True, append_images=frames[1:], **im.info)
except:
    pass
