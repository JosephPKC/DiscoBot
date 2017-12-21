import fnmatch
import os
import requests

from Data.values import Generalvals as gv
'''
Download Manager:
-Download files
-Don't download unless the file does not exist, or a forced overwrite is enabled
'''

class DownloadManager:
    def __init__(self):
        self.path = 'Data\\'

    def find_file(self, pattern, type, name):
        if not isinstance(type, gv.DataType):
            return

        path = self.__create_path(type, name)
        for root, dirs, files in os.walk(path):
            for n in files:
                if fnmatch.fnmatch(n, pattern):
                    return True
        return False

    def download_file(self, type, name, url, force=False):
        if not isinstance(type, gv.DataType):
            return

        path = self.__create_path(type, name)
        if self.find_file(name, type, name) and not force:
            return

        with open(path, 'wb') as f:
            f.write(requests.get(url).content)

    def __create_path(self, type, name):
        return self.path + gv.datatype_path_map[type] + name