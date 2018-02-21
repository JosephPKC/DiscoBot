import random
import re
import requests
import sys
from discord.ext import commands
try:
    import riotwatcher
except ImportError:
    riotwatcher = None
    print('Riotwatcher not found.')
    print('pip install riotwatcher.')
    sys.exit(2)
try:
    import py_gg
except ImportError:
    py_gg = None
    print('Py_gg not found.')
    print('pip install py_gg.')
    sys.exit(2)
# region Data and Managers
from value import GeneralValues as Gv, LeagueValues as Lv
from manager import CacheManager as Cache, LoLDatabase as Database, FileManager as File
# endregion
# region Structures
from structure import DiscoHelp, LoLBuildOrder, LoLMatchDetailed, LoLMatchList, LoLMatchTimeline, LoLPlayer
# endregion
'''

'''


class DiscoLoLCog:
    # region Constants
    # region Mappings
    __command_info_list_map = {
        'player': ['{}player <player> [{}r{}<region>]'
                   .format(Gv.bot_prefix, Gv.bot_arg_prefix, Gv.bot_arg_value_prefix),
                   'Get information on given player.',
                   ['r - Set the region. Default: {}.'.format(Lv.default_region)]
                   ]
    }
    # endregion
    # endregion

    def __init__(self, bot, riot_key, ch_gg_key):
        self.__bot = bot
        self.__watcher = riotwatcher.RiotWatcher(riot_key)
        self.__help = self.__create_help()
        self.__current_patch = self.__find_current_patch()
        py_gg.init(ch_gg_key)

    # region Commands
    @commands.group(name='lol', pass_context=True)
    async def __group_lol(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.__bot.say('Invalid Command: {}. <:dab:390040479951093771>'.format(ctx.subcommand_passed))

    @__group_lol.command(name='help', pass_context=True, aliases=['?'])
    async def __cmd_help(self, ctx, cmd_input: str = None):
        Gv.print_command(ctx.command, cmd_input)
        msg = await self.__display_embed('{}'.format(ctx.message.author.mention), self.__help.embed(ctx))
        await self.__react_to(msg, ['hellyeah', 'dorawinifred', 'cutegroot', 'dab'])

    # region Riotwatcher Commands
    @__group_lol.command(name='buildorder', pass_context=True)
    async def __cmd_build_order(self, ctx, *, cmd_input: str=None):
        Gv.print_command(ctx.command, cmd_input)
        # Parse into Inputs and Args
        inputs = await self.__help_with_inputs(cmd_input, 2, 'buildorder')
        if inputs is None:
            return
        # Get inputs
        name = inputs[0][0]
        mid = await self.__help_with_match_index(inputs[0][1])
        if mid is None:
            return
        args = inputs[1]
        # Get arguments
        region = await self.__help_with_region(args)
        if region is None:
            return
        # Get mid
        if mid < 1000:
            mid = await self.__help_with_match_id(region, name, mid)
            if mid is None:
                return
        # Check Cache
        str_key = (region, mid, Cache.StrKey.LoL.BUILD_ORDER)
        cached = Cache.retrieve(str_key, Cache.CacheType.STR)
        if cached is None:
            # Find API
            try:
                timeline = self.__find_match_timeline(region, mid)
            except requests.HTTPError as e:
                self.__print_http_error(e)
                await self.__display_not_found_timeline(mid, region)
                return
            # Create and Cache
            cached = self.__create_build_order(region, name, mid, timeline)
            Cache.add(str_key, cached, Cache.CacheType.STR)
        # Display
        for e in cached.embed(ctx):
            await self.__bot.say(embed=e)

    @__group_lol.command(name='masteries', pass_context=True)
    async def __cmd_masteries(self, ctx, *, cmd_input: str=None):
        return

    @__group_lol.command(name='match', pass_context=True)
    async def __cmd_match(self, ctx, *, cmd_input: str=None):
        Gv.print_command(ctx.command, cmd_input)
        # Parse into Inputs and Args
        inputs = await self.__help_with_inputs(cmd_input, 1, 'match')
        if inputs is None:
            return
        # Get inputs
        inps = await self.__help_with_match_index_or_id(inputs[0])
        if inps is None:
            return
        name, index, mid = inps[0], inps[1], inps[2]
        args = inputs[1]
        # Get arguments
        region = await self.__help_with_region(args)
        if region is None:
            return
        use_rune, _ = self.__parse_arg(args, 'ru', True)
        use_detail, _ = self.__parse_arg(args, 'd', True)
        # Get mid
        if mid is None:
            mid = await self.__help_with_match_id(region, name, index)
            if mid is None:
                return
        # Check Cache
        str_key = (region, mid, Cache.StrKey.LoL.MATCH_DETAILED)
        cached = Cache.retrieve(str_key, Cache.CacheType.STR)
        if cached is None:
            # Find API
            try:
                match = self.__find_match(region, mid)
            except requests.HTTPError as e:
                self.__print_http_error(e)
                await self.__display_http_error(e, item=mid)
                return
            # Create and Cache
            cached = self.__create_match(region, match)
            Cache.add(str_key, cached, Cache.CacheType.STR)
        for e in cached.embed(ctx, use_rune, use_detail):
            await self.__bot.say(embed=e)

    @__group_lol.command(name='matchlist', pass_context=True, aliases=['matches'])
    async def __cmd_match_list(self, ctx, *, cmd_input: str=None):
        Gv.print_command(ctx.command, cmd_input)
        # Parse into Inputs and Args
        inputs = await self.__help_with_inputs(cmd_input, 1, 'matchlist')
        if inputs is None:
            return
        # Get inputs
        name = inputs[0][0]
        args = inputs[1]
        # Get arguments
        region = await self.__help_with_region(args)
        if region is None:
            return
        amount = await self.__help_with_amount(args)
        if amount is None:
            return
        # Check Cache
        str_key = (region, name.lower(), Cache.StrKey.LoL.MATCH_LIST)
        cached = Cache.retrieve(str_key, Cache.CacheType.STR)
        if cached is None:
            # Find API
            try:
                player = self.__find_player(region, name.lower())
            except requests.HTTPError as e:
                self.__print_http_error(e)
                await self.__display_http_error(e, item=name, location=region)
                return
            try:
                matchlist = self.__get_detailed_match_list(region, player['accountId'])
            except requests.HTTPError as e:
                self.__print_http_error(e)
                await self.__display_not_found_match_list(name, region)
                return
            # Create and Cache
            cached = self.__create_match_list(region, player, matchlist)
            Cache.add(str_key, cached, Cache.CacheType.STR)

        await self.__bot.say(content='{}'.format(ctx.message.author.mention), embed=cached.embed(ctx, amount))

    @__group_lol.command(name='player', pass_context=True, aliases=['summoner', 'profile'])
    async def __cmd_player(self, ctx, *, cmd_input: str=None):
        # await self.__bot.say('<{}:{}>'.format('bronze_i', Repo.emoji_id_map['bronze_i']))
        Gv.print_command(ctx.command, cmd_input)
        # Parse into Inputs and Args
        inputs = await self.__help_with_inputs(cmd_input, 1, 'player')
        if inputs is None:
            return
        # Get inputs
        name = inputs[0][0]
        args = inputs[1]
        # Get arguments
        region = await self.__help_with_region(args)
        if region is None:
            return
        # Check Cache
        str_key = (region, name.lower(), Cache.StrKey.LoL.PLAYER)
        cached = Cache.retrieve(str_key, Cache.CacheType.STR)
        if cached is None:
            # Find API
            try:
                player = self.__find_player(region, name.lower())
            except requests.HTTPError as e:
                self.__print_http_error(e)
                await self.__display_http_error(e, item=name, location=region)
                return
            try:
                ranks = self.__find_ranks(region, player['id'])
                masteries = self.__find_masteries(region, player['id'])
            except requests.HTTPError as e:
                self.__print_http_error(e)
                await self.__display_http_error(e)
                return
            try:
                matchlist = self.__get_detailed_match_list(region, player['accountId'], Lv.queues_standard_list)
            except requests.HTTPError:
                await self.__display_not_found_match_list(name, region)
                return
            # Create and Cache
            cached = self.__create_player(region, player, ranks, matchlist, masteries)
            Cache.add(str_key, cached, Cache.CacheType.STR)

        await self.__bot.say(content='{}'.format(ctx.message.author.mention), embed=cached.embed(ctx))

    @__group_lol.command(name='timeline', pass_context=True)
    async def __cmd_timeline(self, ctx, *, cmd_input: str = None):
        Gv.print_command(ctx.command, cmd_input)
        # Parse into Inputs and Args
        inputs = await self.__help_with_inputs(cmd_input, 1, 'timeline')
        if inputs is None:
            return
        # Get inputs
        inps = await self.__help_with_match_index_or_id(inputs[0])
        if inps is None:
            return
        name, index, mid = inps[0], inps[1], inps[2]
        args = inputs[1]
        # Get arguments
        region = await self.__help_with_region(args)
        if region is None:
            return
        # Get mid
        if mid is None:
            mid = await self.__help_with_match_id(region, name, index)
            if mid is None:
                return
        # Check Cache
        str_key = (region, mid, Cache.StrKey.LoL.MATCH_TIMELINE)
        cached = Cache.retrieve(str_key, Cache.CacheType.STR)
        if cached is None:
            # Find API
            try:
                timeline = self.__find_match_timeline(region, mid)
            except requests.HTTPError as e:
                self.__print_http_error(e)
                await self.__display_not_found_timeline(mid, region)
                return
            try:
                match = self.__find_match(region, mid)
            except requests.HTTPError as e:
                self.__print_http_error(e)
                await self.__display_http_error(e)
                return
            # Create and Cache
            cached = self.__create_timeline(region, match, timeline)
            Cache.add(str_key, cached, Cache.CacheType.STR)

        for e in cached.embed(ctx):
            await self.__bot.say(embed=e)
    # endregion
    # endregion

    # region Command Error Handlers
    # region Riotwatcher Command Handlers
    @__cmd_masteries.error
    async def test(self, ctx, error):
        print(error)
        if isinstance(error, str):
            print('ERROR')
    # endregion
    # endregion

    # region Command Helpers
    # region Input Processing
    async def __help_with_inputs(self, inputs, expected, command):
        parsed = self.__parse_to_inputs_args(inputs)
        if parsed is None or len(parsed[0]) < expected or parsed[0][0] == '':
            await self.__display_bad_input(command)
            return None
        return parsed

    async def __help_with_match_id(self, region, name, index):
        try:
            mid = self.__get_match_id(region, name, index)
        except requests.HTTPError as e:
            self.__print_http_error(e)
            await self.__display_http_error(e, item=name, location=region)
            return None
        if mid is None:
            await self.__bot.say('**{}** is too large of an index.')
            return None
        if mid == -1:
            await self.__display_not_found_match_list(name, region)
            return None
        return mid

    async def __help_with_match_index(self, inputs):
        index = self.__get_match_index(inputs)
        if index is None:
            await self.__display_not_in_range(*Lv.match_index_range)
            return None
        return index

    async def __help_with_match_index_or_id(self, inputs):
        # Use to differentiate between a match id input or a player name + match index input
        name = None if len(inputs) == 1 else inputs[0]
        index = None if len(inputs) == 1 else self.__get_match_index(inputs[1])
        if len(inputs) > 1 and index is None:
            await self.__display_not_in_range(*Lv.match_index_range)
            return None
        mid = inputs[0] if len(inputs) == 1 else None
        return name, index, mid
    # endregion

    # region Argument Processing
    async def __help_with_amount(self, args):
        _, amount = self.__parse_arg(args, 'a', True)
        amount = self.__get_amount(amount)
        if amount is None:
            await self.__display_not_in_range(*Lv.match_list_range)
            return None
        return amount

    async def __help_with_region(self, args):
        # Use to get region
        _, region = self.__parse_arg(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__display_not_found(region)
            return None
        return region_temp
    # endregion
    # endregion

    # region API Retrieval
    @staticmethod
    def __find_api(params, key_type, func):
        for p in params:
            if p is None:
                return None
        key = (*params, key_type)
        cached = Cache.retrieve(key, Cache.CacheType.API)
        if cached is None:
            try:
                new_data = func(*params)
                Cache.add(key, new_data, Cache.CacheType.API)
                return new_data
            except requests.HTTPError as e:
                raise e
        return cached

    @staticmethod
    def __find_api_by_file(url, path, params, key_type, load_func):
        key = (*params, key_type)
        cached = Cache.retrieve(key, Cache.CacheType.API)
        if cached is None:
            try:
                File.download_file(File.FileType.JSON, path, url)
            except requests.HTTPError as e:
                print('HTTP ERROR: {}'.format(e))
                return None
            cached = load_func(path)
            Cache.add(key, cached, Cache.CacheType.API)

        return cached

    # region Riotwatcher Retrieval
    def __find_challengers(self, region, queue_id):
        return self.__find_api(
            params=[region, queue_id],
            key_type=Cache.ApiKey.LoL.CHALLENGERS,
            func=lambda r, qid: self.__watcher.league.challenger_by_queue(r, qid)
        )

    def __find_masters(self, region, queue_id):
        return self.__find_api(
            params=[region, queue_id],
            key_type=Cache.ApiKey.LoL.MASTERS,
            func=lambda r, qid: self.__watcher.league.masters_by_queue(r, qid)
        )

    def __find_match(self, region, match_id):
        return self.__find_api(
            params=[region, match_id],
            key_type=Cache.ApiKey.LoL.MATCH,
            func=lambda r, mid: self.__watcher.match.by_id(r, mid)
        )

    def __find_match_list_full(self, region, account_id):
        return self.__find_api(
            params=[region, account_id],
            key_type=Cache.ApiKey.LoL.MATCH_LIST_FULL,
            func=lambda r, aid: self.__watcher.match.matchlist_by_account(r, aid)
        )

    def __find_match_list_recent(self, region, account_id):
        return self.__find_api(
            params=[region, account_id],
            key_type=Cache.ApiKey.LoL.MATCH_LIST,
            func=lambda r, aid: self.__watcher.match.matchlist_by_account_recent(r, aid)
        )

    def __find_match_spectate(self, region, player_id):
        return self.__find_api(
            params=[region, player_id],
            key_type=Cache.ApiKey.LoL.SPECTATOR,
            func=lambda r, pid: self.__watcher.spectator.by_summoner(r, pid)
        )

    def __find_match_timeline(self, region, match_id):
        return self.__find_api(
            params=[region, match_id],
            key_type=Cache.ApiKey.LoL.MATCH_TIMELINE,
            func=lambda r, mid: self.__watcher.match.timeline_by_match(r, mid)
        )

    def __find_player(self, region, name):
        return self.__find_api(
            params=[region, name],
            key_type=Cache.ApiKey.LoL.PLAYER,
            func=lambda r, n: self.__watcher.summoner.by_name(r, n)
        )

    def __find_ranks(self, region, player_id):
        return self.__find_api(
            params=[region, player_id],
            key_type=Cache.ApiKey.LoL.RANKS,
            func=lambda r, pid: self.__watcher.league.positions_by_summoner(r, pid)
        )

    def __find_champion_mastery(self, region, player_id, champion_id):
        return self.__find_api(
            params=[region, player_id, champion_id],
            key_type=Cache.ApiKey.LoL.MASTERY,
            func=lambda r, pid, cid: self.__watcher.champion_mastery.by_summoner_by_champion(r, pid, cid)
        )

    def __find_masteries(self, region, player_id):
        return self.__find_api(
            params=[region, player_id],
            key_type=Cache.ApiKey.LoL.MASTERY,
            func=lambda r, pid: self.__watcher.champion_mastery.by_summoner(r, pid)
        )

    def __find_total_mastery(self, region, player_id):
        return self.__find_api(
            params=[region, player_id],
            key_type=Cache.ApiKey.LoL.TOTAL_MASTERY,
            func=lambda r, pid: self.__watcher.champion_mastery.scores_by_summoner(r, pid)
        )

    def __find_status(self, region):
        return self.__find_api(
            params=[region],
            key_type=Cache.ApiKey.LoL.STATUS,
            func=lambda r: self.__watcher.lol_status.shard_data(r)
        )
    # endregion

    # region Pygg Retrieval
    def __find_champion_stats(self, elo, champion_id):
        def func(e, cid):
            opts = {
                'champData': 'kda,damage,averageGames,goldEarned,totalheal,sprees,'
                             'minions,positions,normalized,maxMins,matchups,hashes,'
                             'overallPerformanceScore,wins,wards'
            }
            if e != Lv.elo_string_map[Lv.default_elo]:
                opts['elo'] = e
            return py_gg.champions.specific(cid, options=opts)
        return self.__find_api(
            params=[elo, champion_id],
            key_type=Cache.ApiKey.LoL.CHAMPION_STATS,
            func=func
        )
    # endregion

    # region Datadragon Retrieval
    @staticmethod
    def __find_current_patch():
        File.download_file(File.FileType.JSON, Lv.versions_file, Lv.versions_url, force_download=True)
        return File.load_json(Lv.versions_file)[0]

    def __find_champion(self, champion_name):
        url = '{}{}{}{}.json'.format(Lv.data_dragon_base_url, self.__current_patch, Lv.champion_url_part, champion_name)
        path = '{}{}_{}.json'.format(Lv.champions_path, self.__current_patch, champion_name)

        return self.__find_api_by_file(
            url=url, path=path, params=[self.__current_patch, champion_name.lower()],
            key_type=Cache.ApiKey.LoL.CHAMPION,
            load_func=lambda p: File.load_json(p)['data'][champion_name]
        )

    def __find_champion_splash_arts(self, champion_name):
        champion = self.__find_champion(champion_name)
        splash_arts = []
        for s in champion['skins']:
            splash_arts.append([s['name'], '{}{}{}_{}.jpg'
                               .format(Lv.data_dragon_base_url, Lv.champion_splash_url_part, champion_name, s['num'])])
        return splash_arts

    def __find_item(self, item_id):
        url = '{}{}{}'.format(Lv.data_dragon_base_url, self.__current_patch, Lv.items_url_part)
        path = '{}_{}'.format(self.__current_patch, Lv.items_file)

        return self.__find_api_by_file(
            url=url, path=path, params=[self.__current_patch],
            key_type=Cache.ApiKey.LoL.ITEMS,
            load_func=lambda p: File.load_json(p)['data']
        )[str(item_id)]

    def __find_profile_icon(self, icon_id, use_random=False):
        url = '{}{}{}'.format(Lv.data_dragon_base_url, self.__current_patch, Lv.profile_icons_json_url_part)
        path = '{}_{}'.format(self.__current_patch, Lv.profile_icons_file)

        cached = self.__find_api_by_file(
            url=url, path=path, params=[self.__current_patch],
            key_type=Cache.ApiKey.LoL.PROFILE_ICONS,
            load_func=lambda p: File.load_json(p)['data']
        )
        if cached is None:
            return None

        if use_random:
            size = len(cached.keys())
            index = int(random.random() * (size - 1))
            icon_id = list(cached.keys())[index]
        elif str(icon_id) not in cached:
            return None

        return '{}{}{}{}.png'.format(Lv.data_dragon_base_url, self.__current_patch, Lv.profile_icon_url_part, icon_id)
    # endregion
    # endregion

    # region Factories
    def __create_help(self):
        cmds = []
        for c, i in self.__command_info_list_map.items():
            cmds.append(DiscoHelp.DiscoHelpCommandPackage(
                c, i[0], i[1], i[2]
            ))

        return DiscoHelp.DiscoHelp(
            'LoL', cmds
        )

    def __create_build_order(self, region, name, match_id, timeline):
        match = self.__find_match(region, match_id)
        pid = 0
        pname = None
        sid = 0
        platform = 0
        # Find params
        for p in match['participantIdentities']:
            if p['player']['summonerName'].lower() == name.lower():
                pid = p['participantId']
                pname = p['player']['summonerName']
                sid = p['player']['summonerId']
                platform = p['player']['platformId']
                break
        # Champion, Url
        champion = Database.select_champion(match['participants'][pid - 1]['championId'])['name']
        url = Lv.get_match_history_url(region, platform, match_id, sid)
        # Events
        events = []
        types = ['ITEM_PURCHASED', 'ITEM_DESTROYED']
        for f in timeline['frames']:
            for e in f['events']:
                if e['type'] in types and e['participantId'] == pid:
                    item = Database.select_item(e['itemId'])['name']
                    mins, secs = Lv.get_mins_secs_from_time(e['timestamp'])
                    time = '{:02d}:{:02d}'.format(mins, secs)
                    events.append(LoLBuildOrder.LoLBuildOrderEventPackage(
                        e['type'], time, item
                    ))
        return LoLBuildOrder.LoLBuildOrder(
            Lv.region_string_map[region], pname, match_id, champion, events, url
        )

    def __create_match(self, region, match):
        # Season, Queue, Duration, URL
        season = Database.select_season(match['seasonId'])['name']
        queue_results = Database.select_queue(match['queueId'], all=True)
        queue = self.__get_queue(queue_results)
        duration = self.__get_time(match['gameDuration'])
        url = Lv.get_match_history_url(region, match['platformId'], match['gameId'])
        # Teams
        teams = []
        for i in range(0, 2):
            teams.append(self.__build_match_team(region, match, i))
        return LoLMatchDetailed.LoLMatchDetailed(
            Lv.region_string_map[region], match['gameId'], season, queue, duration, teams, queue_results['hasLanes'],
            queue_results['hasTowers'], queue_results['hasTowers'], queue_results['hasDragons'],
            queue_results['hasBarons'], queue_results['hasHeralds'], queue_results['hasVilemaws'],
            queue_results['hasScore'], queue_results['hasVision'], queue_results['hasMonsters'], url
        )

    def __create_match_list(self, region, player, matchlist):
        # URL
        url = Lv.get_op_gg_url(region, player['name'])
        # Matches
        matches = []
        for m in matchlist:
            matches.append(self.__build_match_list_match(player, m))
        return LoLMatchList.LoLMatchList(
            Lv.region_string_map[region], player['name'], url, matches
        )

    def __create_player(self, region, player, ranks, matchlist, masteries):
        url = Lv.get_op_gg_url(region, player['name'])
        # Create Ranks
        ranks_list = []
        for r in ranks:
            ranks_list.append(self.__build_player_rank(r))
        # Create Masteries
        masteries_list = []
        for m in masteries[:5]:
            masteries_list.append(self.__build_player_mastery(m))
        # Calculate Recent Matches
        recent_games, recent_wins = len(matchlist), 0
        kills, deaths, assists, vision, cs = 0, 0, 0, 0, 0
        for m in matchlist:
            number_of_players = Database.select_queue(m['queueId'], num_of_players=True)['numOfPlayers']
            participant_id = self.__get_participant_id(m['participantIdentities'], player['accountId'])
            team_id = self.__get_team_id(participant_id, number_of_players)
            recent_wins, kills, deaths, assists, vision, cs = self.__build_player_recent_match(
                m['teams'][team_id // 100 - 1], m['participants'][participant_id - 1]['stats'], recent_wins,
                kills, deaths, assists, vision, cs
            )
        recent_losses = recent_games - recent_wins
        if recent_games > 0:
            kills /= recent_games
            deaths /= recent_games
            assists /= recent_games
            vision /= recent_games
            cs /= recent_games
        # Create Player
        return LoLPlayer.LoLPlayer(
            player['name'], Lv.region_string_map[region], url, player['profileIconId'],
            self.__find_profile_icon(player['profileIconId']), player['summonerLevel'], ranks_list,
            masteries_list, recent_games, recent_wins, recent_losses, kills, deaths, assists, vision, cs
        )

    def __create_timeline(self, region, match, timeline):
        # Season, Queue, URL
        season = Database.select_season(match['seasonId'])['name']
        queue = self.__get_queue(Database.select_queue(match['queueId']))
        url = Lv.get_match_history_url(region, match['platformId'], match['gameId'])
        # Teams
        teams = []
        for i in [100, 200]:
            teams.append(self.__build_timeline_team(match, i))
        num_of_players = len(timeline['frames'][0]['participantFrames'])
        # Events
        events = []
        for f in timeline['frames']:
            for e in f['events']:
                event = self.__build_timeline_event(e, teams, num_of_players)
                if event is not None:
                    events.append(event)
        return LoLMatchTimeline.LoLMatchTimeline(
            Lv.region_string_map[region], match['gameId'], season, queue, teams, events, url
        )
    # endregion

    # region Factory Builders
    # region Match Builders
    def __build_match_team(self, region, match, index):
        # Bans
        team = match['teams'][index]
        bans = []
        for b in team['bans']:
            champ = Database.select_champion(b['championId'])
            bans.append(champ['name'] if champ is not None else 'None')
        # Players
        start = 0 if team['teamId'] == 100 else len(match['participants']) // 2
        end = start + len(match['participants']) // 2
        players = []
        for i in range(start, end):
            players.append(self.__build_match_player(region, match, i))
        return LoLMatchDetailed.LoLMatchDetailedTeamPackage(
            team['teamId'], team['win'] == 'Win', team['firstBlood'], team['firstTower'], team['firstInhibitor'],
            team['firstBaron'], team['firstDragon'], team['firstRiftHerald'], team['towerKills'],
            team['inhibitorKills'], team['baronKills'], team['dragonKills'], team['vilemawKills'],
            team['riftHeraldKills'], team['dominionVictoryScore'], bans, players
        )

    def __build_match_player(self, region, match, index):
        player = match['participants'][index]
        timeline = player['timeline']
        stats = player['stats']
        identity = match['participantIdentities'][index]['player']
        champion = Database.select_champion(player['championId'])['name']
        spell1 = Database.select_summoner_spell(player['spell1Id'])['name']
        spell2 = Database.select_summoner_spell(player['spell2Id'])['name']
        items = []
        for i in range(0, 7):
            item = Database.select_item(stats['item{}'.format(i)])
            items.append(item['name'] if item is not None else 'None')
        damage_dealt = LoLMatchDetailed.LoLMatchDetailedDamagePackage(
            stats['totalDamageDealt'], stats['physicalDamageDealt'], stats['magicDamageDealt'], stats['trueDamageDealt']
        )
        damage_to_champs = LoLMatchDetailed.LoLMatchDetailedDamagePackage(
            stats['totalDamageDealtToChampions'], stats['physicalDamageDealtToChampions'],
            stats['magicDamageDealtToChampions'], stats['trueDamageDealtToChampions']
        )
        damage_taken = LoLMatchDetailed.LoLMatchDetailedDamagePackage(
            stats['totalDamageTaken'], stats['physicalDamageTaken'], stats['magicalDamageTaken'],
            stats['trueDamageTaken']
        )
        runes = []
        for i in range(0, 6):
            runes.append(self.__build_match_rune(stats, i))
        url = Lv.get_op_gg_url(region, identity['summonerName'])

        try:
            first_inhibitor = stats['firstInhibitorKill'] or stats['firstInhibitorAssist']
        except KeyError:
            first_inhibitor = False
        try:
            first_blood = stats['firstBloodKill'] or stats['firstBloodAssist']
        except KeyError:
            first_blood = False
        try:
            first_tower = stats['firstTowerKill'] or stats['firstTowerAssist']
        except KeyError:
            first_tower = False

        return LoLMatchDetailed.LoLMatchDetailedPlayerPackage(
            identity['summonerName'], champion, Lv.lane_string_map[timeline['lane']],
            Lv.role_string_map[timeline['role']], self.__get_key_value(player, 'highestAchievedSeasonTier'),
            [spell1, spell2], items, stats['kills'], stats['deaths'], stats['assists'], stats['largestKillingSpree'],
            stats['largestMultiKill'], stats['killingSprees'], stats['doubleKills'], stats['tripleKills'],
            stats['quadraKills'], stats['pentaKills'], stats['unrealKills'], damage_dealt,
            stats['largestCriticalStrike'], damage_to_champs, stats['totalHeal'], stats['damageSelfMitigated'],
            stats['damageDealtToObjectives'], stats['damageDealtToTurrets'], stats['visionScore'],
            stats['timeCCingOthers'], damage_taken, stats['goldEarned'], stats['goldSpent'], stats['turretKills'],
            stats['inhibitorKills'], stats['totalMinionsKilled'], stats['neutralMinionsKilled'],
            self.__get_key_value(stats, 'visionWardsBoughtInGame'), self.__get_key_value(stats, 'wardsPlaced'),
            self.__get_key_value(stats, 'wardsKilled'), first_blood, first_tower, first_inhibitor,
            stats['totalPlayerScore'], runes, url
        )

    @staticmethod
    def __build_match_rune(stats, index):
        rune_style = 'Primary' if index < 4 else 'Sub'
        rune_string = 'perk{}'.format(index)
        rune = Database.select_rune(stats[rune_string], True)
        style = Database.select_rune_style(stats['perk{}Style'.format(rune_style)])['name']
        var_vals = []
        time, percent, sec = True, True, True
        for i, v in enumerate(rune['vars']):
            if v is None:
                continue
            val = ''
            if rune['hasTimeVar'] and time:
                val += '{}:{:02d}'.format(stats['{}Var{}'.format(rune_string, i + 1)],
                                          stats['{}Var{}'.format(rune_string, i + 2)])
                time = False
            elif rune['hasPercentVar'] and percent:
                val += '{}%'.format(stats['{}Var{}'.format(rune_string, i + 1)])
                percent = False
            elif rune['hasSecVar'] and sec:
                val += '{}s'.format(stats['{}Var{}'.format(rune_string, i + 1)])
                sec = False
            elif rune['hasPerfectVar']:
                val += 'Perfect'
            elif time or percent or sec:
                val = '{}'.format(stats['{}Var{}'.format(rune_string, i + 1)])
            var_vals.append([v, val])

        return LoLMatchDetailed.LoLMatchDetailedRunePackage(
            rune['name'], style, var_vals
        )
    # endregion

    # region Match List Builders
    def __build_match_list_match(self, player, match):
        season = Database.select_season(match['seasonId'])['name']
        queue_results = Database.select_queue(match['queueId'], all=True)
        queue = self.__get_queue(queue_results)
        participant_id = self.__get_participant_id(match['participantIdentities'], player['accountId'])
        participant = match['participants'][participant_id - 1]
        timeline = participant['timeline']
        stats = participant['stats']
        champion = Database.select_champion(participant['championId'])['name']
        return LoLMatchList.LoLMatchListMatchPackage(
            match['gameId'], season, queue, Lv.role_string_map[timeline['role']],
            Lv.lane_string_map[timeline['lane']], match['gameDuration'], champion, stats['kills'], stats['deaths'],
            stats['assists'], stats['totalMinionsKilled'] + stats['neutralMinionsKilled'], stats['timeCCingOthers'],
            stats['visionScore'], stats['win'], queue_results['hasLanes']
        )
    # endregion

    # region Player Builders
    @staticmethod
    def __build_player_mastery(mastery):
        champion_name = Database.select_champion(mastery['championId'])['name']
        return LoLPlayer.LoLPlayerMasteriesPackage(
            champion_name, mastery['championLevel'], mastery['championPoints']
        )

    @staticmethod
    def __build_player_rank(rank):
        return LoLPlayer.LoLPlayerRanksPackage(
            Lv.queue_string_map[rank['queueType']], rank['leagueName'], rank['tier'], rank['rank'], rank['wins'],
            rank['losses'], rank['leaguePoints'], rank['freshBlood'], rank['hotStreak'], rank['veteran']
        )

    @staticmethod
    def __build_player_recent_match(team, participant, wins, kills, deaths, assists, vision, cs):
        if team['win'] == 'Win':
            wins += 1
        kills += participant['kills']
        deaths += participant['deaths']
        assists += participant['assists']
        vision += participant['visionScore']
        cs += participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
        return wins, kills, deaths, assists, vision, cs
    # endregion

    # region Timeline Builders
    def __build_timeline_event(self, event, teams, num):
        allowed = ['CHAMPION_KILL', 'BUILDING_KILL', 'ELITE_MONSTER_KILL']
        if event['type'] not in allowed:
            return None
        if event['type'] == allowed[0]:
            return self.__build_timeline_event_champion_kill(
                event, teams, num
            )
        elif event['type'] == allowed[1]:
            return self.__build_timeline_event_building_kill(
                event, teams, num
            )
        else:
            return self.__build_timeline_event_elite_monster_kill(
                event, teams, num
            )

    def __build_timeline_event_champion_kill(self, event, teams, num):
        team = 200 if event['victimId'] <= num // 2 else 100
        allies = teams[0] if team == 100 else teams[1]
        enemies = teams[1] if team == 100 else teams[0]
        if event['killerId'] > 0:
            killer = allies.players[Lv.get_player_index_in_team(event['killerId'], num)][1]
        else:
            killer = 'Team {}'.format(int(team / 100))
        victim = enemies.players[Lv.get_player_index_in_team(event['victimId'], num)][1]
        assists = []
        for a in event['assistingParticipantIds']:
            assists.append(allies.players[Lv.get_player_index_in_team(a, num)][1])
        return LoLMatchTimeline.LoLMatchTimelineEventPackage(
            event['type'], self.__get_time_stamp(event['timestamp']), team, killer, victim, assists
        )

    def __build_timeline_event_building_kill(self, event, teams, num):
        team = 200 if event['teamId'] == 100 else 100
        allies = teams[0] if team == 100 else teams[1]
        if event['killerId'] > 0:
            killer = allies.players[Lv.get_player_index_in_team(event['killerId'], num)][1]
        else:
            killer = 'Team {}'.format(int(team / 100))
        if event['buildingType'] == 'INHIBITOR_BUILDING':
            victim = '{} {}'.format(Lv.event_string_map[event['laneType']], Lv.event_string_map[event['buildingType']])
        elif event['towerType'] == 'NEXUS_TURRET':
            victim = Lv.event_string_map[event['towerType']]
        else:
            victim = '{} {}'.format(Lv.event_string_map[event['laneType']], Lv.event_string_map[event['towerType']])
        assists = []
        for a in event['assistingParticipantIds']:
            assists.append(allies.players[Lv.get_player_index_in_team(a, num)][1])
        return LoLMatchTimeline.LoLMatchTimelineEventPackage(
            event['type'], self.__get_time_stamp(event['timestamp']), team, killer, victim, assists
        )

    def __build_timeline_event_elite_monster_kill(self, event, teams, num):
        team = 100 if event['killerId'] <= num // 2 else 200
        allies = teams[0] if team == 100 else teams[1]
        if event['killerId'] > 0:
            killer = allies.players[Lv.get_player_index_in_team(event['killerId'], num)][1]
        else:
            killer = 'Team {}'.format(int(team / 100))
        if event['monsterType'] == 'DRAGON':
            victim = Lv.event_string_map[event['monsterSubType']]
        else:
            victim = Lv.event_string_map[event['monsterType']]
        return LoLMatchTimeline.LoLMatchTimelineEventPackage(
            event['type'], self.__get_time_stamp(event['timestamp']), team, killer, victim, []
        )

    @staticmethod
    def __build_timeline_team(match, index):
        start = 0 if index == 100 else len(match['participantIdentities']) // 2
        end = start + len(match['participantIdentities']) // 2
        players = []
        for p in match['participantIdentities'][start:end]:
            players.append([p['player']['summonerName'],
                            Database.select_champion(
                                match['participants'][p['participantId'] - 1]['championId'])['name']])
        return LoLMatchTimeline.LoLMatchTimelineTeamPackage(
            index, match['teams'][index // 100 - 1]['win'] == 'Win', players
        )
    # endregion
    # endregion

    # region Get, Parse
    # region Arg Getters
    @staticmethod
    def __get_range(value, min_value, max_value, default_value):
        if value is None:
            return default_value
        if 0 < max_value < int(value):
            return None
        if int(value) < min_value:
            return None
        return int(value)

    def __get_amount(self, amount):
        try:
            return self.__get_range(amount, *Lv.match_list_range, Lv.default_match_list_amount)
        except ValueError:
            return None

    @staticmethod
    def __get_region(region):
        if region is None:
            return Lv.default_region
        if region not in Lv.regions_list:
            if region + Lv.region_optional_suffix not in Lv.regions_list:
                return None
            return region + Lv.region_optional_suffix
        return region
    # endregion

    # region Input Getters
    def __get_detailed_match_list(self, region, account_id, white_list=None):
        matchlist = self.__find_match_list_recent(region, account_id)
        matches_list = []
        for m in matchlist['matches']:
            if white_list is None or m['queue'] in white_list:
                matches_list.append(self.__find_match(region, m['gameId']))
        return matches_list

    @staticmethod
    def __get_elo(elo):
        if elo is None:
            return Lv.elo_string_map[Lv.default_elo]
        elif elo in Lv.elo_string_map:
            return Lv.elo_string_map[elo]
        else:
            return None

    def __get_match_id(self, region, name, index):
        try:
            player = self.__find_player(region, name)
        except requests.HTTPError as e:
            raise e
        if index > 20:
            try:
                matchlist = self.__find_match_list_full(region, player['accountId'])
                if index > matchlist['endIndex']:
                    return None
            except requests.HTTPError:
                return -1
        else:
            try:
                matchlist = self.__find_match_list_recent(region, player['accountId'])
            except requests.HTTPError:
                return -1
        match_id = matchlist['matches'][index - 1]['gameId']
        return match_id

    def __get_match_index(self, index):
        try:
            return self.__get_range(index, *Lv.match_index_range, Lv.default_match_index)
        except ValueError:
            return None

    # region Builder Getters
    @staticmethod
    def __get_key_value(obj, key):
        try:
            return obj[key]
        except KeyError:
            return None

    @staticmethod
    def __get_participant_id(participants, account_id):
        for p in participants:
            if p['player']['accountId'] == account_id:
                return p['participantId']
        return None

    @staticmethod
    def __get_queue(queue_results):
        return '{}: {}{}'.format(queue_results['map'], queue_results['mode'],
                                 '' if queue_results['extra'] is None else ' {}'.format(queue_results['extra']))

    @staticmethod
    def __get_team_id(pid, num):
        return 100 if pid <= num // 2 else 200

    @staticmethod
    def __get_time(time):
        duration = Gv.get_minutes_seconds(time)
        return '{:02d}:{:02d}'.format(duration[0], duration[1])

    @staticmethod
    def __get_time_stamp(time):
        duration = Lv.get_mins_secs_from_time(time)
        return '{:02d}:{:02d}'.format(duration[0], duration[1])
    # endregion

    # region Parsers
    @staticmethod
    def __parse_to_inputs_args(inputs, arg_prefix=Gv.bot_arg_prefix):
        try:
            splits = re.split(' ?{}'.format(arg_prefix), inputs)
            input_splits = re.split(' ? ', splits[0])
            return input_splits, splits[1:]
        except TypeError:
            print('Type Error: {}'.format(inputs))
            return None
        except ValueError:
            print('Value Error: {}'.format(inputs))
            return None

    @staticmethod
    def __parse_arg(args, arg, has_value=False, arg_value_prefix=Gv.bot_arg_value_prefix):
        value = None
        found = False
        for a in args:
            try:
                split = re.split(arg_value_prefix, a)
            except ValueError:
                print('Value Error: {}'.format(a))
                return None
            if split[0] == arg:
                if has_value and len(split) > 1:
                    value = split[1]
                found = True
                break
        return found, value
    # endregion
    # endregion

    # region Display, Print, React
    # region Error Displays
    async def __display_bad_input(self, command):
        return await self.__bot.say('Bad Input.\n**Usage:** ' + self.__command_info_list_map[command][0])

    async def __display_embed(self, content, embed):
        return await self.__bot.say(content=content, embed=embed)

    async def __display_http_error(self, e, **kwargs):
        if e.response.status_code == 403:
            return await self.__bot.say('**Error:** API key expired or forbidden request.'
                                        .format(e.response.status_code))
        elif e.response.status_code == 404:
            return await self.__display_not_found(kwargs['item'], kwargs['location'])
        elif e.response.status_code == 429:
            return await self.__bot.say('**Error:** Rate limit exceeded.'.format(e.response.status_code))
        else:
            return await self.__bot.say('**HTTP Error:** {}.'.format(e.response.status_code))

    async def __display_not_found(self, item, location=None):
        string = '**{}** not found'.format(item)
        if location is not None:
            string += ' in **{}**'.format(location)
        string += '.'
        return await self.__bot.say(string)

    async def __display_not_found_match_list(self, player, region):
        return await self.__bot.say('No matches found for **{}** in **{}**'.format(player, region))

    async def __display_not_found_timeline(self, match, region):
        return await self.__bot.say('No timeline found for **{}** in **{}**'.format(match, region))

    async def __display_not_in_range(self, min_value, max_value):
        if max_value == -1:
            return await self.__bot.say('Value must be at least **{}**.'.format(min_value))
        return await self.__bot.say('Value must be between **{}** and **{}**.'.format(min_value, max_value))
    # endregion

    @staticmethod
    def __print_http_error(e):
        if e.response.status_code == 403:
            print('HTTP Error {}. Is the API Key expired?'.format(e.response.status_code))
        elif e.response.status_code == 404:
            print('HTTP Error {}. Query not found.'.format(e.response.status_code))
        elif e.response.status_code == 429:
            print('HTTP Error {}. Rate limit exceeded.'.format(e.response.status_code))
        else:
            print('HTTP Error {}'.format(e.response.status_code))
    # endregion

    # Misc
    async def __react_to(self, msg, emojis):
        for e in self.__bot.get_all_emojis():
            if e.name in emojis:
                await self.__bot.add_reaction(msg, e)
