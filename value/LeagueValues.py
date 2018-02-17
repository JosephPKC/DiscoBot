# region Constants
# File Paths
champions_path = 'champions\\'
# File Path Names
# emotes_file = 'emotes.json'
items_file = 'items.json'
profile_icons_file = 'profile_icons.json'
versions_file = 'versions.json'
# URL Bases
champion_gg_base_url = 'http://champion.gg/champion/'
champion_official_base_url = 'https://na.leagueoflegends.com/en/game-info/champions/'
champion_wiki_base_url = 'http://leagueoflegends.wikia.com/wiki/'
data_dragon_base_url = 'http://ddragon.leagueoflegends.com/cdn/'
match_history_base_url = 'http://matchhistory.'
versions_url = 'https://ddragon.leagueoflegends.com/api/versions.json'
# URL Parts
champion_url_part = '/data/en_US/champion/'
champion_splash_url_part = 'img/champion/splash/'
# emote_url_part = '/img/sticker/'
# emotes_json_url_part = '/data/en_US/sticker.json'
item_art_url_part = '/img/item/'
items_url_part = '/data/en_US/item.json'
match_history_url_part = '.leagueoflegends.com/en/#match-details/'
profile_icon_url_part = '/img/profileicon/'
profile_icons_json_url_part = '/data/en_US/profileicon.json'
# Default Values
default_best_players_amount = 50
default_embed_color = 0x18719
default_elo = 'platplus'
default_masteries_amount = 10
default_match_index = 1
default_match_list_amount = 10
default_region = 'na1'
# Range Values
best_players_range = [1, 200]
masteries_range = [1, -1]
match_index_range = [1, -1]
match_list_range = [1, 20]
# Split Values
best_players_split = 20
build_order_split = 20
masteries_split = 20
match_list_split = 20
match_timeline_split = 20
# Misc Values
region_optional_suffix = '1'
# endregion

# region Enumerations


# endregion


# region Mappings
# Regions
region_string_map = {
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
region_match_history_string_map = {
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
region_spectate_list_map = {
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
# Queues
queue_string_map = {
    'RANKED_FLEX_TT': 'Flex 3v3',
    'RANKED_FLEX_SR': 'Flex 5v5',
    'RANKED_SOLO_5x5': 'Solo 5v5',
    'RANKED_TEAM_3x3': 'Team 3v3',
    'RANKED_TEAM_5x5': 'Team 5v5'
}
queue_string_inverted_map = {
    'solosr': 'RANKED_SOLO_5x5',
    'solo': 'RANKED_SOLO_5x5',
    'flexsr': 'RANKED_FLEX_SR',
    'flextt': 'RANKED_FLEX_TT'
}
# Tiers
tier_string_map = {
    'MASTER': 'Master',
    'CHALLENGER': 'Challenger'
}
# Lanes
lane_string_map = {
    'TOP': 'Top',
    'JUNGLE': 'Jungle',
    'MID': 'Middle',
    'MIDDLE': 'Middle',
    'BOTTOM': 'Bottom'
}
# Roles
role_string_map = {
    'DUO_SUPPORT': 'Support',
    'DUO_CARRY': 'Carry',
    'NONE': '',
    'SOLO': 'Solo',
    'DUO': 'Duo',
    'MIDDLE': 'Middle',
    'TOP': 'Top',
    'JUNGLE': 'Jungle'
}
# Elos
elo_string_map = {
    'PLATINUM,DIAMOND,MASTER,CHALLENGER': 'Platplus',
    'PLATINUM': 'Plat',
    'GOLD': 'Gold',
    'SILVER': 'Silver',
    'BRONZE': 'Bronze'
}
elo_string_inverted_map = {
    'platplus': 'PLATINUM,DIAMOND,MASTER,CHALLENGER',
    'bronze': 'BRONZE',
    'silver': 'SILVER',
    'gold': 'GOLD',
    'platinum': 'PLATINUM',
    'diamond': 'PLATINUM,DIAMOND,MASTER,CHALLENGER',
    'master': 'PLATINUM,DIAMOND,MASTER,CHALLENGER',
    'challenger': 'PLATINUM,DIAMOND,MASTER,CHALLENGER'
}
# Events
event_string_map = {
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
# Spell Effects
spell_effect_string_map = {
    'attackdamage': 'AD',
    'spelldamage': 'AP',
    'bonusattackdamage': 'Bonus AD',
    'health': 'HP',
    'bonushealth': 'Bonus HP',
    '@special.dariusr3': ''
}
# endregion


# region Lists
queues_list = [k for k in queue_string_map.keys()]
queues_standard_list = [400, 420, 430, 440, 460, 470]
regions_list = [k for k in region_string_map.keys()]
# endregion


# region Methods
# Get/Calculate/Convert (Get)
def get_match_history_url(region, match_id, player_id=None):
    if region == 'kr':
        url = 'https://matchhistory.leagueoflegends.co.kr/ko/#match-details/KR/{}'.format(match_id)
    else:
        url = 'https://matchhistory.{}.leagueoflegends.com/en/#match-details/{}/{}'\
            .format(region_match_history_string_map[region], region.upper(), match_id)
    if player_id is not None:
        url += '/{}'.format(player_id)
    url += '?tab=overview'
    return url


def get_mins_secs_from_time(time_stamp):
    time = time_stamp / 1000 / 60
    mins = int(time)
    secs = int(time % 1 * 60)
    return mins, secs


def get_op_gg_url(region, player_name):
    player_name = player_name.replace(' ', '+')
    return 'http://{}.op.gg/summoner/userName={}'.format(region_match_history_string_map[region], player_name)


def get_player_index_in_team(player_index, number_of_players):
    return player_index % (number_of_players // 2) - 1
# endregion
