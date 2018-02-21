# region Imports
from value import LeagueValues as Lv
# endregion


class LoLTotalMastery:
    def __init__(self, region, name, player_id, total_score):
        self.region = region
        self.name = name
        self.player_id = player_id
        self.total_score = total_score

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}Name: {}\n'.format(tabs, self.name)
        string += '{}Region: {}\n'.format(tabs, Lv.regions_string_map[self.region])
        string += '{}Total Mastery Score: {}\n'.format(tabs, self.total_score)
        return [string]