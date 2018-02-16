# region Imports
from enum import Enum
# endregion


# region General Enumerations
# File Types
class FileType(Enum):
    META = 0
    IMG = 1
    JSON = 2


# Cache Key Types
class CacheKeyType(Enum):
    STR_LOL_PLAYER = 1
    API_LOL_PLAYER = 2
    API_LOL_RANKS = 3
    STR_LOL_MATCH_LIST = 4
    API_LOL_MATCH_LIST = 5
    API_LOL_MATCH = 6
    STR_LOL_MATCH_DETAILED = 7
    STR_LOL_MATCH_TIMELINE = 8
    API_LOL_MATCH_TIMELINE = 9
    STR_LOL_MASTERY = 10
    API_LOL_MASTERY = 11
    STR_LOL_TOTAL_MASTERY = 12
    API_LOL_TOTAL_MASTERY = 13
    API_LOL_MATCH_LIST_FULL = 14
    STR_LOL_CHALLENGERS = 15
    API_LOL_CHALLENGERS = 16
    STR_LOL_MASTERS = 17
    API_LOL_MASTERS = 18
    STR_LOL_STATUS = 19
    API_LOL_STATUS = 20
    STR_LOL_SPECTATE = 21
    API_LOL_SPECTATE = 22
    STR_LOL_CHAMPION = 23
    API_LOL_CHAMPION = 24
    STR_LOL_CHAMPION_ART = 25
    STR_LOL_BUILD_ORDER = 26
    API_LOL_PROFILE_ICONS = 27
    STR_LOL_ITEM = 28
    API_LOL_ITEM = 29
    API_LOL_EMOTES = 30
    STR_LOL_CHAMPION_STATS = 31
    API_LOL_CHAMPION_STATS = 32
# endregion


# region General Mappings
# Map File Type to Path Prefix
file_type_path_map = {
    FileType.META: '',
    FileType.IMG: 'img\\',
    FileType.JSON: 'json\\'
}
# endregion


# region General Constants
# Paths
general_path_prefix = 'data\\'
lol_db_path = 'data\\LoLStaticData.db'

# Prefix
argument_prefix = '-'
argument_value_prefix = '='

# Time, Durations
db_freshness = 60
api_freshness = 30
str_freshness = 30
# endregion

# region Methods


def print_cache(key, found):
    print('{}: {}.'.format('FOUND' if found else 'NOT FOUND', key))


def get_minutes_seconds(time_in_s):
    return time_in_s / 60, time_in_s % 60
# endregion
