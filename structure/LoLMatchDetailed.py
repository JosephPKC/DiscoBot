# region Imports
from value import LeagueValues as Lv, GeneralValues as Gv
# endregion


class LoLMatchDetailedTimelinePackage:
    def __init__(self, timeline):
        self.timeline = timeline


class LoLMatchDetailedRunePackage:
    def __init__(self, rune_id, style_pair, name, var_pair_list):
        self.rune_id = rune_id
        self.style_pair = style_pair
        self.name = name
        self.var_pair_list = var_pair_list


class LoLMatchDetailedDamagePackage:
    def __init__(self, total, magical, physical, true):
        self.total = total
        self.magical = magical
        self.physical = physical
        self.true = true


class LoLMatchDetailedPlayerPackage:
    def __init__(self, name, champion_pair, role_id, lane_id,
                 spell_pair_list, item_pair_list, rune_list,
                 kda_triple, largest_spree, largest_multi_kill,
                 double_kills, triple_kills, quadra_kills,
                 penta_kills, unreal_kills, largest_critical,
                 damage_dealt, damage_to_champs, damage_taken,
                 healing, damage_mitigated, damage_to_obj,
                 damage_to_tower, vision_triple, cc,
                 gold_pair, towers_pair, inhibitors_pair,
                 cs, monster_pair, first_blood_pair,
                 first_tower_pair, score_pair, has_lanes):
        self.name = name
        self.champion_pair = champion_pair
        self.role_id = role_id
        self.lane_id = lane_id
        self.spell_pair_list = spell_pair_list
        self.item_pair_list = item_pair_list
        self.rune_list = rune_list
        self.kda_triple = kda_triple
        self.largest_spree = largest_spree
        self.largest_multi_kill = largest_multi_kill
        self.double_kills = double_kills
        self.triple_kills = triple_kills
        self.quadra_kills = quadra_kills
        self.penta_kills = penta_kills
        self.unreal_kills = unreal_kills
        self.largest_critical = largest_critical
        self.damage_dealt = damage_dealt
        self.damage_to_champs = damage_to_champs
        self.damage_taken = damage_taken
        self.healing = healing
        self.damage_mitigated = damage_mitigated
        self.damage_to_obj = damage_to_obj
        self.damage_to_tower = damage_to_tower
        self.vision_triple = vision_triple
        self.cc = cc
        self.gold_pair = gold_pair
        self.towers_pair = towers_pair
        self.inhibitors_pair = inhibitors_pair
        self.cs = cs
        self.monster_pair = monster_pair
        self.first_blood_pair = first_blood_pair
        self.first_tower_pair = first_tower_pair
        self.score_pair = score_pair
        self.has_lanes = has_lanes

    def to_str(self, use_runes=False, use_details=False, use_timeline=False, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}{}\n'.format(tabs, self.name)
        string += '{}{}'.format(tabs, self.champion_pair[1])
        if self.has_lanes:
            string += ', {} {}'\
                .format(Lv.lanes_string_map[self.lane_id],
                        Lv.roles_string_map[self.role_id])
        string += '\n'

        if self.spell_pair_list[0][1] is not None:
            string += '{}Spell 1: {}\n'.format(tabs, self.spell_pair_list[0][1])
        if self.spell_pair_list[1][1] is not None:
            string += '{}Spell 2: {}\n'.format(tabs, self.spell_pair_list[1][1])
        string += '{}KDA: {}/{}/{}\n'\
            .format(tabs, self.kda_triple[0], self.kda_triple[1], self.kda_triple[2])
        if self.score_pair[0]:
            string += '{}Score: {}\n'.format(tabs, self.score_pair[1])

        string += '{}Final Items:\n'.format(tabs)
        for i, item in enumerate(self.item_pair_list):
            string += '\t{}{}: {}\n'.format(tabs, 'Trinket' if i == 6 else i + 1, item[1])

        if use_runes:
            string += '{}Primary: {}\n'.format(tabs, self.rune_list[0].style_pair[1])
            for r in self.rune_list[:3]:
                string += '\t{}{}\n'.format(tabs, r.name)
                for v in r.var_pair_list:
                    string += '\t\t{}{}: {}\n'.format(tabs, v[0], v[1])

            string += '{}Secondary: {}\n'.format(tabs, self.rune_list[4].style_pair[1])
            for r in self.rune_list[4:]:
                string += '\t{}{}\n'.format(tabs, r.name)
                for v in r.var_pair_list:
                    string += '\t\t{}{}: {}\n'.format(tabs, v[0], v[1])
        strings.append(string)

        string = ''
        if use_details:
            string += '{}Largest Killing Spree: {}\n'.format(tabs, self.largest_spree)
            string += '{}Largest Multi Kill: {}\n'.format(tabs, self.largest_multi_kill)
            string += '\t{}Double Kills: {}\n'.format(tabs, self.double_kills)
            string += '\t{}Triple Kills: {}\n'.format(tabs, self.triple_kills)
            string += '\t{}Quadra Kills: {}\n'.format(tabs, self.quadra_kills)
            string += '\t{}Penta Kills: {}\n'.format(tabs, self.penta_kills)
            string += '\t{}Unreal Kills: {}\n'.format(tabs, self.unreal_kills)
            if self.first_blood_pair[0]:
                string += '\t{}First Blood Kill.\n'.format(tabs)
            elif self.first_blood_pair[1]:
                string += '\t{}First Blood Assist.\n'.format(tabs)
            string += '\n'

            if self.towers_pair[0]:
                string += '{}Towers Killed: {}\n'.format(tabs, self.towers_pair[1])
                if self.first_tower_pair[0]:
                    string += '\t{}First Tower Kill.\n'.format(tabs)
                elif self.first_tower_pair[1]:
                    string += '\t{}First Tower Assist.\n'.format(tabs)
            if self.inhibitors_pair[0]:
                string += '{}Inhibitors Killed: {}\n'\
                    .format(tabs, self.inhibitors_pair[1])
            string += '\n'

            string += '{}CS: {}'.format(tabs, self.cs)
            if self.monster_pair[0]:
                string += ', Monsters: {}'.format(self.monster_pair[1])
            string += '\n\n'

            if self.vision_triple[0]:
                string += '{}Vision Score: {}, Vision Bought: {}\n'\
                    .format(tabs, self.vision_triple[1], self.vision_triple[2])
            string += '{}Crowd Control Time: {}\n'.format(tabs, self.cc)
            string += '{}Gold Spent/Earned: {}/{}\n'.format(tabs, self.gold_pair[0], self.gold_pair[1])
            string += '\n'

        string += '{}Damage Dealt: {}\n'.format(tabs, self.damage_dealt.total)
        if use_details:
            string += '\t{}Magical: {}\n'.format(tabs, self.damage_dealt.magical)
            string += '\t{}Physical: {}\n'.format(tabs, self.damage_dealt.physical)
            string += '\t{}True: {}\n'.format(tabs, self.damage_dealt.true)

        string += '{}Damage Dealt to Champions: {}\n'\
            .format(tabs, self.damage_to_champs.total)
        if use_details:
            string += '\t{}Magical: {}\n'.format(tabs, self.damage_to_champs.magical)
            string += '\t{}Physical: {}\n'.format(tabs, self.damage_to_champs.physical)
            string += '\t{}True: {}\n'.format(tabs, self.damage_to_champs.true)

        string += '{}Damage Taken: {}\n'.format(tabs, self.damage_taken.total)
        if use_details:
            string += '\t{}Magical: {}\n'.format(tabs, self.damage_taken.magical)
            string += '\t{}Physical: {}\n'.format(tabs, self.damage_taken.physical)
            string += '\t{}True: {}\n'.format(tabs, self.damage_taken.true)

            string += '{}Damage Dealt to Objectives: {}\n'.format(tabs, self.damage_to_obj)
            string += '{}Damage Dealt to Towers: {}\n'.format(tabs, self.damage_to_tower)
            string += '{}Damage Mitigated: {}\n'.format(tabs, self.damage_mitigated)

        string += '{}Total Healing: {}\n'.format(tabs, self.healing)
        string += '{}Largest Critical Strike: {}\n'.format(tabs, self.largest_critical)
        strings.append(string)

        # if use_timeline and self.has_lanes:
        #     headers = ['{}CS Per Min:\n'.format(tabs),
        #                '{}CS Diffs Per Min:\n'.format(tabs),
        #                '{}XP Per Min:\n'.format(tabs),
        #                '{}XP Diffs Per Min:\n'.format(tabs),
        #                '{}Gold Per Min:\n'.format(tabs),
        #                '{}Damage Taken Per Min:\n'.format(tabs),
        #                '{}Damage Diffs Taken Per Min:\n'.format(tabs)]
        #     string = ''
        #     for i, t in enumerate(self.timeline_list):
        #         string += headers[i]
        #         for v in t.timeline:
        #             string += '\t{}{}: {}\n'.format(tabs, v[0], v[1])
        #     strings.append(string)
        return strings


