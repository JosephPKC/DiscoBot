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
db_freshness = 300
api_freshness = 30
str_freshness = 30
# endregion

# region Methods


def print_cache(key, found):
    print('{}: {}.'.format('FOUND' if found else 'NOT FOUND', key))


def get_minutes_seconds(time_in_s):
    return time_in_s / 60, time_in_s % 60
# endregion
