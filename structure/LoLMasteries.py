# region Imports
from value import LeagueValues as Lv
# endregion


class LoLMasteriesMastery:
    def __init__(self, champion_pair, level, points, points_since_last_level,
                 points_to_next_level, chest_granted, tokens_earned):
        self.champion_pair = champion_pair
        self.level = level
        self.points = points
        self.points_since_last_level = points_since_last_level
        self.points_to_next_level = points_to_next_level
        self.chest_granted = chest_granted
        self.tokens_earned = tokens_earned

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}Champion: {}\n'.format(tabs, self.champion_pair[1])
        string += '{}Level: {}\n'.format(tabs, self.level)
        string += '{}Points: {}\n'.format(tabs, self.points)
        string += '\t{}Points Since Last level: {}\n'\
            .format(tabs, self.points_since_last_level)
        if self.points_to_next_level > 0:
            string += '\t{}Points Until Next level: {}\n'\
                .format(tabs, self.points_to_next_level)
        string += '{}Tokens Earned: {}\n'.format(tabs, self.tokens_earned)
        if self.chest_granted:
            string += '{}Chest Granted.\n'.format(tabs)
        return string


class LoLMasteries:
    def __init__(self, region, name, player_id, masteries_list):
        self.region = region
        self.name = name
        self.player_id = player_id
        self.masteries_list = masteries_list

    def to_str(self, amount, use_asc, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}Name: {}\n'.format(tabs, self.name)
        string += '{}Region: {}\n'.format(tabs, Lv.regions_string_map[self.region])
        strings.append(string)
        string = ''

        if use_asc:
            self.masteries_list.reverse()
        for i, m in enumerate(self.masteries_list[:amount]):
            string += '{}\n'.format(m.to_str(depth + 1))
            if i % 10 >= 9:
                strings.append(string)
                string = ''
            elif len(self.masteries_list) - i == 1:
                strings.append(string)
        if use_asc:
            self.masteries_list.reverse()

        return strings