class LoLMatchDetailedTeamPackage:
    def __init__(self, has_win, towers_pair, inhibitors_pair,
                 dragons_pair, barons_pair, heralds_pair,
                 vilemaws_pair, first_blood, first_tower,
                 first_inhibitor, first_dragon, first_baron,
                 score_pair, bans_pair_list, players_list):
        self.has_win = has_win
        self.towers_pair = towers_pair
        self.inhibitors_pair = inhibitors_pair
        self.dragons_pair = dragons_pair
        self.barons_pair = barons_pair
        self.heralds_pair = heralds_pair
        self.vilemaws_pair = vilemaws_pair
        self.first_blood = first_blood
        self.first_tower = first_tower
        self.first_inhibitor = first_inhibitor
        self.first_dragon = first_dragon
        self.first_baron = first_baron
        self.score_pair = score_pair
        self.bans_pair_list = bans_pair_list
        self.players_list = players_list

    def to_str(self, use_runes=False, use_details=False, use_timeline=False, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}{}\n'.format(tabs, 'VICTORY' if self.has_win else 'DEFEAT')
        if self.score_pair[0]:
            string += '{}Score: {}\n'.format(tabs, self.score_pair[1])

        if use_details:
            if self.first_blood:
                string += '{}{}.\n'.format(tabs, 'First Blood')
            if self.towers_pair[0]:
                string += '{}Towers: {}.{}\n'\
                    .format(tabs, self.towers_pair[1],
                            ' First Tower.' if self.first_tower else '')
            if self.inhibitors_pair[0]:
                string += '{}Inhibitors: {}.{}\n'\
                    .format(tabs, self.inhibitors_pair[1],
                            ' First Inhibitor.' if self.first_inhibitor else '')
            if self.dragons_pair[0]:
                string += '{}Dragons: {}.{}\n'\
                    .format(tabs, self.dragons_pair[1],
                            ' First Dragon.' if self.first_dragon else '')
            if self.heralds_pair[0]:
                string += '{}Rift Heralds: {}.\n'\
                    .format(tabs, self.heralds_pair[1])
            if self.barons_pair[0]:
                string += '{}Barons: {}.{}\n'\
                    .format(tabs, self.barons_pair[1],
                            ' First Baron.' if self.first_baron else '')
            if self.vilemaws_pair[0]:
                string += '{}Vile Maws: {}.\n'.format(tabs, self.vilemaws_pair[1])

        if self.bans_pair_list:
            string += '{}Bans:\n'.format(tabs)
        for i, b in enumerate(self.bans_pair_list):
            string += '{} {}. {}\n'.format(tabs, i + 1, b[1])
        strings.append(string)

        for p in self.players_list:
            for s in p.to_str(use_runes, use_details, use_timeline, depth):
                strings.append(s)
        return strings


