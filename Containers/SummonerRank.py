from Data.values import LoLvals

class SummonerRank:
    def __init__(self, queue, name, division, rank, lp, wins, losses, is_veteran, is_inactive, is_fresh, is_hot):
        self.queue = queue
        self.name = name
        self.division = division
        self.rank = rank
        self.lp = lp
        self.wins = wins
        self.losses = losses
        self.wr = wins / (wins + losses) * 100
        self.veteran = is_veteran
        self.inactive = is_inactive
        self.fresh_blood = is_fresh
        self.hot_streak = is_hot

    def __str__(self):
        string = '{}\n'.format(LoLvals.queues_strings[self.queue])
        string += '\t{}\n'.format(self.name)
        string += '\t{} {}\n'.format(self.division, self.rank)
        string += '\t{} LP\n'.format(self.lp)
        string += '\t{} wins, {} losses, {:.2f}% winrate\n'.format(self.wins, self.losses, self.wr)
        if self.veteran or self.inactive or self.fresh_blood or self.hot_streak:
            string += '\t'
        if self.veteran:
            string += 'Veteran. '
        if self.inactive:
            string += 'Inactive. '
        if self.fresh_blood:
            string += 'Fresh Blood. '
        if self.hot_streak:
            string += 'Hot Streak. '
        return string
