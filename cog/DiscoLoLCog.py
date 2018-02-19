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
from manager import CacheManager as Cache, LoLDatabase as Database, LoLFactory as Factory, FileManager as File
# endregion
# region Structures
from structure import DiscoHelp, LoLBuildOrder
# endregion


class DiscoLoLCog:
    __command_info_list_map = {
        'player': ['{}player <player> [{}r{}<region>]'
                   .format(Gv.bot_prefix, Gv.bot_arg_prefix, Gv.bot_arg_value_prefix),
                   'Get information on given player.',
                   ['r - Set the region. Default: {}.'.format(Lv.default_region)]
                   ]
    }

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
            cached = Factory.create_match(region, match)
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
            cached = Factory.create_match_list_recent(region, player, matchlist)
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
            cached = Factory.create_player(region, player, ranks, matchlist, masteries)
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
            cached = Factory.create_timeline(region, match, timeline)
            Cache.add(str_key, cached, Cache.CacheType.STR)

        for e in cached.embed(ctx):
            await self.__bot.say(embed=e)
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
        for p in match['participantIdentities']:
            if p['player']['summonerName'].lower() == name.lower():
                pid = p['participantId']
                pname = p['player']['summonerName']
                sid = p['player']['summonerId']
                platform = p['player']['platformId']
                break

        champion = Database.select_champion(match['participants'][pid - 1]['championId'])['name']
        url = Lv.get_match_history_url(region, platform, match_id, sid)

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

    # endregion

    # region Factory Builders

    # endregion

    # region Get, Parse
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
    def __get_elo(elo):
        if elo is None:
            return Lv.elo_string_map[Lv.default_elo]
        elif elo in Lv.elo_string_map:
            return Lv.elo_string_map[elo]
        else:
            return None

    def __get_detailed_match_list(self, region, account_id, white_list=None):
        matchlist = self.__find_match_list_recent(region, account_id)
        matches_list = []
        for m in matchlist['matches']:
            if white_list is None or m['queue'] in white_list:
                matches_list.append(self.__find_match(region, m['gameId']))
        return matches_list

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

    @staticmethod
    def __get_region(region):
        if region is None:
            return Lv.default_region
        if region not in Lv.regions_list:
            if region + Lv.region_optional_suffix not in Lv.regions_list:
                return None
            return region + Lv.region_optional_suffix
        return region

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

    # region Display, Print
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

    # region Checks, Misc
    async def __react_to(self, msg, emojis):
        for e in self.__bot.get_all_emojis():
            if e.name in emojis:
                await self.__bot.add_reaction(msg, e)
    # endregion
