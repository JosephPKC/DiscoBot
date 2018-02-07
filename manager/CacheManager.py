# region Imports
import datetime

from enum import Enum
# endregion


class CacheType(Enum):
    NONE = 0
    DB = 1
    API = 2
    STR = 3


class Cache:
    def __init__(self, item, freshness):
        self.item = item
        self.freshness = freshness

    def __str__(self):
        return '{} @ {}'.format(self.item, self.freshness)


class CacheManager:
    def __init__(self, db_freshness, api_freshness, str_freshness):
        self.__db_cache = {}
        self.__api_cache = {}
        self.__str_cache = {}

        self.__db_freshness = db_freshness
        self.__api_freshness = api_freshness
        self.__str_freshness = str_freshness

    def clean_up(self):
        self.__db_cache = self.__get_cleaned_cache(self.__db_cache, self.__db_freshness)
        self.__api_cache = self.__get_cleaned_cache(self.__api_cache, self.__api_freshness)
        self.__str_cache = self.__get_cleaned_cache(self.__str_cache, self.__str_freshness)

    def retrieve(self, key, cache_type):
        cache = self.__determine_cache(cache_type)
        freshness = self.__determine_freshness(cache_type)
        if not self.__is_exist(cache, key):
            return None
        if not self.__is_fresh(cache, freshness, key):
            return None
        cache[key].freshness = datetime.datetime.now()
        return cache[key].item

    def add(self, key, item, cache_type):
        cache = self.__determine_cache(cache_type)
        cache[key] = Cache(item, datetime.datetime.now())

    def __determine_cache(self, cache_type):
        if cache_type == CacheType.DB:
            return self.__db_cache
        elif cache_type == CacheType.API:
            return self.__api_cache
        elif cache_type == CacheType.STR:
            return self.__str_cache
        else:
            return None

    def __determine_freshness(self, cache_type):
        if cache_type == CacheType.DB:
            return self.__db_freshness
        elif cache_type == CacheType.API:
            return self.__api_freshness
        elif cache_type == CacheType.STR:
            return self.__str_freshness
        else:
            return None

    def __get_cleaned_cache(self, cache, freshness):
        return {k: v for k, v in cache.items() if self.__is_fresh(cache, freshness, k)}

    def __str__(self):
        return 'DB: {}\nAPI: {}\nSTR: {}'.format(self.__db_cache, self.__api_cache, self.__str_cache)

    @staticmethod
    def __is_fresh(cache, freshness, key):
        duration = (datetime.datetime.now() - cache[key].freshness).total_seconds() / 60
        return duration <= freshness

    @staticmethod
    def __is_exist(cache, key):
        return key in cache
