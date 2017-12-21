from Data.values import LoLvals

class PlayerMatchList:
    def __init__(self, name, region, id, matches, **kwargs):
        self.name = name
        self.region = region
        self.id = id
        self.matches = matches

    def to_str(self, i_min=1, i_max=20):
        string = 'Name: {}\n'.format(self.name)
        string += 'Region: {}\n'.format(LoLvals.regions_strings[self.region])
        string += 'Recent Matches:\n'
        string += self.to_str_match_only(i_min, i_max)
        return string

    def to_str_match_only(self, i_min=1, i_max=20):
        string = ''
        for m in self.matches[i_min - 1:i_max]:
            string += '{}\n'.format(m)
        return string