# region Imports
import fnmatch
import json
import os
import requests

from value import GeneralValues as Gv
# endregion


class FileManager:
    def __init__(self):
        # Nothing
        return

    def find_file(self, file_type, name, pattern):
        if not isinstance(file_type, Gv.FileType):
            return False
        for root, dirs, files in os.walk(self.__create_path(file_type, name)):
            for f in files:
                if fnmatch.fnmatch(f, pattern):
                    return True
        return False

    def download_file(self, file_type, name, url, force_download=False):
        if not isinstance(file_type, Gv.FileType):
            return
        if self.find_file(file_type, name, name) and not force_download:
            return
        with open(self.__create_path(file_type, name), 'wb') as file:
            file.write(requests.get(url).content)

    def load_json(self, path):
        with open(self.__create_path(Gv.FileType.JSON, path), 'r', encoding='utf-8') as file:
            j_file = json.loads(file.read())
        return j_file

    def __create_path(self, file_type, name):
        return Gv.general_path_prefix + Gv.file_type_path_map[file_type] + name


