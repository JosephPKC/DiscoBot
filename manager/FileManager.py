from enum import Enum
import fnmatch
import json
import os
import requests


# region Classes
class FileType(Enum):
    META = 0
    IMG = 1
    JSON = 2
# endregion


# region Fields
__file_type_path_map = {
    FileType.META: 'data\\',
    FileType.IMG: 'data\\img\\',
    FileType.JSON: 'data\\json\\'
}
# endregion


# region Methods
def __create_path(file_type, name):
    return __file_type_path_map[file_type] + name


def download_file(file_type, name, url, force_download=False):
    if not isinstance(file_type, FileType):
        return
    if find_file(file_type, name, name) and not force_download:
        return
    with open(__create_path(file_type, name), 'wb') as file:
        file.write(requests.get(url).content)


def find_file(file_type, name, pattern):
    if not isinstance(file_type, FileType):
        return False
    for root, dirs, files in os.walk(__create_path(file_type, name)):
        for f in files:
            if fnmatch.fnmatch(f, pattern):
                return True
    return False


def load_json(path):
    with open(__create_path(FileType.JSON, path), 'r', encoding='utf-8') as file:
        j_file = json.loads(file.read())
    return j_file
# endregion
