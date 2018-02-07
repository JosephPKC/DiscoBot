# region LoL Constants
# region Files
version_file = 'versions.json'
version_path = 'data\\json\\versions.json'
# endregion

# region URLs
base_url = 'http://ddragon.leagueoflegends.com/cdn/'
version_url = 'https://ddragon.leagueoflegends.com/api/versions.json'
profile_icon_url_part = '/img/profileicon/'
# endregion

# region Defaults
default_region = 'na1'
# endregion

# region Mappings
regions_string_map = {
    'br1': 'BR',
    'eun1': 'EUN',
    'euw1': 'EUW',
    'jp1': 'JP',
    'kr': 'KR',
    'la1': 'LAN',
    'la2': 'LAS',
    'na1': 'NA',
    'oc1': 'OC',
    'tr1': 'TR',
    'ru': 'RU',
    'pbe1': 'PBE'
}

queues_string_map = {
    'RANKED_FLEX_TT': 'Flex 3v3',
    'RANKED_FLEX_SR': 'Flex 5v5',
    'RANKED_SOLO_5x5': 'Solo 5v5',
    'RANKED_TEAM_3x3': 'Team 3v3',
    'RANKED_TEAM_5x5': 'Team 5v5'
}
# endregion

# region Lists
regions_list = [k for k in regions_string_map.keys()]
queues_list = [k for k in queues_string_map.keys()]
# endregion

# region Misc
optional_region_suffix = '1'
# endregion
# endregion
