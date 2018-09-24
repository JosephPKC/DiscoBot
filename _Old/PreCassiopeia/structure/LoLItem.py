from value import LeagueValues as Lv


class LoLItem:
    def __init__(self, name, item_id, gist, description, base, buy, sell, builds_from_list, builds_into_list, art):
        self.name = name
        self.item_id = item_id
        self.gist = gist
        self.description = description
        self.base = base
        self.buy = buy
        self.sell = sell
        self.builds_from_list = builds_from_list
        self.builds_into_list = builds_into_list
        self.art = art

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}{}\n'.format(tabs, self.name)
        string += '{}{}\n\n'.format(tabs, self.gist)
        string += '{}{}\n\n'.format(tabs, self.description)
        string += '{}Gold:\n'.format(tabs)
        string += '{}\tBase: {}\n'.format(tabs, self.base)
        string += '{}\tTotal: {}\n'.format(tabs, self.buy)
        string += '{}\tSell: {}\n'.format(tabs, self.sell)
        if self.builds_from_list:
            string += '{}Builds from:\n'.format(tabs)
        for b in self.builds_from_list:
            string += '\t{}{}\n'.format(tabs, b)
        if self.builds_into_list:
            string += '{}Builds into:\n'.format(tabs)
        for b in self.builds_into_list:
            string += '\t{}{}\n'.format(tabs, b)
        return [string]
