# region Imports
from value import LeagueValues as Lv
# endregion


class LoLBestPlayersPlayer:
    def __init__(self, player_id, name, lp, rank, wins, losses,
                 is_veteran, is_inactive, is_fresh_blood, is_hot_streak):
        self.player_id = player_id
        self.name = name
        self.lp = lp
        self.rank = rank
        self.wins = wins
        self.losses = losses
        self.is_veteran = is_veteran
        self.is_inactive = is_inactive
        self.is_fresh_blood = is_fresh_blood
        self.is_hot_streak = is_hot_streak

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}{}:\n'.format(tabs, self.name)
        string += '\t{}{} LP\n'.format(tabs, self.lp)
        string += '\t{}{} wins, {} losses, {:.2f}% winrate\n'.format(tabs, self.wins, self.losses, self.wins / (self.losses + self.wins) * 100)
        if self.is_veteran or self.is_inactive \
                or self.is_fresh_blood or self.is_hot_streak:
            string += '\t{}'.format(tabs)
            if self.is_veteran:
                string += 'Veteran. '
            if self.is_inactive:
                string += 'Inactive. '
            if self.is_fresh_blood:
                string += 'Fresh Blood. '
            if self.is_hot_streak:
                string += 'Hot Streak. '
            string += '\n'
        return string


class LoLBestPlayers:
    def __init__(self, region, tier_id, queue_id, name, players_list):
        self.region = region
        self.tier_id = tier_id
        self.queue_id = queue_id
        self.name = name
        self.players_list = players_list

    def to_str(self, amount, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}{}\n'.format(tabs, self.name)
        string += '{}Region: {}\n'.format(tabs, Lv.regions_string_map[self.region])
        string += '{}{} {}'.format(tabs, Lv.tiers_string_map[self.tier_id],
                                   Lv.queues_string_map[self.queue_id])
        strings.append(string)
        string = ''

        if amount >= len(self.players_list):
            amount = len(self.players_list) - 1

        for i, p in enumerate(self.players_list[:amount]):
            string += '{}. {}\n'.format(i + 1, p.to_str())
            if i % Lv.split_best_players >= Lv.split_best_players - 1:
                strings.append(string)
                string = ''
            elif len(self.players_list[:amount]) - i == 1:
                strings.append(string)
        return strings
