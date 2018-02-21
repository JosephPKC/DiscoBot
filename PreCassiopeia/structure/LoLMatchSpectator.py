# region Imports
from value import LeagueValues as Lv, GeneralValues as Gv
# endregion


class LoLMatchSpectatorTeamPlayer:
    def __init__(self, name, spell_pair, champion, is_bot, runes_list, primary, secondary):
        self.name = name
        self.spell_pair = spell_pair
        self.champion = champion
        self.is_bot = is_bot
        self.runes_list = runes_list
        self.primary = primary
        self.secondary = secondary

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}{}'.format(tabs, self.name)
        if self.is_bot:
            string += 'Bot'
        string += '\n'
        string += '{}Champion: {}\n'.format(tabs, self.champion)
        string += '{}Summoner Spells: {}, {}\n'.format(tabs, self.spell_pair[0], self.spell_pair[1])
        string += '{}Primary: {}\n'.format(tabs, self.primary)
        for r in self.runes_list[:4]:
            string += '\t{}{}\n'.format(tabs, r)
        string += '{}Secondary: {}\n'.format(tabs, self.secondary)
        for r in self.runes_list[4:]:
            string += '\t{}{}\n'.format(tabs, r)
        return string


class LoLMatchSpectatorTeam:
    def __init__(self,  team_id, players_list):
        self.team_id = team_id
        self.players_list = players_list

    def to_str(self, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}Team {}\n'.format(tabs, self.team_id // 100)
        for p in self.players_list:
            string += '{}'.format(p.to_str(depth + 1))
            strings.append(string)
            string = ''
        return strings


class LoLMatchSpectator:
    def __init__(self, region, match_id, queue, encryption_key, duration, teams_list):
        self.region = region
        self.match_id = match_id
        self.queue = queue
        self.encryption_key = encryption_key
        self.duration = duration
        self.teams_list = teams_list

    def to_str(self, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}Match ID: {}\n'. format(tabs, self.match_id)
        string += '{}Region: {}\n'.format(tabs, Lv.regions_string_map[self.region])
        string += '{}Queue: {}\n'.format(tabs, self.queue)
        mins, secs = Gv.get_minutes_seconds(self.duration)
        string += '{}Time Elapsed: {}:{:02d} ({}:{:02d})\n\n'.format(tabs, int(mins), secs,
                                                                     int(mins) + 3, secs)
        string += '{}Encryption Key: {}\n'.format(tabs, self.encryption_key)
        strings.append(string)

        for t in self.teams_list:
            for s in t.to_str(depth):
                strings.append(s)
        return strings
