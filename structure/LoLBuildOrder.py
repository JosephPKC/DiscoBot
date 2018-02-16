# region Imports
import math

from value import LeagueValues as Lv, GeneralValues as Gv
# endregion


class LoLBuildOrderEvent:
    def __init__(self, event_type, time_stamp, item):
        self.event_type = event_type
        self.time_stamp = time_stamp
        self.item = item

    def to_str(self, depth=0):
        tabs = '\t' * depth
        mins, secs = Lv.get_mins_secs_from_time_stamp(self.time_stamp)
        string = '{}@{}:{:02d}\n'.format(tabs, mins, secs)
        if self.event_type == 'ITEM_PURCHASED':
            string += '{}Purchased/Got: {}\n'.format(tabs, self.item)
        else:
            string += '{}Sold/Used/Removed: {}\n'.format(tabs, self.item)
        return string


class LoLBuildOrder:
    def __init__(self, region, name, player_id, match_id, champion, events):
        self.region = region
        self.name = name
        self.player_id = player_id
        self.match_id = match_id
        self.champion = champion
        self.events = events

    def to_str(self, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}Match ID: {}\n'.format(tabs, self.match_id)
        string += '{}Name: {}\n'.format(tabs, self.name)
        string += '{}Region: {}\n'.format(tabs, Lv.regions_string_map[self.region])
        string += '{}Champion: {}\n'.format(tabs, self.champion)
        strings.append(string)
        string = ''

        for i, e in enumerate(self.events):
            string += '{}\n'.format(e.to_str(depth))
            if i % Lv.split_build_order >= Lv.split_build_order - 1:
                strings.append(string)
                string = ''
            elif len(self.events) - i == 1:
                strings.append(string)
        return strings