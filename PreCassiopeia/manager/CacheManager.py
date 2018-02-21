import datetime
from enum import Enum
from value import GeneralValues as Gv


# region Classes
class CacheType(Enum):
    NONE = 0
    API = 1
    DB = 2
    STR = 3


class ApiKey:
    class LoL(Enum):
        NONE = 0
        PLAYER = 1
        RANKS = 2
        MATCH_LIST = 3
        MATCH = 4
        MATCH_TIMELINE = 5
        MASTERY = 6
        TOTAL_MASTERY = 7
        MATCH_LIST_FULL = 8
        CHALLENGERS = 9
        MASTERS = 10
        STATUS = 11
        SPECTATOR = 12
        CHAMPION = 13
        PROFILE_ICONS = 14
        ITEMS = 15
        CHAMPION_STATS = 16


class StrKey:
    class LoL(Enum):
        NONE = 0
        PLAYER = 1
        MATCH_LIST = 2
        MATCH_DETAILED = 3
        MATCH_TIMELINE = 4
        MASTERY = 5
        CHALLENGERS = 6
        MASTERS = 7
        STATUS = 8
        SPECTATOR = 9
        CHAMPION = 10
        CHAMPION_SPLASHES = 11
        BUILD_ORDER = 12
        ITEM = 13
        CHAMPION_STATS = 14


class Cache:
    def __init__(self, item, freshness):
        self.item = item
        self.freshness = freshness

    def __str__(self):
        return '{} @ {}'.format(self.item, self.freshness)
# endregion


# region Fields
__api_cache = {}
__db_cache = {}
__str_cache = {}
# endregion


# region Methods
def __get_cache(cache_type):
    if cache_type == CacheType.API:
        return __api_cache
    elif cache_type == CacheType.DB:
        return __db_cache
    elif cache_type == CacheType.STR:
        return __str_cache
    else:
        return None


def __get_freshness(cache_type):
    if cache_type == CacheType.API:
        return Gv.api_freshness
    elif cache_type == CacheType.DB:
        return Gv.db_freshness
    elif cache_type == CacheType.STR:
        return Gv.str_freshness
    else:
        return None


def __get_cleaned_cache(cache, freshness):
    return {k: v for k, v in cache.items() if __is_fresh(cache, freshness, k)}


def __is_exist(cache, key):
    return key in cache


def __is_fresh(cache, freshness, key):
    duration = (datetime.datetime.now() - cache[key].freshness).total_seconds() / 60
    return duration <= freshness


def __print_cache(key, found):
    print('{}: {}.'.format('FOUND' if found else 'NOT FOUND', key))


def add(key, item, cache_type):
    cache = __get_cache(cache_type)
    cache[key] = Cache(item, datetime.datetime.now())


def clean_up():
    global __api_cache, __db_cache, __str_cache
    __db_cache = __get_cleaned_cache(__db_cache, Gv.db_freshness)
    __api_cache = __get_cleaned_cache(__api_cache, Gv.api_freshness)
    __str_cache = __get_cleaned_cache(__str_cache, Gv.str_freshness)


def retrieve(key, cache_type):
    cache = __get_cache(cache_type)
    freshness = __get_freshness(cache_type)
    if not __is_exist(cache, key):
        __print_cache(key, False)
        return None
    if not __is_fresh(cache, freshness, key):
        __print_cache(key, False)
        return None
    __print_cache(key, True)
    return cache[key].item
# endregion
