# region LoL Constants
# region Files
version_file = 'versions.json'
version_path = 'data\\json\\versions.json'
champions_path = 'champions\\'
profile_icons_path = 'profile_icons.json'
emotes_path = 'emotes.json'
items_path = 'items.json'
# endregion

# region URLs
base_official_champion_url = 'https://na.leagueoflegends.com/en/game-info/champions/'
base_wiki_champion_url =  'http://leagueoflegends.wikia.com/wiki/'
base_match_history_url = 'http://matchhistory.'
base_match_history_url_extension = '.leagueoflegends.com/en/#match-details/'
base_champion_gg_url = 'http://champion.gg/champion/'

base_url = 'http://ddragon.leagueoflegends.com/cdn/'
version_url = 'https://ddragon.leagueoflegends.com/api/versions.json'

profile_icon_json_url_part = '/data/en_US/profileicon.json'
profile_icon_url_part = '/img/profileicon/'
emote_json_url_part = '/data/en_US/sticker.json'
emote_url_part = '/img/sticker/'
champion_url_part = '/data/en_US/champion/'
champion_art_url_part = 'img/champion/splash/'
item_url_part = '/data/en_US/item.json'
item_art_url_part = '/img/item/'
# endregion

# region Defaults
default_region = 'na1'
default_recent_matches_amount = 10
default_match_index = 1
default_masteries_amount = 10
default_best_players_amount = 100
default_elo = 'platplus'
# endregion

# region Ranges
range_recent_matches = [1, 20]
range_match_index = [1, -1]
range_masteries = [1, -1]
range_best_players = [1, 200]
# endregion

# region Display String Split Amounts
split_masteries = 10
split_best_players = 25
split_match_list = 10
split_match_timeline = 10
split_build_order = 10
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

regions_match_history_string_map = {
    'br1': 'br',
    'eun1': 'eune',
    'euw1': 'euw',
    'jp1': 'jp',
    'kr': 'kr',
    'la1': 'lan',
    'la2': 'las',
    'na1': 'na',
    'oc1': 'oce',
    'tr1': 'tr',
    'ru': 'ru'
}

regions_spectate_list_map = {
    'br1': ['BR1', 'br', '80'],
    'eun1': ['EUN1', 'eu', '8088'],
    'euw1': ['EUW1', 'euw1', '80'],
    'jp1': ['JP1', 'jp1', '80'],
    'kr': ['KR', 'kr', '80'],
    'la1': ['LA1', 'la1', '80'],
    'la2': ['LA2', 'la2', '80'],
    'na1': ['NA1', 'na', '80'],
    'oc1': ['OC1', 'oc1', '80'],
    'tr1': ['TR1', 'tr', '80'],
    'ru': ['RU', 'ru', '80'],
    'pbe1': ['PBE1', 'pbe', '8088']
}

queues_string_map = {
    'RANKED_FLEX_TT': 'Flex 3v3',
    'RANKED_FLEX_SR': 'Flex 5v5',
    'RANKED_SOLO_5x5': 'Solo 5v5',
    'RANKED_TEAM_3x3': 'Team 3v3',
    'RANKED_TEAM_5x5': 'Team 5v5'
}

queues_string_map_inverted = {
    'solosr': 'RANKED_SOLO_5x5',
    'solo': 'RANKED_SOLO_5x5',
    'flexsr': 'RANKED_FLEX_SR',
    'flextt': 'RANKED_FLEX_TT'
}

tiers_string_map = {
    'MASTER': 'Master',
    'CHALLENGER': 'Challenger'
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
ch_gg_roles_string_map = {
    'DUO_SUPPORT': 'Support',
    'DUO_CARRY': 'Carry',
    'MIDDLE': 'Middle',
    'TOP': 'Top',
    'JUNGLE': 'Jungle'
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
    'ELDER_DRAGON': 'Elder Dragon',
    'BARON_NASHOR': 'Baron',
    'RIFTHERALD': 'Rift Herald',
    'VILE_MAW': 'Vile\'Maw'
}

spell_effect_burn_map = {
    'attackdamage': 'AD',
    'spelldamage': 'AP',
    'bonusattackdamage': 'Bonus AD',
    'health': 'HP',
    'bonushealth': 'Bonus HP',
    '@special.dariusr3': ''
}

elo_strings_map = {
    'platplus': 'PLATINUM,DIAMOND,MASTER,CHALLENGER',
    'bronze': 'BRONZE',
    'silver': 'SILVER',
    'gold': 'GOLD',
    'platinum': 'PLATINUM',
    'diamond': 'PLATINUM,DIAMOND,MASTER,CHALLENGER',
    'master': 'PLATINUM,DIAMOND,MASTER,CHALLENGER',
    'challenger': 'PLATINUM,DIAMOND,MASTER,CHALLENGER'
}

elo_string_map_inverted = {
    'PLATINUM,DIAMOND,MASTER,CHALLENGER': 'platplus',
    'PLATINUM': 'plat',
    'GOLD': 'gold',
    'SILVER': 'silver',
    'BRONZE': 'bronze'
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

def get_mins_secs_from_time_stamp(time_stamp):
    time = time_stamp / 1000 / 60
    mins = int(time)
    secs = int(time % 1 * 60)
    return mins, secs

def get_match_history_url(region, match_id, player_id=None):
    if region == 'kr':
        url = 'https://matchhistory.leagueoflegends.co.kr/ko/#match-details/KR/{}'.format(match_id)
    else:
        url = 'https://matchhistory.{}.leagueoflegends.com/en/#match-details/{}/{}'.format(regions_match_history_string_map[region], region.upper(), match_id)
    if player_id is not None:
        url += '/{}'.format(player_id)
    url += '?tab=overview'
    return url
# endregion
