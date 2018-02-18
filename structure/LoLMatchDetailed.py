# region Imports
from value import LeagueValues as Lv, GeneralValues as Gv
# endregion


class LoLMatchDetailed:
    def __init__(self, region, match_id, season, queue, duration, teams, has_lanes, has_towers, has_inhibitors,
                 has_dragons, has_barons, has_heralds, has_vilemaws, has_score, has_vision, has_monsters, official):
        self.region = region
        self.match_id = match_id
        self.season = season
        self.queue = queue
        self.duration = duration
        self.teams = teams
        self.has_lanes = has_lanes
        self.has_towers = has_towers
        self.has_inhibitors = has_inhibitors
        self.has_dragons = has_dragons
        self.has_barons = has_barons
        self.has_heralds = has_heralds
        self.has_vilemaws = has_vilemaws
        self.has_score = has_score
        self.has_vision = has_vision
        self.has_monsters = has_monsters
        self.official = official

    def embed(self, ctx, use_rune, use_detail):
        embeds = []
        embed = Gv.create_embed(Lv.default_embed_color,
                                'Overview of Match __**{}**__ in __**{}**__.'.format(self.match_id, self.region),
                                ctx.message.author)
        embed.set_author(name='{}'.format(self.match_id),
                         url=self.official)
        # Match Info: Season, Queue, Duration
        embed.add_field(name='__Info:__',
                        value='{}\n{}\n**Duration:** {}'.format(self.season, self.queue, self.duration),
                        inline=False)
        for t in self.teams:
            embed.add_field(name='__TEAM {}:__'.format(t.team_id // 100),
                            value=self.__get_team_string(t),
                            inline=True)
        embeds.append(embed)
        # Players
        for t in self.teams:
            for p in t.players:
                embed = Gv.create_embed(Lv.default_embed_color,
                                        'Overview of __**Team {}\'s**__ __**{}**__.'
                                        .format(t.team_id // 100, p.name),
                                        ctx.message.author)
                embed.set_author(name='OP.GG: {}'.format(p.name),
                                 url=p.url,
                                 icon_url=Lv.op_gg_icon_url)
                embed.add_field(name='__OVERVIEW:__',
                                value=self.__get_player_string_basic(p),
                                inline=True)
                # KDA, CS, CC, Vision, Gold
                embed.add_field(name='__BASIC DETAILS:__',
                                value=self.__get_player_string_stats(p, use_detail),
                                inline=True)
                # Killing, Damage, Objectives
                embed.add_field(name='__ADVANCED DETAILS:__',
                                value=self.__get_player_string_obj(p, use_detail),
                                inline=True)
                # Runes
                if use_rune:
                    embed.add_field(name='__RUNES:__',
                                    value=self.__get_player_string_rune(p.runes),
                                    inline=True)
                embeds.append(embed)
        return embeds

    @staticmethod
    def __get_obj_kill_string(has_obj, first_obj, obj_kills, obj, objs):
        string = ''
        if has_obj:
            string += '**{}** {:<2}'.format(objs, obj_kills)
            if first_obj:
                string += ' Got **{}**.'.format(obj)
            string += '\n'
        return string
    
    def __get_player_string_basic(self, player):
        # Player Info: Basics, Name, Champion, Lane, Role, Previous Rank
        player_info = '**Champion:** {}'.format(player.champion)
        if self.has_lanes:
            player_info += ' {} {}'.format(player.lane, player.role)
        player_info += '\n'
        player_info += '**Previously:** {}\n'.format(player.previous_rank)
        # Summoner Spells
        player_info += '**Summoner Spells: ** {} {}\n'.format(*player.summoner_spells)
        # Final Items
        item_info = '**Final Items:**\n'
        for i, b in enumerate(player.items):
            item_info += '{}. {}\n'.format(i + 1, b)
        player_info += item_info
        return player_info

    def __get_player_string_stats(self, player, use_detail):
        # Player Info: Basics, Name, Champion, Lane, Role, Previous Rank
        player_info = ''
        if self.has_score:
            player_info += '**Score:** {}\n'.format(player.score)
        player_info += '**KDA:** {} / {} / {}\n'.format(player.kills, player.deaths, player.assists)
        player_info += '**CS:** {}'.format(player.cs)
        if self.has_monsters:
            player_info += ' **Monsters:** {}'.format(player.monsters)
        player_info += '\n'
        player_info += '**Gold Spent/Earned:** {} / {}\n'.format(player.gold_spent, player.gold_earned)
        player_info += '**CC:** {}\n'.format(player.cc)
        if self.has_vision:
            player_info += '**Vision:** {}\n'.format(player.vision)
            if use_detail:
                player_info += '\t**Wards Placed:** {}\n'.format(player.wards_placed)
                player_info += '\t**Wards Killed:** {}\n'.format(player.wards_killed)
                player_info += '\t**Wards Bought:** {}\n'.format(player.vision_bought)
        return player_info

    def __get_player_string_obj(self, player, use_detail):
        player_info = ''
        if use_detail:
            player_info += '**Killing Sprees:** {} **Largest:** {}\n'\
                .format(player.killing_sprees, player.largest_killing_spree)
            player_info += '**Largest Multi Kill:** {}\n'.format(player.largest_multi_kill)
            player_info += '\t**Double Kills:** {}\n'.format(player.double_kills)
            player_info += '\t**Triple Kills:** {}\n'.format(player.triple_kills)
            player_info += '\t**Quadra Kills:** {}\n'.format(player.quadra_kills)
            player_info += '\t**Penta Kills:** {}\n'.format(player.penta_kills)
            player_info += '\t**Unreal Kills:** {}\n'.format(player.unreal_kills)
            if player.first_blood:
                player_info += '\tGot **First Blood.**\n'
        player_info += '**Total Damage Dealt:** {}\n'.format(player.damage_dealt.total)
        if use_detail:
            player_info += '\t**Magical:** {}\n'.format(player.damage_dealt.magical)
            player_info += '\t**Physical:** {}\n'.format(player.damage_dealt.physical)
            player_info += '\t**True:** {}\n'.format(player.damage_dealt.true)
        player_info += '**Damage Dealt to Champions:** {}\n'.format(player.damage_dealt_to_champs.total)
        if use_detail:
            player_info += '\t**Magical:** {}\n'.format(player.damage_dealt_to_champs.magical)
            player_info += '\t**Physical:** {}\n'.format(player.damage_dealt_to_champs.physical)
            player_info += '\t**True:** {}\n'.format(player.damage_dealt_to_champs.true)
        player_info += '**Total Damage Taken:** {}\n'.format(player.damage_taken.total)
        if use_detail:
            player_info += '\t**Magical:** {}\n'.format(player.damage_taken.magical)
            player_info += '\t**Physical:** {}\n'.format(player.damage_taken.physical)
            player_info += '\t**True:** {}\n'.format(player.damage_taken.true)
        player_info += '**Largest Critical Strike:** {}\n'.format(player.largest_critical)
        player_info += '**Total Healing:** {}\n'.format(player.healing)
        player_info += '**Damage Self Mitigated:** {}\n'.format(player.damage_mitigated)
        player_info += '**Damage to Objectives:** {}\n'.format(player.damage_to_obj)
        if use_detail:
            if self.has_towers:
                player_info += '\t**Damage to Towers:** {}\n'.format(player.damage_to_towers)
                player_info += '\t**Towers:** {}'.format(player.tower_kills)
                if player.first_tower:
                    player_info += '\tGot **First Tower**.'
                player_info += '\n'
            if self.has_inhibitors:
                player_info += '\t**Inhibitors:** {}'.format(player.inhibitor_kills)
                if player.first_tower:
                    player_info += '\tGot **First Inhibitor**.'
                player_info += '\n'
        return player_info

    def __get_player_string_rune(self, runes):
        player_info = '**Primary:** {}\n'.format(runes[0].style)
        for r in runes[:3]:
            player_info += '**{}:**\n'.format(r.name)
            for v in r.var_vals:
                player_info += '\t{}: {}\n'.format(v[0], v[1])
        player_info += '\n**Secondary:** {}\n'.format(runes[4].style)
        for r in runes[4:]:
            player_info += '**{}:**\n'.format(r.name)
            for v in r.var_vals:
                player_info += '\t{}: {}\n'.format(v[0], v[1])
        return player_info

    def __get_team_string(self, team):
        team_info = '**{}**\n'.format('VICTORY' if team.did_win else 'DEFEAT')
        # Objectives and First Objectives
        if self.has_score:
            team_info += '**Score:** {}\n'.format(team.score)
        team_info += self.__get_obj_kill_string(self.has_towers, team.first_tower,
                                                team.tower_kills, 'First Tower', 'Towers:')
        team_info += self.__get_obj_kill_string(self.has_inhibitors, team.first_inhibitor,
                                                team.inhibitor_kills, 'First Inhibitor', 'Inhibitors:')
        team_info += self.__get_obj_kill_string(self.has_dragons, team.first_dragon,
                                                team.dragon_kills, 'First Dragon', 'Dragons:')
        team_info += self.__get_obj_kill_string(self.has_barons, team.first_baron,
                                                team.baron_kills, 'First Baron', 'Barons:')
        team_info += self.__get_obj_kill_string(self.has_heralds, team.first_rift_herald,
                                                team.rift_herald_kills, 'First Herald',
                                                'Heralds:')
        team_info += self.__get_obj_kill_string(self.has_vilemaws, False, team.vilemaw_kills,
                                                '', 'Vile\'Maws:')
        if team.first_blood:
            team_info += 'Got **First Blood**.\n'
        else:
            team_info += '\n'
        if team.bans:
            ban_info = '\n__**BANS:**__\n'
            for i, b in enumerate(team.bans):
                ban_info += '{}. **{}**\n'.format(i + 1, b)
            team_info += ban_info
        return team_info


class LoLMatchDetailedTeamPackage:
    def __init__(self, team_id, did_win, first_blood, first_tower, first_inhibitor, first_baron, first_dragon,
                 first_rift_herald, tower_kills, inhibitor_kills, baron_kills, dragon_kills, vilemaw_kills,
                 rift_herald_kills, score, bans, players):
        self.team_id = team_id
        self.did_win = did_win
        self.first_blood = first_blood
        self.first_tower = first_tower
        self.first_inhibitor = first_inhibitor
        self.first_baron = first_baron
        self.first_dragon = first_dragon
        self.first_rift_herald = first_rift_herald
        self.tower_kills = tower_kills
        self.inhibitor_kills = inhibitor_kills
        self.baron_kills = baron_kills
        self.dragon_kills = dragon_kills
        self.vilemaw_kills = vilemaw_kills
        self.rift_herald_kills = rift_herald_kills
        self.score = score
        self.bans = bans
        self.players = players


class LoLMatchDetailedPlayerPackage:
    def __init__(self, name, champion, lane, role, previous_rank, summoner_spells, items, kills, deaths, assists,
                 largest_killing_spree, largest_multi_kill, killing_sprees, double_kills, triple_kills,
                 quadra_kills, penta_kills, unreal_kills, damage_dealt, largest_critical, damage_dealt_to_champs,
                 healing, damage_mitigated, damage_to_obj, damage_to_towers, vision, cc, damage_taken,
                 gold_earned, gold_spent, tower_kills, inhibitor_kills, cs, monsters, vision_bought, wards_placed,
                 wards_killed, first_blood, first_tower, first_inhibitor, score, runes, url):
        self.url = url
        self.name = name
        self.champion = champion
        self.lane = lane
        self.role = role
        self.previous_rank = previous_rank
        self.summoner_spells = summoner_spells
        self.items = items
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.largest_killing_spree = largest_killing_spree
        self.largest_multi_kill = largest_multi_kill
        self.killing_sprees = killing_sprees
        self.double_kills = double_kills
        self.triple_kills = triple_kills
        self.quadra_kills = quadra_kills
        self.penta_kills = penta_kills
        self.unreal_kills = unreal_kills
        self.damage_dealt = damage_dealt
        self.largest_critical = largest_critical
        self.damage_dealt_to_champs = damage_dealt_to_champs
        self.healing = healing
        self.damage_mitigated = damage_mitigated
        self.damage_to_obj = damage_to_obj
        self.damage_to_towers = damage_to_towers
        self.vision = vision
        self.cc = cc
        self.damage_taken = damage_taken
        self.gold_earned = gold_earned
        self.gold_spent = gold_spent
        self.tower_kills = tower_kills
        self.inhibitor_kills = inhibitor_kills
        self.cs = cs
        self.monsters = monsters
        self.vision_bought = vision_bought
        self.wards_placed = wards_placed
        self.wards_killed = wards_killed
        self.first_blood = first_blood
        self.first_tower = first_tower
        self.first_inhibitor = first_inhibitor
        self.score = score
        self.runes = runes


class LoLMatchDetailedDamagePackage:
    def __init__(self, total, physical, magical, true):
        self.total = total
        self.physical = physical
        self.magical = magical
        self.true = true


class LoLMatchDetailedRunePackage:
    def __init__(self, name, style, var_vals):
        self.name = name
        self.style = style
        self.var_vals = var_vals
