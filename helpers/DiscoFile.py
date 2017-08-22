import os       # Used for find_file()
import fnmatch  # Used for find_file()
import requests # Used for download_file()
import json     # Used for load_json()

try:            # Used for scale_image()
    from PIL import Image
    from resizeimage import resizeimage
except ImportError:
    print('PIL and resizeimage not found.')

try:            # Used for upload_file()
    import discord
except ImportError:
    print('Discord module not found.')


def find_file(pattern, path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return True
    return False

def download_file(url, path):
    with open(path, 'wb') as f:
        f.write(requests.get(url).content)

async def upload_file(path, bot, channel):
    with open(path, 'rb') as f:
        await bot.send_file(channel, f)

def scale_image(path, new_path, height, width):
    with open(path, 'r+b') as f:
        with Image.open(f) as image:
            cover = resizeimage.resize_cover(image, [height, width])
            cover.save(new_path, image.format)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        j_file = json.loads(f.read())
    return j_file