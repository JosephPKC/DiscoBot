# region Imports
from value import LeagueValues as Lv
# endregion


class LoLMatch:
    def __init__(self, region, match_id, champion_pair,
                 queue_pair, season_pair,
                 role_id, lane_id, kda_triple, cs, cc,
                 vision, is_win, is_lanes=True):
        self.region = region
        self.match_id = match_id
        self.champion_pair = champion_pair
        self.queue_pair = queue_pair
        self.season_pair = season_pair
        self.role_id = role_id
        self.lane_id = lane_id
        self.kda_triple = kda_triple
        self.cs = cs
        self.cc = cc
        self.vision = vision
        self.is_win = is_win
        self.is_lanes = is_lanes

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}{}\n'.format(tabs, 'VICTORY' if self.is_win else 'DEFEAT')
        string += '{}Match ID: {}\n'.format(tabs, self.match_id)
        string += '{}{}\n'.format(tabs, self.season_pair[1])
        string += '{}{}\n'.format(tabs, self.queue_pair[1])
        string += '{}Champion: {}\n'.format(tabs, self.champion_pair[1])
        if self.is_lanes:
            string += '{}Lane: {} {}\n'.format(tabs,
                                               Lv.lanes_string_map[self.lane_id],
                                               Lv.roles_string_map[self.role_id])
        string += '{}KDA: {}/{}/{}\n'.format(tabs, self.kda_triple[0], self.kda_triple[1], self.kda_triple[2])
        string += '{}CS: {}, CC: {}, Vision: {}\n'.format(tabs, self.cs, self.cc, self.vision)
        return [string]


class LoLMatchList:
    def __init__(self, region, name, player_id, account_id, matches):
        self.region = region
        self.name = name
        self.player_id = player_id
        self.account_id = account_id
        self.matches = matches

    def to_str(self, amount, depth=0):
        if amount < 0 or amount > len(self.matches):
            return None
        tabs = '\t' * depth
        strings = []
        string = '{}Name: {}\n'.format(tabs, self.name)
        string += '{}Region: {}\n'.format(tabs, Lv.regions_string_map[self.region])
        string += '{}Recent Matches:\n'.format(tabs)
        strings.append(string)
        string = ''
        for i, m in enumerate(self.matches[:amount]):
            if i % 10 < 9:
                string += '{}\n'.format(m.to_str(depth + 1)[0])
            else:
                string += '{}\n'.format(m.to_str(depth + 1)[0])

                strings.append(string)
                string = ''
            if i % 10 < 9 and len(self.matches[:amount]) - i == 1:
                strings.append(string)
        return strings