class LoLMatchDetailed:
    def __init__(self, region, match_id, queue_pair, season_pair, duration, team_pair):
        self.region = region
        self.match_id = match_id
        self.queue_pair = queue_pair
        self.season_pair = season_pair
        self.duration = duration
        self.team_pair = team_pair

    def to_str(self, use_runes=False, use_details=False, use_timeline=False, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}Match ID: {}\n'.format(tabs, self.match_id)
        string += '{}Region: {}\n'.format(tabs, Lv.regions_string_map[self.region])
        string += '{}{}\n'.format(tabs, self.season_pair[1])
        string += '{}{}\n'.format(tabs, self.queue_pair[1])
        minutes, seconds = Gv.get_minutes_seconds(self.duration)
        string += '{}Duration: {}:{:02d}\n'.format(tabs, int(minutes), round(seconds))
        strings.append(string)

        team1 = self.team_pair[0].\
            to_str(use_runes, use_details, use_timeline, depth)
        team2 = self.team_pair[1].\
            to_str(use_runes, use_details, use_timeline, depth)
        string = '{}Team 1:\n{}\n'.format(tabs, team1[0])
        strings.append(string)

        for s in team1[1:]:
            strings.append(s)
        string = '{}Team 2:\n{}\n'.format(tabs, team2[0])
        strings.append(string)

        for s in team2[1:]:
            strings.append(s)
        return strings
