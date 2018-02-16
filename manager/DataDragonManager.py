# region Imports
import json
import random
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
        path = '{}{}_{}.json'.format(Lv.champions_path, self.__current_patch, champion_name)
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

    def get_profile_icon(self, icon_id, use_random=False):
        json_url = '{}{}{}'.format(Lv.base_url, self.__current_patch,
                                     Lv.profile_icon_json_url_part)
        path = '{}_{}'.format(self.__current_patch, Lv.profile_icons_path)
        api_key = (self.__current_patch, Gv.CacheKeyType.API_LOL_PROFILE_ICONS)
        cached = self.__cache.retrieve(api_key, CacheManager.CacheType.API)
        if cached is None:
            # Download file
            try:
                self.__file.download_file(Gv.FileType.JSON, path, json_url)
            except requests.HTTPError as e:
                print('HTTP ERROR: {}'.format(e))
                return None
            # Open file
            cached = self.__file.load_json(path)['data']
            self.__cache.add(api_key, cached, CacheManager.CacheType.API)
        if use_random:
            size = len(cached.keys())
            index = int(random.random() * (size - 1))
            icon_id = list(cached.keys())[index]
        elif icon_id not in cached:
            return None
        return '{}{}{}{}.png'.format(Lv.base_url, self.__current_patch,
                                     Lv.profile_icon_url_part, icon_id)

    def get_emote(self, emote_id, use_random=False):
        json_url = '{}{}{}'.format(Lv.base_url, self.__current_patch,
                                     Lv.emote_json_url_part)
        path = '{}_{}'.format(self.__current_patch, Lv.emotes_path)
        api_key = (self.__current_patch, Gv.CacheKeyType.API_LOL_EMOTES)
        cached = self.__cache.retrieve(api_key, CacheManager.CacheType.API)
        if cached is None:
            # Download file
            try:
                self.__file.download_file(Gv.FileType.JSON, path, json_url)
            except requests.HTTPError as e:
                print('HTTP ERROR: {}'.format(e))
                return None
            # Open file
            cached = self.__file.load_json(path)['data']
            self.__cache.add(api_key, cached, CacheManager.CacheType.API)
        if use_random:
            size = len(cached.keys())
            index = int(random.random() * (size - 1))
            emote_id = list(cached.keys())[index]
        elif emote_id not in cached:
            return None
        return '{}{}{}{}.png'.format(Lv.base_url, self.__current_patch,
                                     Lv.emote_url_part, emote_id)

    def get_item(self, item_id):
        # Will return a dictionary containing the json data, and a list of image urls
        url = '{}{}{}'.format(Lv.base_url, self.__current_patch,
                                     Lv.item_url_part)
        path = '{}_{}'.format(self.__current_patch, Lv.items_path)
        api_key = (self.__current_patch, Gv.CacheKeyType.API_LOL_ITEM)
        cached = self.__cache.retrieve(api_key, CacheManager.CacheType.API)
        if cached is None:
            # Download file
            try:
                self.__file.download_file(Gv.FileType.JSON, path, url)
            except requests.HTTPError as e:
                print('HTTP ERROR: {}'.format(e))
                return None
            # Open file
            cached = self.__file.load_json(path)['data']
            self.__cache.add(api_key, cached, CacheManager.CacheType.API)
        return cached[str(item_id)]
    # endregion

    # region Helpers
    def __get_latest_patch(self):
        self.__file.download_file(Gv.FileType.JSON, Lv.version_file, Lv.version_url)
        with open(Lv.version_path, 'r', encoding='utf-8') as file:
            json_file = json.loads(file.read())
        return json_file[0]
    # endregion
