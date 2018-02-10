# region Imports
import json
import re
import requests
import sys

from discord.ext import commands
try:
    import riotwatcher
except ImportError:
    print('Riotwatcher not found.')
    print('pip install riotwatcher.')
    sys.exit(2)
try:
    import py_gg
except ImportError:
    print('Py_gg not found.')
    print('pip install py_gg.')
    sys.exit(2)

from value import GeneralValues as Gv, LeagueValues as Lv
from manager import CacheManager, DatabaseManager, FileManager
from structure import LoLPlayer, LoLMatchList, LoLMatchDetailed
# endregion


class DiscoLoLCog:
    def __init__(self, bot, riot_key, ch_gg_key, cache, database, file):
        if not isinstance(bot, commands.Bot) \
                or not isinstance(cache, CacheManager.CacheManager) \
                or not isinstance(database, DatabaseManager.DatabaseManager) \
                or not isinstance(file, FileManager.FileManager):
            return
        self.__bot = bot
        self.__watcher = riotwatcher.RiotWatcher(riot_key)
        self.ch_gg_key = ch_gg_key
        self.__file = file
        self.__cache = cache
        self.__database = database
        self.__current_patch = self.__get_latest_patch()

    # region Commands
    @commands.group(pass_context=True)
    async def lol(self, ctx):
        # The command group for all lol-related commands
        if ctx.invoked_subcommand is None:
            await self.__bot.say('Invalid Command: {}. <:dab:390040479951093771>'.format(ctx.subcommand_passed))

    @lol.command(name='help', aliases=[],
                 pass_context=True, help='Show commands.')
    async def help(self, ctx):
        print('Command: {}'.format(ctx.command))
        # A special command that simply displays all of the command usages.
        msg = await self.__bot.say('You invoked the help command. <:dab:390040479951093771>')
        for e in self.__bot.get_all_emojis():
            if e.name == 'hellyeah':
                await self.__bot.add_reaction(msg, e)
            elif e.name == 'dorawinifred':
                await self.__bot.add_reaction(msg, e)
            elif e.name == 'cutegroot':
                await self.__bot.add_reaction(msg, e)

    @lol.command(name='player', aliases=['summoner'],
                 pass_context=True, help='Get player info.')
    async def player(self, ctx, *, cmd_input: str=None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('player'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('player'))
            return
        name = inputs[0]
        _, region, _ = self.__parse_args(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__bot.say('Region **{}** not found.'.format(region))
            return
        region = region_temp
        # Check Cache
        str_key = (region, name, Gv.CacheKeyType.STR_LOL_PLAYER)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            Gv.print_cache(str_key, False)
            # Get Data Objects via API
            player = self.__find_player(region, name)
            if player is None:
                await self.__bot.say('Player **{}** not found in region **{}**.'.format(name, region))
                return
            ranks = self.__find_ranks(region, player['id'])
            if ranks is None:
                await self.__bot.say('Player **{}** not found in region **{}**'.format(name, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_player(region, player, ranks)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        else:
            Gv.print_cache(str_key, True)
        # Display Storage Structure
        await self.__bot.say('{}{}{}{}.png'.format(Lv.base_url, self.__current_patch,
                                                   Lv.profile_icon_url_part,
                                                   cached.icon))
        for s in cached.to_str():
            await self.__bot.say('```{}```'.format(s))

    @lol.command(name='matchlist', aliases=['matches'],
                 pass_context=True, help='Get most recent matches.')
    async def matchlist(self, ctx, *, cmd_input: str=None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('matchlist'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('matchlist'))
            return
        name = inputs[0]
        # Get and Check Region
        _, region, others = self.__parse_args(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__bot.say('Region **{}** not found.'.format(region))
            return
        region = region_temp

        # Get and Check Amount
        _, amount, _ = self.__parse_args(others, 'a', True)
        if amount is None:
            amount = Lv.default_amount_range_match_list[1]
        elif int(amount) > Lv.default_amount_range_match_list[1]:
            await self.__bot.say('Amount should be between {} and {}.'
                                 .format(Lv.default_amount_range_match_list[0],
                                         Lv.default_amount_range_match_list[1]))
            amount = Lv.default_amount_range_match_list[1]
        elif int(amount) < Lv.default_amount_range_match_list[0]:
            await self.__bot.say('Amount should be between {} and {}.'
                                 .format(Lv.default_amount_range_match_list[0],
                                         Lv.default_amount_range_match_list[1]))
            amount = Lv.default_amount_range_match_list[0]
        else:
            amount = int(amount)

        # Check Cache
        str_key = (region, name, Gv.CacheKeyType.STR_LOL_MATCH_LIST)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            Gv.print_cache(str_key, False)
            # Get Data Objects via API
            player = self.__find_player(region, name)
            if player is None:
                await self.__bot.say('Player **{}** not found in region **{}**.'.format(name, region))
                return
            matchlist = self.__find_match_list(region, player['accountId'])
            if matchlist is None:
                await self.__bot.say('Recent matches not found for player **{}** in region **{}**.'
                                     .format(name, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_match_list(region, player, matchlist)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        else:
            Gv.print_cache(str_key, True)
        # Display Storage Structure
        for s in cached.to_str(amount):
            await self.__bot.say('```{}```'.format(s))

    @lol.command(name='match', aliases=[],
                 pass_context=True, help='Get match info.')
    async def match(self, ctx, *, cmd_input: str=None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('match'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('match'))
            return
        # Can be one input or two
        if len(inputs) < 2:
            match_id = inputs[0]
            name = None
            index = None
        else:
            match_id = None
            name = inputs[0]
            index = inputs[1]
            try:
                index = int(index)
            except ValueError:
                await self.__bot.say('Second input must be a number.')
                return
            if index < Lv.default_amount_range_match_list[0]:
                index = Lv.default_amount_range_match_list[0]
            elif index > Lv.default_amount_range_match_list[1]:
                index = Lv.default_amount_range_match_list[1]

        # Get and Check Region
        _, region, others = self.__parse_args(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__bot.say('Region **{}** not found.'.format(region))
            return
        region = region_temp
        # Get and Check Flags
        use_rune, _, others = self.__parse_args(others, 'rd')
        use_detail, _, others = self.__parse_args(others, 'd')
        use_timeline, _, _ = self.__parse_args(others, 't')
        # Check Cache
        str_key = (region, match_id, Gv.CacheKeyType.STR_LOL_MATCH_DETAILED)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            Gv.print_cache(str_key, False)
            # Get Data Objects via API
            if index is not None:
                player = self.__find_player(region, name)
                if player is None:
                    self.__bot.say('Player **{}** not found in region **{}**.'.format(name, region))
                    return
                matchlist = self.__find_match_list(region, player['accountId'])
                if matchlist is None:
                    await self.__bot.say(
                        'Recent matches not found for player **{}** in region **{}**.'.format(name, region))
                    return
                match_id = matchlist['matches'][index - 1]['gameId']
            match = self.__find_match(region, match_id)
            if match is None:
                await self.__bot.say('Match **{}** not found in region **{}**.'.format(match_id, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_match_detailed(region, match)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        else:
            Gv.print_cache(str_key, True)
        # Display Storage Structure
        for s in cached.to_str(use_rune, use_detail, use_timeline):
            await self.__bot.say('```{}```'.format(s))
    # endregion

    # region Retrieval, API Calls
    def __find_player(self, region, name):
        if region is None or name is None:
            return None
        api_key = (region, name, Gv.CacheKeyType.API_LOL_PLAYER)
        cached = self.__cache.retrieve(api_key, CacheManager.CacheType.API)
        if cached is None:
            Gv.print_cache(api_key, False)
            try:
                player = self.__watcher.summoner.by_name(region, name)
                self.__cache.add(api_key, player, CacheManager.CacheType.API)
                return player
            except requests.HTTPError as e:
                self.__print_http_error(e)
                return None
        else:
            Gv.print_cache(api_key, True)
            return cached

    def __find_ranks(self, region, player_id):
        if region is None or player_id is None:
            return None
        api_key = (region, player_id, Gv.CacheKeyType.API_LOL_RANKS)
        cached = self.__cache.retrieve(api_key, CacheManager.CacheType.API)
        if cached is None:
            Gv.print_cache(api_key, False)
            try:
                ranks = self.__watcher.league.positions_by_summoner(region, player_id)
                self.__cache.add(api_key, ranks, CacheManager.CacheType.API)
                return ranks
            except requests.HTTPError as e:
                self.__print_http_error(e)
                return None
        else:
            Gv.print_cache(api_key, True)
            return cached

    def __find_match_list(self, region, account_id):
        if region is None or account_id is None:
            return None
        api_key = (region, account_id, Gv.CacheKeyType.API_LOL_MATCH_LIST)
        cached = self.__cache.retrieve(api_key, CacheManager.CacheType.API)
        if cached is None:
            Gv.print_cache(api_key, False)
            try:
                matchlist = self.__watcher.match.matchlist_by_account_recent(region, account_id)
                self.__cache.add(api_key, matchlist, CacheManager.CacheType.API)
                return matchlist
            except requests.HTTPError as e:
                self.__print_http_error(e)
                return None
        else:
            Gv.print_cache(api_key, True)
            return cached

    def __find_match(self, region, match_id):
        if region is None or match_id is None:
            return None
        api_key = (region, match_id, Gv.CacheKeyType.API_LOL_MATCH)
        cached = self.__cache.retrieve(api_key, CacheManager.CacheType.API)
        if cached is None:
            Gv.print_cache(api_key, False)
            try:
                match = self.__watcher.match.by_id(region, match_id)
                self.__cache.add(api_key, match, CacheManager.CacheType.API)
                return match
            except requests.HTTPError as e:
                self.__print_http_error(e)
                return None
        else:
            Gv.print_cache(api_key, True)
            return cached
    # endregion

    # region Factory
    @staticmethod
    def __create_player(region, player, ranks):
        if region is None or player is None or ranks is None:
            return None
        str_ranks = []
        for r in ranks:
            str_ranks.append(
                LoLPlayer.LoLPlayerRankPackage(r['leagueName'], r['queueType'],
                                               r['tier'], r['rank'],
                                               r['leaguePoints'], r['wins'],
                                               r['losses'], r['veteran'],
                                               r['inactive'], r['freshBlood'],
                                               r['hotStreak']))
        return LoLPlayer.LoLPlayer(region, player['name'], player['id'],
                                   player['accountId'], player['summonerLevel'],
                                   player['profileIconId'], str_ranks)

    def __create_match_list(self, region, player, matchlist):
        matches = []
        for m in matchlist['matches']:
            match = self.__find_match(region, m['gameId'])
            if match is None:
                print('Match {} not found.'.format(m['gameId']))
                continue
            matches.append(self.__create_match(region, player, match, m))
        return LoLMatchList.LoLMatchList(region, player['name'], player['id'], player['accountId'], matches)

    def __create_match(self, region, player, match, match_details):
        queue_results = self.__database.select_lol_queue(match_details['queue'], True, True)
        if queue_results is None:
            print('Queue Not Found: {}.'.format(match_details['queue']))
            return None
        queue = '{}: {}{}'.format(queue_results['map'],
                                  queue_results['mode'],
                                  '' if queue_results['extra'] is None
                                  else ' {}'.format(queue_results['extra']))

        indices = self.__get_indicies_from_match(player['accountId'], match, queue_results['numOfPlayers'])
        if indices is None:
            print('Something went wrong when getting indices from match.')
        player_stats = match['participants'][indices[0] - 1]['stats']

        season_results = self.__database.select_lol_season(match_details['season'])
        if season_results is None:
            print('Season Not Found: {}'.format(match_details['season']))
            return None
        champion_results = self.__database.select_lol_champion(match_details['champion'])
        if champion_results is None:
            print('Champion Not Found: {}'.format(match_details['champion']))
            return None

        return LoLMatchList.LoLMatch(region, match_details['gameId'],
                                     [match_details['champion'], champion_results],
                                     [match_details['queue'], queue],
                                     [match_details['season'], season_results],
                                     match_details['role'], match_details['lane'],
                                     [player_stats['kills'], player_stats['deaths'],
                                      player_stats['assists']],
                                     player_stats['totalMinionsKilled'],
                                     player_stats['timeCCingOthers'],
                                     player_stats['visionScore'],
                                     player_stats['win'], queue_results['hasLanes'])

    def __create_match_detailed(self, region, match):
        queue_results = self.__database.select_lol_queue(match['queueId'],
                                                         True, True, True,
                                                         True, True, True, True,
                                                         True, True, True)
        queue = '{}: {}{}'.format(queue_results['map'],
                                  queue_results['mode'],
                                  '' if queue_results['extra'] is None
                                  else ' {}'.format(queue_results['extra']))

        season_results = self.__database.select_lol_season(match['seasonId'])

        team1 = self.__create_match_detailed_team(match, 0, queue_results)
        team2 = self.__create_match_detailed_team(match, 1, queue_results)

        return LoLMatchDetailed.LoLMatchDetailed(
            region, match['gameId'], [match['queueId'], queue],
            [match['seasonId'], season_results], match['gameDuration'],
            [team1, team2]
        )

    def __create_match_detailed_team(self, match, index, queue_results):
        players_per_team = queue_results['numOfPlayers'] // 2
        team = match['teams'][index]
        if index == 0:
            offset = 0
            participants = match['participants'][:players_per_team]
        else:
            offset = players_per_team
            participants = match['participants'][players_per_team:]

        players = []
        for i, p in enumerate(participants):
            players.append(self.__create_match_detailed_player(
                    match['participantIdentities'][i + offset]['player']['summonerName'],
                    p, queue_results
                ))

        bans = []
        for b in team['bans']:
            champ = self.__database.select_lol_champion(b['championId'])
            bans.append([b['championId'], champ])

        return LoLMatchDetailed.LoLMatchDetailedTeamPackage(
            team['win'] == 'Win', [queue_results['hasTowers'], team['towerKills']],
            [queue_results['hasTowers'], team['inhibitorKills']],
            [queue_results['hasDragons'], team['dragonKills']],
            [queue_results['hasBarons'], team['baronKills']],
            [queue_results['hasHeralds'], team['riftHeraldKills']],
            [queue_results['hasVilemaws'], team['vilemawKills']],
            team['firstBlood'], team['firstTower'], team['firstInhibitor'],
            team['firstDragon'], team['firstBaron'],
            [queue_results['hasScore'], team['dominionVictoryScore']],
            bans, players
        )

    def __create_match_detailed_player(self, name, player, queue_results):
        stats = player['stats']
        timeline = player['timeline']
        champion = self.__database.select_lol_champion(player['championId'])
        spell1 = self.__database.select_lol_summoner_spell(player['spell1Id'])
        spell2 = self.__database.select_lol_summoner_spell(player['spell2Id'])

        items = []
        for i in range(0, 7):
            item = self.__database.select_lol_item(stats['item{}'.format(i)])
            items.append([stats['item{}'.format(i)], item])

        runes = []
        for r in range(0, 6):
            runes.append(self.__create_match_detailed_rune(stats, r))

        damage_dealt = LoLMatchDetailed.LoLMatchDetailedDamagePackage(
            stats['totalDamageDealt'], stats['magicDamageDealt'],
            stats['physicalDamageDealt'], stats['trueDamageDealt']
        )

        damage_to_champs = LoLMatchDetailed.LoLMatchDetailedDamagePackage(
            stats['totalDamageDealtToChampions'], stats['magicDamageDealtToChampions'],
            stats['physicalDamageDealtToChampions'], stats['trueDamageDealtToChampions']
        )

        damage_taken = LoLMatchDetailed.LoLMatchDetailedDamagePackage(
            stats['totalDamageTaken'], stats['magicalDamageTaken'],
            stats['physicalDamageTaken'], stats['trueDamageTaken']
        )

        timelines = []
        times = ['0-10', '10-20', '20-30', '30-end']
        headers = ['creepsPerMinDeltas', 'csDiffPerMinDeltas', 'xpPerMinDeltas',
                   'xpDiffPerMinDeltas', 'goldPerMinDeltas', 'damageTakenPerMinDeltas',
                   'damageTakenDiffPerMinDeltas']
        for h in headers:
            data = timeline[h]
            timeline_single = []
            for t in times[:len(data)]:
                timeline_single.append([t, data[t]])
            timelines.append(LoLMatchDetailed.LoLMatchDetailedTimelinePackage(timeline_single))

        return LoLMatchDetailed.LoLMatchDetailedPlayerPackage(
            name, [player['championId'], champion], timeline['role'],
            timeline['lane'],
            [[player['spell1Id'], spell1], [player['spell2Id'], spell2]],
            items, runes, [stats['kills'], stats['deaths'], stats['assists']],
            stats['largestKillingSpree'], stats['largestMultiKill'],
            stats['doubleKills'], stats['tripleKills'], stats['quadraKills'],
            stats['pentaKills'], stats['unrealKills'], stats['largestCriticalStrike'],
            damage_dealt, damage_to_champs, damage_taken, stats['totalHeal'],
            stats['damageSelfMitigated'], stats['damageDealtToObjectives'],
            stats['damageDealtToTurrets'], [queue_results['hasVision'],
                                            stats['visionScore'],
                                            stats['visionWardsBoughtInGame']],
            stats['timeCCingOthers'], [stats['goldSpent'], stats['goldEarned']],
            [queue_results['hasTowers'], stats['turretKills']],
            [queue_results['hasTowers'], stats['inhibitorKills']],
            stats['totalMinionsKilled'],
            [queue_results['hasMonsters'], stats['neutralMinionsKilled']],
            [stats['firstBloodKill'], stats['firstBloodAssist']],
            [stats['firstTowerKill'], stats['firstTowerAssist']],
            [stats['firstInhibitorKill'], stats['firstInhibitorAssist']],
            [queue_results['hasScore'], stats['totalPlayerScore']],
            queue_results['hasLanes'], timelines
        )

    def __create_match_detailed_rune(self, stats, index):
        rune_string = 'perk{}'.format(index)
        style = stats['perkPrimaryStyle'] if index < 4 else stats['perkSubStyle']
        style_results = self.__database.select_lol_rune_style(style)
        rune_results = self.__database.select_lol_rune(stats[rune_string])

        rune_vars = []
        did_time = False
        did_percent = False
        did_sec = False
        for i, v in enumerate(rune_results['vars']):
            if v is None:
                continue
            if rune_results['hasTimeVar'] and not did_time:
                val = '{}:{:02d}'\
                    .format(stats['{}Var{}'.format(rune_string, i + 1)],
                            stats['{}Var{}'.format(rune_string, i + 2)])
                rune_vars.append([v, val])
                did_time = True
            elif rune_results['hasPercentVar'] and not did_percent:
                val = '{}%' \
                    .format(stats['{}Var{}'.format(rune_string, i + 1)])
                rune_vars.append([v, val])
                did_percent = True
            elif rune_results['hasSecVar'] and not did_sec:
                val = '{}s' \
                    .format(stats['{}Var{}'.format(rune_string, i + 1)])
                rune_vars.append([v, val])
                did_sec = True
            elif rune_results['hasPerfectVar']:
                print('time var')
                val = 'Perfect'
                rune_vars.append([v, val])
            elif not did_time or not did_percent or not did_sec:
                rune_vars.append([v, stats['{}Var{}'.format(rune_string, i + 1)]])

        return LoLMatchDetailed.LoLMatchDetailedRunePackage(
            stats[rune_string], [style, style_results],
            rune_results['name'], rune_vars
        )
    # endregion

    # region Parsing
    @staticmethod
    def __parse_inputs_and_args(inp, arg_prefix=Gv.argument_prefix):
        splits = re.split(' ?{}'.format(arg_prefix), inp)
        inp_splits = re.split(' ? ', splits[0])
        return inp_splits, splits[1:]

    @staticmethod
    def __parse_args(args, arg, has_value=False,
                     arg_value_prefix=Gv.argument_value_prefix):
        value = None
        found = False
        index = -1
        for i, a in enumerate(args):
            try:
                split = re.split(arg_value_prefix, a)
            except ValueError:
                print('Value Error when splitting {} on {}.'.format(a, arg_value_prefix))
                return None
            if split[0] == arg:
                if has_value:
                    if len(split) > 1:
                        value = split[1]
                found = True
                index = i
                break
        return found, value, [a for i, a in enumerate(args) if i != index]
    # endregion

    @staticmethod
    def __get_region(region):
        if region is None:
            return Lv.default_region
        if region not in Lv.regions_list:
            if region + Lv.optional_region_suffix not in Lv.regions_list:
                return None
            else:
                return region + Lv.optional_region_suffix
        return region

    @staticmethod
    def __get_indicies_from_match(player_id, match, num_of_players):
        player_index = None
        for p in match['participantIdentities']:
            if p['player']['currentAccountId'] == player_id:
                player_index = p['participantId']
        if player_index is None:
            return None
        if player_index < num_of_players / 2:
            team_index = 1
        else:
            team_index = 2
        return player_index, team_index

    def __get_latest_patch(self):
        self.__file.download_file(Gv.FileType.JSON, Lv.version_file, Lv.version_url)
        with open(Lv.version_path, 'r', encoding='utf-8') as file:
            json_file = json.loads(file.read())
        return json_file[0]

    @staticmethod
    def __get_command_usage(command, prefix=Gv.argument_prefix, value_prefix=Gv.argument_value_prefix):
        if command == 'player':
            return 'player *name* [{}r{}*region*]'\
                .format(prefix, value_prefix)
        elif command == 'matchlist':
            return 'matchlist *name* [{}r{}*region*] [{]a{}*amount* 1-20]'\
                .format(prefix, value_prefix, prefix, value_prefix)
        elif command == 'match':
            return 'match *id* [{}r{}*region*] [{}rd] [{}d] [{}t]'\
                .format(prefix, value_prefix, prefix, prefix, prefix)
        else:
            return ''

    async def __display_not_yet_implemented(self, command_name):
        await self.__bot.say('{} has not yet been implemented. <:dab:390040479951093771>'.format(command_name))

    @staticmethod
    def __print_http_error(e):
        if e.response.status_code == 403:
            print('HTTP Error {}. Is the API Key expired?'.format(e.response.status_code))
        elif e.response.status_code == 404:
            print('HTTP Error {}. Query not found.'.format(e.response.status_code))
        else:
            print('HTTP Error {}'.format(e.response.status_code))
