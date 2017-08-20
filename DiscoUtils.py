import os
import re
import fnmatch
import requests
from PIL import Image
from resizeimage import resizeimage

# region General
PREFIX = '\\'
DEBUG = False
VERBOSE = False
# endregion

# region LoL
DOWNLOAD = False
DETAILED_SPELLS = False
# endregion

def generic_except(e):
    print('{}: {}'.format(type(e).__name__, e))


def parse_into_two(string, split):
    splits = re.split(split, string)
    first, second = splits[0], (splits[1] if len(splits) > 1 else None)
    return first, second

def champion_base_as(offset):
    return 0.625 / (1 + offset)

def sub_line_breaks(string):
    return string.replace('<br><br>', '\n\t').replace('<br>', '\n')