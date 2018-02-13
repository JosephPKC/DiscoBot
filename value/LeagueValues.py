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
default_amount_range_match_list = [1, 20]
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

lanes_string_map = {
    'TOP': 'Top',
    'JUNGLE': 'Jungle',
    'MID': 'Middle',
    'MIDDLE': 'Middle',
    'BOTTOM': 'Bottom'
}

roles_string_map = {
    'DUO_SUPPORT': 'Support',
    'DUO_CARRY': 'Carry',
    'NONE': '',
    'SOLO': 'Solo',
    'DUO': 'Duo'
}

events_string_map = {
    'NEXUS_TURRET': 'Nexus Tower',
    'MID_LANE': 'Middle Lane',
    'BOT_LANE': 'Bottom Lane',
    'TOP_LANE': 'Top Lane',
    'INHIBITOR_BUILDING': 'Inhibitor',
    'INNER_TURRET': 'Inner Tower',
    'OUTER_TURRET': 'Outer Tower',
    'BASE_TURRET': 'Inhibitor Tower',
    'WATER_DRAGON': 'Ocean Dragon',
    'AIR_DRAGON': 'Cloud Dragon',
    'EARTH_DRAGON': 'Mountain Dragon',
    'FIRE_DRAGON': 'Infernal Dragon',
    'BARON_NASHOR': 'Baron',
    'RIFT_HERALD': 'Rift Herald',
    'VILE_MAW': 'Vile\'Maw'
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

# region Methods
def player_to_in_team(index, num_of_players):
    return index % (num_of_players // 2) - 1
# endregion
