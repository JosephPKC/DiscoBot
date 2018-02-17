import random
import requests
from manager import CacheManager as Cache, FileManager as File
from value import LeagueValues as Lv


# region Classes

# endregion


# region Fields
__current_patch = None
# endregion


# region Methods
def __get_latest_patch():
    File.download_file(File.FileType.JSON, Lv.versions_file, Lv.versions_url)
    return File.load_json(Lv.versions_file)[0]


def get_current_patch():
    return __current_patch


def init():
    global __current_patch
    __current_patch = __get_latest_patch()
    

def get_champion(champion_name):
    url = '{}{}{}{}.json'.format(Lv.data_dragon_base_url, __current_patch, Lv.champion_url_part, champion_name)
    path = '{}{}_{}.json'.format(Lv.champions_path, __current_patch, champion_name)
    key = (__current_patch, champion_name, Cache.ApiKey.LoL.CHAMPION)

    cached = Cache.retrieve(key, Cache.CacheType.API)
    if cached is None:
        try:
            File.download_file(File.FileType.JSON, path, url)
        except requests.HTTPError as e:
            print('HTTP ERROR: {}'.format(e))
            return None
        cached = File.load_json(path)['data'][champion_name]
        Cache.add(key, cached, Cache.CacheType.API)

    return cached


def get_champion_splashes(champion_name):
    cached = get_champion(champion_name)
    if cached is None:
        return None

    art = []
    for s in cached['skins']:
        art.append([s['name'], '{}{}{}_{}.jpg'
                   .format(Lv.data_dragon_base_url, Lv.champion_splash_url_part, champion_name, s['num'])])
    return cached


# def get_emote(emote_id, use_random=False):
#     json_url = '{}{}{}'.format(Lv.base_url, __current_patch,
#                                  Lv.emote_json_url_part)
#     path = '{}_{}'.format(__current_patch, Lv.emotes_path)
#     key = (__current_patch, Cache.ApiKey.LOL_EMOTES)
#     cached = Cache.retrieve(key, Cache.CacheType.API)
#     if cached is None:
#         # Download file
#         try:
#             File.download_file(Gv.FileType.JSON, path, json_url)
#         except requests.HTTPError as e:
#             print('HTTP ERROR: {}'.format(e))
#             return None
#         # Open file
#         cached = File.load_json(path)['data']
#         Cache.add(key, cached, Cache.CacheType.API)
#     if use_random:
#         size = len(cached.keys())
#         index = int(random.random() * (size - 1))
#         emote_id = list(cached.keys())[index]
#     elif emote_id not in cached:
#         return None
#     return '{}{}{}{}.png'.format(Lv.base_url, __current_patch,
#                                  Lv.emote_url_part, emote_id)


def get_item(item_id):
    url = '{}{}{}'.format(Lv.data_dragon_base_url, __current_patch, Lv.items_url_part)
    path = '{}_{}'.format(__current_patch, Lv.items_file)
    key = (__current_patch, Cache.ApiKey.LoL.ITEMS)

    cached = Cache.retrieve(key, Cache.CacheType.API)
    if cached is None:
        try:
            File.download_file(File.FileType.JSON, path, url)
        except requests.HTTPError as e:
            print('HTTP ERROR: {}'.format(e))
            return None
        cached = File.load_json(path)['data']
        Cache.add(key, cached, Cache.CacheType.API)

    return cached[str(item_id)]


def get_profile_icon(icon_id, use_random=False):
    json_url = '{}{}{}'.format(Lv.data_dragon_base_url, __current_patch, Lv.profile_icons_json_url_part)
    path = '{}_{}'.format(__current_patch, Lv.profile_icons_file)
    key = (__current_patch, Cache.ApiKey.LoL.PROFILE_ICONS)

    cached = Cache.retrieve(key, Cache.CacheType.API)
    if cached is None:
        try:
            File.download_file(File.FileType.JSON, path, json_url)
        except requests.HTTPError as e:
            print('HTTP ERROR: {}'.format(e))
            return None
        cached = File.load_json(path)['data']
        Cache.add(key, cached, Cache.CacheType.API)

    if use_random:
        size = len(cached.keys())
        index = int(random.random() * (size - 1))
        icon_id = list(cached.keys())[index]
    elif str(icon_id) not in cached:
        return None

    return '{}{}{}{}.png'.format(Lv.data_dragon_base_url, __current_patch, Lv.profile_icon_url_part, icon_id)
# endregion
