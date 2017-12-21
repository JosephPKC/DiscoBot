
class PlayerMatch:
    def __init__(self, id, champion, queue, season, role, lane, **kwargs):
        self.id = id
        self.champion = champion
        self.queue = queue
        self.season = season
        self.role = role
        self.lane = lane
        self.kills = kwargs['kills']
        self.deaths = kwargs['deaths']
        self.assists = kwargs['assists']
        self.cs = kwargs['cs']
        self.cc = kwargs['cc']
        self.vision = kwargs['vision']
        self.victory = kwargs['victory']


    def __str__(self):
        # Note we need to access database to map ids to actual names
        string = '\t{}\n'.format('VICTORY' if self.victory else 'DEFEAT')
        string += '\tMatch ID: {}\n'.format(self.id)
        string += '\tSeason {}, Queue: {}\n'.format(self.season, self.queue)
        string += '\tChampion: {}, Lane: {}\n'.format(self.champion, self.lane)
        string += '\tKDA: {}/{}/{}\n'.format(self.kills, self.deaths, self.assists)
        string += '\tCS: {}, CC: {}, Vision: {}\n'.format(self.cs, self.cc, self.vision)
        return string