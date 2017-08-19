import os
import re
import fnmatch
import requests
from PIL import Image
from resizeimage import resizeimage

PREFIX = '\\'


def generic_except(e):
    print('{}: {}'.format(type(e).__name__, e))

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def download_file(url, save_path):
    # print(url)
    # print(save_path)
    with open(save_path, 'wb') as f:
        f.write(requests
                .get(url).content)

def shrink_image(image, save_path, height, width):
    with open(image, 'r+b') as f:
        with Image.open(f) as image:
            cover = resizeimage.resize_cover(image, [height, width])
            cover.save(save_path, image.format)

def parse_into_two(string, split):
    splits = re.split(split, string)
    first, second = splits[0], (splits[1] if len(splits) > 1 else None)
    return first, second

def champion_base_as(offset):
    return 0.625 / (1 + offset)