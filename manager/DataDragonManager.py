# region Imports
import json
import requests

from manager import CacheManager, FileManager
from value import GeneralValues as Gv, LeagueValues as Lv
# endregion
# This will wrap the data dragon url calls.


class DataDragonManager:
    def __init__(self, file, cache):
        self.__file = file
        self.__cache = cache
        self.__current_patch = self.__get_latest_patch()

    # region Core Retrieval
    def get_current_patch(self):
        return self.__current_patch

    def get_champion(self, champion_name):
        # Will return a dictionary containing the json data, and a list of image urls
        url = '{}{}{}{}.json'.format(Lv.base_url, self.__current_patch,
                                     Lv.champion_url_part, champion_name)
        path = '{}{}.json'.format(Lv.champions_path, champion_name)
        api_key = (self.__current_patch, champion_name, Gv.CacheKeyType.API_LOL_CHAMPION)
        cached = self.__cache.retrieve(api_key, CacheManager.CacheType.API)
        if cached is None:
            # Download file
            try:
                self.__file.download_file(Gv.FileType.JSON, path, url)
            except requests.HTTPError as e:
                print('HTTP ERROR: {}'.format(e))
                return None
            # Open file
            cached = self.__file.load_json(path)['data'][champion_name]
            self.__cache.add(api_key, cached, CacheManager.CacheType.API)
        art = []
        for s in cached['skins']:
            art.append(
                [s['name'], '{}{}{}_{}.jpg'
                    .format(Lv.base_url, Lv.champion_art_url_part,champion_name, s['num'])]
            )
        return cached, art
    # endregion

    # region Helpers
    def __get_latest_patch(self):
        self.__file.download_file(Gv.FileType.JSON, Lv.version_file, Lv.version_url)
        with open(Lv.version_path, 'r', encoding='utf-8') as file:
            json_file = json.loads(file.read())
        return json_file[0]
    # endregion
