# region Imports
from value import LeagueValues as Lv
# endregion

# region Structures
class LoLPlayerRankPackage:
    def __init__(self, name, queue, division, rank, lp, wins, losses, is_veteran, is_inactive, is_fresh, is_streak):
        self.name = name
        self.queue = queue
        self.division = division
        self.rank = rank
        self.lp = lp
        self.wins = wins
        self.losses = losses
        self.wr = wins / (wins + losses) * 100
        self.is_veteran = is_veteran
        self.is_inactive = is_inactive
        self.is_fresh = is_fresh
        self.is_streak = is_streak

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}:\n'.format(Lv.queues_string_map[self.queue])
        string += '{}{}\n'.format(tabs, self.name)
        string += '{}{} {}\n'.format(tabs, self.division, self.rank)
        string += '{}{} LP\n'.format(tabs, self.lp)
        string += '{}{} wins, {} losses, {:.2f}% winrate\n'.format(tabs, self.wins, self.losses, self.wr)
        if self.is_veteran or self.is_inactive or self.is_fresh or self.is_streak:
            string += '{}'.format(tabs)
        if self.is_veteran:
            string += 'Veteran. '
        if self.is_inactive:
            string += 'Inactive. '
        if self.is_fresh:
            string += 'Fresh Blood. '
        if self.is_streak:
            string += 'Hot Streak. '
        return [string]


class LoLPlayer:
    def __init__(self, region, name, player_id, account_id, level, icon, ranks):
        self.region = region
        self.name = name
        self.playerId = player_id
        self.accountId = account_id
        self.level = level
        self.icon = icon
        self.ranks = {}
        for r in ranks:
            self.ranks[r.queue] = r

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = 'Name: {}\n'.format(self.name)
        string += 'Region: {}\n'.format(Lv.regions_string_map[self.region])
        string += 'Level: {}\n'.format(self.level)
        string += 'Ranked Info:\n'
        if self.ranks:
            for r in self.ranks.keys():
                string += str(self.ranks[r].to_str(depth + 1)[0]) + '\n'
        else:
            string += "{}Placements not finished.\n".format(tabs + '\t')
        return [string]
# endregion

# region Factory
def create_lol_player(region, player, ranks):
    if region is None or player is None or ranks is None:
        return None
    str_ranks = []
    for r in ranks:
        str_ranks.append(LoLPlayerRankPackage(r['leagueName'], r['queueType'],
                                              r['tier'], r['rank'], r['leaguePoints'],
                                              r['wins'], r['losses'], r['veteran'],
                                              r['inactive'], r['freshBlood'],
                                              r['hotStreak']))
    return LoLPlayer(region, player['name'], player['id'], player['accountId'],
                     player['summonerLevel'], player['profileIconId'], str_ranks)
# endregion
