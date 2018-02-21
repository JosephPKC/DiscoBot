from value import LeagueValues as Lv


class LoLChampionStatsPosition:
    def __init__(self, win_rate, play_rate, ban_rate, kda_triple, minions, game_score, total, damage_taken, damage_dealt, healing, killing_sprees, performance, gold_earned):
        self.win_rate = win_rate
        self.play_rate = play_rate
        self.ban_rate = ban_rate
        self.kda_triple = kda_triple
        self.minions = minions
        self.game_score = game_score
        self.total = total
        self.damage_taken = damage_taken
        self.damage_dealt = damage_dealt
        self.healing = healing
        self.killing_sprees = killing_sprees
        self.performance = performance
        self.gold_earned = gold_earned

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Overall Performance:', self.performance[0], self.total,
                    self.performance[2], self.performance[1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Win Rate:', self.win_rate[0], self.total,self.win_rate[2],
                    self.win_rate[1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Play Rate:', self.play_rate[0], self.total,self.play_rate[2],
                    self.play_rate[1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Ban Rate:', self.ban_rate[0], self.total,self.ban_rate[2],
                    self.ban_rate[1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Average Game Score:', self.game_score[0], self.total,
                    self.game_score[2], self.game_score[1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Kills:', self.kda_triple[0][0], self.total,
                    self.kda_triple[0][2],self.kda_triple[0][1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Deaths:', self.kda_triple[1][0], self.total,
                    self.kda_triple[1][2], self.kda_triple[1][1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Assists:', self.kda_triple[2][0], self.total,
                    self.kda_triple[2][2], self.kda_triple[2][1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Gold Earned:', self.gold_earned[0], self.total,
                    self.gold_earned[2], self.gold_earned[1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Minions:', self.minions[0], self.total, self.minions[2],
                    self.minions[1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Damage Dealt:', self.damage_dealt[0], self.total,
                    self.damage_dealt[2], self.damage_dealt[1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Damage Taken:', self.damage_taken[0], self.total,
                    self.damage_taken[2], self.damage_taken[1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Killing Sprees:', self.killing_sprees[0], self.total,
                    self.killing_sprees[2], self.killing_sprees[1])
        string += '{}{:<25}{:>2}/{:<3} ({:+d} from {})\n'\
            .format(tabs, 'Healing:', self.healing[0], self.total, self.healing[2],
                    self.healing[1])
        return string


class LoLChampionStatsMinMax:
    def __init__(self, win_rate, play_rate, ban_rate, kda_triple, minions_triple, gold_earned,
                 killing_sprees, damage_dealt, healing, damage_taken):
        self.win_rate = win_rate
        self.play_rate = play_rate
        self.ban_rate = ban_rate
        self.kda_triple = kda_triple
        self.minions_triple = minions_triple
        self.gold_earned = gold_earned
        self.killing_sprees = killing_sprees
        self.damage_dealt = damage_dealt
        self.healing = healing
        self.damage_taken = damage_taken

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}Win Rate:  {:04.2f}% - {:04.2f}%\n'\
            .format(tabs, self.win_rate[0], self.win_rate[1])
        string += '{}Play Rate: {:04.2f}% - {:04.2f}%\n'\
            .format(tabs, self.play_rate[0], self.play_rate[1])
        string += '{}Ban Rate:  {:04.2f}% - {:04.2f}%\n\n'\
            .format(tabs, self.ban_rate[0], self.ban_rate[1])

        string += '{}Kills:   {:04.2f} - {:04.2f}\n'\
            .format(tabs, self.kda_triple[0][0], self.kda_triple[1][0])
        string += '{}Deaths:  {:04.2f} - {:04.2f}\n'\
            .format(tabs, self.kda_triple[0][1], self.kda_triple[1][1])
        string += '{}Assists: {:04.2f} - {:04.2f}\n\n'\
            .format(tabs, self.kda_triple[0][2], self.kda_triple[1][2])

        string += '{}Gold Earned: {:04.2f} - {:04.2f}\n'\
            .format(tabs, self.gold_earned[0], self.gold_earned[1])
        string += '{}Minions:     {:04.2f} - {:04.2f}\n'\
            .format(tabs, self.minions_triple[0][0], self.minions_triple[1][0])
        string += '{}Monsters in Ally Jungle:  {:04.2f} - {:04.2f}\n'\
            .format(tabs, self.minions_triple[0][1], self.minions_triple[1][1])
        string += '{}Monsters in Enemy Jungle: {:04.2f} - {:04.2f}\n\n'\
            .format(tabs, self.minions_triple[0][2], self.minions_triple[1][2])

        string += '{}Damage Dealt:   {:04.2f} - {:04.2f}\n'\
            .format(tabs, self.damage_dealt[0], self.damage_dealt[1])
        string += '{}Damage Taken:   {:04.2f} - {:04.2f}\n'\
            .format(tabs, self.damage_taken[0], self.damage_taken[1])
        string += '{}Killing Sprees: {:04.2f} - {:04.2f}\n'\
            .format(tabs, self.killing_sprees[0], self.killing_sprees[1])
        string += '{}Total Healing:  {:04.2f} - {:04.2f}\n'\
            .format(tabs, self.healing[0], self.healing[1])
        return string


class LolChampionStatsNormalized:
    def __init__(self, kda_triple, win_rate, play_rate, ban_rate, minions_triple, gold_earned,
                 killing_sprees, average_game_score, total_damage_taken, total_damage_dealt,
                 total_heal):
        self.kda_triple = kda_triple
        self.win_rate = win_rate
        self.play_rate = play_rate
        self.ban_rate = ban_rate
        self.minions_triple = minions_triple
        self.gold_earned = gold_earned
        self.killing_sprees = killing_sprees
        self.average_game_score = average_game_score
        self.total_damage_taken = total_damage_taken
        self.total_damage_dealt = total_damage_dealt
        self.total_heal = total_heal
        self.kda = (self.kda_triple[0] + self.kda_triple[2]) / (1 + self.kda_triple[1])

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}Win Rate:  {:04.2f}\n'.format(tabs, self.win_rate)
        string += '{}Play Rate: {:04.2f}\n'.format(tabs, self.play_rate)
        string += '{}Ban Rate:  {:04.2f}\n'.format(tabs, self.ban_rate)
        string += '{}Average Game Score: {:04.2f}\n\n'.format(tabs, self.average_game_score)
        string += '{}Kills:   {:04.2f}\n'.format(tabs, self.kda_triple[0])
        string += '{}Deaths:  {:04.2f}\n'.format(tabs, self.kda_triple[1])
        string += '{}Assists: {:04.2f}\n'.format(tabs, self.kda_triple[2])
        string += '{}KDA: {:04.2f}\n\n'.format(tabs, self.kda)

        string += '{}Gold Earned: {:04.2f}\n'.format(tabs, self.gold_earned)
        string += '{}Minions: {:04.2f}\n'.format(tabs, self.minions_triple[0])
        string += '{}Monsters in Ally Jungle:  {:04.2f}\n'.format(tabs, self.minions_triple[1])
        string += '{}Monsters in Enemy Jungle: {:04.2f}\n\n'.format(tabs, self.minions_triple[2])

        string += '{}Damage Dealt:   {:04.2f}\n'.format(tabs, self.total_damage_dealt)
        string += '{}Damage Taken:   {:04.2f}\n'.format(tabs, self.total_damage_taken)
        string += '{}Killing Sprees: {:04.2f}\n'.format(tabs, self.killing_sprees)
        string += '{}Total Healing:  {:04.2f}\n'.format(tabs, self.total_heal)
        return string


class LoLChampionStatsDamageComposition:
    def __init__(self, total, total_physical, total_magical, total_true, percent_physical, percent_magical, percent_true):
        self.total = total
        self.total_physical = total_physical
        self.total_magical = total_magical
        self.total_true = total_true
        self.percent_physical = percent_physical
        self.percent_magical = percent_magical
        self.percent_true = percent_true

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}Total Damage: {:04.2f}\n'.format(tabs, self.total)
        string += '\t{}{:<10}{:04.2f} ({:04.2f}%)\n'\
            .format(tabs, 'Physical:', self.total_physical, self.percent_physical)
        string += '\t{}{:<10}{:04.2f} ({:04.2f}%)\n'\
            .format(tabs, 'Magical:', self.total_magical, self.percent_magical)
        string += '\t{}{:<10}{:04.2f} ({:04.2f}%)\n'\
            .format(tabs, 'True:', self.total_true, self.percent_true)
        return string


class LoLChampionStats:
    def __init__(self, name, ch_gg_name, champion_id, role, elo, win_rate, play_rate, ban_rate,
                 kda_triple, total_damage_taken, wards_pair, average_games, largest_killing_spree,
                 minions_triple, games_played, overall_performance, percent_role_played,
                 gold_earned, killing_sprees, total_heal, damage_composition, positions_pair,
                 normalized, min_max_pair):
        self.name = name
        self.ch_gg_name = ch_gg_name
        self.champion_id = champion_id
        self.role = role
        self.elo = elo
        self.win_rate = win_rate
        self.play_rate = play_rate
        self.ban_rate = ban_rate
        self.kda_triple = kda_triple
        self.total_damage_taken = total_damage_taken
        self.wards_pair = wards_pair
        self.average_games = average_games
        self.largest_killing_spree = largest_killing_spree
        self.minions_triple = minions_triple
        self.games_played = games_played
        self.overall_performance = overall_performance
        self.percent_role_played = percent_role_played
        self.gold_earned = gold_earned
        self.killing_sprees = killing_sprees
        self.total_heal = total_heal
        self.damage_composition = damage_composition
        self.positions_pair = positions_pair
        self.normalized = normalized
        self.min_max_pair = min_max_pair
        self.kda = (self.kda_triple[0] + self.kda_triple[2]) / (1 + self.kda_triple[1])

    def to_str(self, use_pos, use_norm, use_min_max, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}Champion: {} ({})\n'.format(tabs, self.name, Lv.ch_gg_roles_string_map[self.role])
        string += '{}Elo: {}\n'.format(tabs, Lv.elo_string_map_inverted[self.elo])
        string += '{}Analyzed {} Games, {:04.2f}% of which were in {}.\n'\
            .format(tabs, self.games_played, self.percent_role_played,
                    Lv.ch_gg_roles_string_map[self.role])
        string += '{}Average Games Played by an Average User: {:04.2f}\n\n'.format(tabs, self.average_games)
        string += '{}Win Rate:  {:04.2f}%\n'.format(tabs, self.win_rate)
        string += '{}Play Rate: {:04.2f}%\n'.format(tabs, self.play_rate)
        string += '{}Ban Rate:  {:04.2f}%\n'.format(tabs, self.ban_rate)
        string += '{}Average Overall Performance Score: {:04.2f}\n'.format(tabs, self.overall_performance)
        string += '{}Kills:   {:04.2f}\n'.format(tabs, self.kda_triple[0])
        string += '{}Deaths:  {:04.2f}\n'.format(tabs, self.kda_triple[1])
        string += '{}Assists: {:04.2f}\n'.format(tabs, self.kda_triple[2])
        string += '{}KDA:     {:04.2f}\n\n'.format(tabs, self.kda)

        string += '{}Average Gold Earned: {:04.2f}\n'.format(tabs, self.gold_earned)
        string += '{}Average Minions: {:04.2f}\n'.format(tabs, self.minions_triple[0])
        string += '{}Average Monsters in Ally Jungle:  {:04.2f}\n'\
            .format(tabs, self.minions_triple[1])
        string += '{}Average Monsters in Enemy Jungle: {:04.2f}\n\n'\
            .format(tabs, self.minions_triple[2])

        string += 'Average {}'.format(self.damage_composition.to_str(depth))
        string += '{}Average Damage Taken:   {:04.2f}\n'.format(tabs, self.total_damage_taken)
        string += '{}Largest Killing Spree:  {}\n'.format(tabs, self.largest_killing_spree)
        string += '{}Average Killing Sprees: {:04.2f}\n'\
            .format(tabs, self.killing_sprees)
        string += '{}Average Healing: {:04.2f}\n'.format(tabs, self.total_heal)
        string += '{}Average Wards Placed: {:04.2f}\n'.format(tabs, self.wards_pair[0])
        string += '{}Average Wards Killed: {:04.2f}\n'.format(tabs, self.wards_pair[1])
        strings.append(string)

        if use_norm:
            string = '{}Normalized Stats (Compared to other {})\n'\
                .format(tabs, Lv.ch_gg_roles_string_map[self.role])
            string += '{}'.format(self.normalized.to_str(depth))
            strings.append(string)

        if use_min_max:
            string = '{}Min/Max Stats\n'.format(tabs)
            string += '{}'.format(self.min_max_pair.to_str(depth))
            strings.append(string)

        if use_pos:
            string = '{}Positional Stats (Ranked relative to other {})\n'\
                .format(tabs, Lv.ch_gg_roles_string_map[self.role])
            string += '{}'.format(self.positions_pair.to_str(depth))
            strings.append(string)
        return strings
