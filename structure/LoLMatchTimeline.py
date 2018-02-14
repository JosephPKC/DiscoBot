# region Imports
from value import LeagueValues as Lv
# endregion


class LoLMatchTimelineEvent:
    def __init__(self, event_type, time_stamp, description, killer, victim, assists_list, team_id):
        self.event_type = event_type
        self.time_stamp = time_stamp
        self.description = description
        self.killer = killer
        self.victim = victim
        self.assists_list = assists_list
        self.team_id = team_id

    def to_str(self, depth=0):
        tabs = '\t' * depth
        team_string = '1' if self.team_id == 100 else '2'
        time = self.time_stamp / 1000 / 60
        mins = int(time)
        secs = int(time % 1 * 60)
        string = '{}@{}:{:02d}\n'.format(tabs, mins, secs)
        string += '{}Team {} '.format(tabs, team_string)
        if self.event_type == 'CHAMPION_KILL':
            string += 'has slain {}.\n'.format(self.victim)
        elif self.event_type == 'BUILDING_KILL':
            string += 'has destroyed {}.\n'.format(self.description)
        else:
            string += 'has slain {}.\n'.format(self.description)
        string += '\t{}By {}\n'.format(tabs, self.killer)
        if self.assists_list:
            string += '\t{}Assisted By:\n'.format(tabs)
        for a in self.assists_list:
            string += '\t\t{}{}\n'.format(tabs, a)
        return string


class LoLMatchTimelineTeam:
    def __init__(self, team_id, is_winner, player_pair_list):
        self.team_id = team_id
        self.is_winner = is_winner
        self.player_pair_list = player_pair_list


class LoLMatchTimeline:
    def __init__(self, region, match_id, teams_list, events_list):
        self.region = region
        self.match_id = match_id
        self.teams_list = teams_list
        self.events_list = events_list

    def to_str(self, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}Match ID: {}\n'.format(tabs, self.match_id)
        string += '{}Region: {}\n'.format(tabs, Lv.regions_string_map[self.region])

        for t in self.teams_list:
            string += '{}Team {}:\n'.format(tabs, t.team_id // 100)
            if t.is_winner:
                string += '\t{}VICTORY.\n'.format(tabs)
            else:
                string += '\t{}DEFEAT.\n'.format(tabs)
            for i, p in enumerate(t.player_pair_list):
                string += '\t{}{}. {}: {}\n'.format(tabs, i + 1, p[0], p[1])
        strings.append(string)
        string = ''
        for i, e in enumerate(self.events_list):
            string += '{}\n'.format(e.to_str(depth + 1))
            if i % Lv.split_match_timeline >= Lv.split_match_timeline - 1:
                strings.append(string)
                string = ''
            elif len(self.events_list) - i == 1:
                strings.append(string)
        return strings

        