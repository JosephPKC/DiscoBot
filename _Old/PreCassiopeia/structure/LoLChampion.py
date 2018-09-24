# region Imports
import math

from value import LeagueValues as Lv
# endregion


class LoLChampionSpell:
    def __init__(self, name, description, cd, cost, range):
        self.name = name
        self.description = description
        self.cd = cd
        self.cost = cost
        self.range = range

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}{}:\n{}\t{}\n\n'.format(tabs, self.name, tabs, self.description)
        if self.cd is not None:
            string += '\t{}Cooldown: {}\n'.format(tabs, self.cd)
        if self.cost is not None:
            string += '\t{}Cost: {}\n'.format(tabs, self.cost)
        if self.range is not None:
            string += '\t{}Range: {}\n'.format(tabs, self.range)
        return string

class LoLChampionStats:
    def __init__(self, ms, auto_range, hp_pair, mp_pair, armor_pair, mr_pair, hpr_pair, mpr_pair,
                 crit_pair, ad_pair, as_pair):
        self.ms = ms
        self.auto_range = auto_range
        self.hp_pair = hp_pair
        self.mp_pair = mp_pair
        self.armor_pair = armor_pair
        self.mr_pair = mr_pair
        self.hpr_pair = hpr_pair
        self.mpr_pair = mpr_pair
        self.crit_pair = crit_pair
        self.ad_pair = ad_pair
        self.as_pair = as_pair

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}Health:          {:<6} (+{:<5} per level)\n'\
            .format(tabs, self.hp_pair[0], self.hp_pair[1])
        string += '{}Mana:            {:<6} (+{:<5} per level)\n'\
            .format(tabs, self.mp_pair[0], self.mp_pair[1])
        string += '{}Health Regen:    {:<6} (+{:<5} per level)\n'\
            .format(tabs, self.hpr_pair[0], self.hpr_pair[1])
        string += '{}Mana Regen:      {:<6} (+{:<5} per level)\n'\
            .format(tabs, self.mpr_pair[0], self.mpr_pair[1])
        string += '{}Attack Damage:   {:<6} (+{:<5} per level)\n'\
            .format(tabs, self.ad_pair[0], self.ad_pair[1])
        base_as = 0.625 / (1 + self.as_pair[0])
        string += '{}Attack Speed:    {:04.4f} (+{:.2%} per level)\n'\
            .format(tabs, base_as, self.as_pair[1] / 100)
        string += '{}Armor:           {:<6} (+{:<5} per level)\n'\
            .format(tabs, self.armor_pair[0], self.armor_pair[1])
        string += '{}Magic Resist:    {:<6} (+{:<5} per level)\n'\
            .format(tabs, self.mr_pair[0], self.mr_pair[1])
        if self.crit_pair[0] != 0 or self.crit_pair[1] != 0:
            string += '{}Critical Chance: {:<6} (+{:.2%} per level)\n'\
                .format(tabs, self.crit_pair[0], self.crit_pair[1] / 100)
        string += '{}Movement Speed:  {:<6}\n'.format(tabs, self.ms)
        string += '{}Attack Range:    {:<6}\n'.format(tabs, self.auto_range)
        return string


class LoLChampion:
    def __init__(self, name, title, champion_id, lore,
                 tips_pair_list, tags_list, stats, spells_list, wiki_url, official_url):
        self.wiki_url = wiki_url
        self.official_url = official_url
        self.name = name
        self.title = title
        self.champion_id = champion_id
        self.lore = lore
        self.tips_pair_list = tips_pair_list
        self.tags_list = tags_list
        self.stats = stats
        self.spells_list = spells_list

    def to_str(self, use_lore, use_tips, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}{}, {}\n'.format(tabs, self.name, self.title)
        string += '{}Tags:\n'.format(tabs)
        for t in self.tags_list:
            string += '\t{}{}\n'.format(tabs, t)
        string += '{}Stats:\n'.format(tabs)
        string += self.stats.to_str(depth + 1)
        string += '{}Spells:\n'.format(tabs)
        strings.append(string)

        for s in self.spells_list:
            string = '{}\n'.format(s.to_str(depth))
            strings.append(string)

        if use_lore:
            partitions = int(math.ceil(len(self.lore) / 500))
            for i in range(1, partitions + 1):
                strings.append('{}\t'.format(tabs) + self.lore[500 * (i - 1):500 * i])
        if use_tips:
            string = '{}Ally Tips:\n'.format(tabs)
            for i, t in enumerate(self.tips_pair_list[0]):
                string += '\t{}{}. {}\n'.format(tabs, i + 1, t)
            string += '\n{}Enemy Tips:\n'.format(tabs)
            for i, t in enumerate(self.tips_pair_list[1]):
                string += '\t{}{}. {}\n'.format(tabs, i + 1, t)
            strings.append(string)
        return strings
