# region Imports
import fnmatch
import os
import requests

from value import GeneralValues as Gv
# endregion


class FileManager:
    def __init__(self, path):
        self.path = path

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

    def __create_path(self, file_type, name):
        return self.path + Gv.file_type_path_map[file_type] + name
