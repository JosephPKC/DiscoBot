from Data.values import LoLvals

class Summoner:
    def __init__(self, name, region, id, level, icon, ranks, **kwargs):
        self.name = name
        self.region = region
        self.id = id
        self.level = level
        self.icon = icon
        self.ranks = {}
        for r in ranks:
            self.ranks[r.queue] = r

    def __str__(self):
        string = 'Name: {}\n'.format(self.name)
        string += 'Region: {}\n'.format(LoLvals.regions_strings[self.region])
        string += 'Level: {}\n'.format(self.level)
        string += 'Ranked Info:\n'
        for r in self.ranks.keys():
            string += str(self.ranks[r]) + '\n'
        return string