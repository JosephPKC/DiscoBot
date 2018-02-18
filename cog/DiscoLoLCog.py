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
from value import GeneralValues as Gv, LeagueValues as Lv
from manager import CacheManager as Cache, LoLDatabase as Database, LoLDataDragon as Datadragon, \
     LoLFactory as Factory, FileManager as File, EmojiRepository as Repo
from structure import DiscoHelp


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
        py_gg.init(ch_gg_key)

    # region Commands
    @commands.group(name='lol', pass_context=True)
    async def __group_lol(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.__bot.say('Invalid Command: {}. <:dab:390040479951093771>'.format(ctx.subcommand_passed))

    # Riot API Commands
    @__group_lol.command(name='help', pass_context=True, aliases=['?'])
    async def __cmd_help(self, ctx, cmd_input: str=None):
        Gv.print_command(ctx.command, cmd_input)
        msg = await self.__display_embed('{}'.format(ctx.message.author.mention), self.__help.embed(ctx))
        await self.__react_to(msg, ['hellyeah', 'dorawinifred', 'cutegroot', 'dab'])

    @__group_lol.command(name='match', pass_context=True)
    async def __cmd_match(self, ctx, *, cmd_input: str=None):
        Gv.print_command(ctx.command, cmd_input)
        # Parse into Inputs and Args
        inputs = self.__parse_to_inputs_args(cmd_input)
        if inputs is None or len(inputs[0]) < 1 or inputs[0][0] == '':
            await self.__display_bad_input('match')
            return
        # Get inputs
        if len(inputs[0]) == 1:
            name = None
            index = None
            mid = inputs[0][0]
        else:
            name = inputs[0][0]
            index = self.__get_match_index(inputs[0][1])
            if index is None:
                await self.__display_not_in_range(*Lv.match_index_range)
                return
            mid = None
        args = inputs[1]
        # Get arguments
        _, region = self.__parse_arg(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__display_not_found(region)
            return
        region = region_temp
        use_rune, _ = self.__parse_arg(args, 'ru', True)
        use_detail, _ = self.__parse_arg(args, 'd', True)
        # Get mid
        if mid is None:
            try:
                mid = self.__get_match_id(region, name, index)
            except requests.HTTPError as e:
                self.__print_http_error(e)
                await self.__display_http_error(e, item=name, location=region)
                return
            if mid is None:
                await self.__bot.say('**{}** is too large of an index.')
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
        inputs = self.__parse_to_inputs_args(cmd_input)
        if inputs is None or len(inputs[0]) < 1 or inputs[0][0] == '':
            await self.__display_bad_input('matchlist')
            return
        # Get inputs
        name = inputs[0][0]
        args = inputs[1]
        # Get arguments
        _, region = self.__parse_arg(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__display_not_found(region)
            return
        region = region_temp
        _, amount = self.__parse_arg(args, 'a', True)
        amount = self.__get_amount(amount)
        if amount is None:
            await self.__display_not_in_range(*Lv.match_list_range)

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
                await self.__display_http_error(e)
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
        inputs = self.__parse_to_inputs_args(cmd_input)
        if inputs is None or len(inputs[0]) < 1 or inputs[0][0] == '':
            await self.__display_bad_input('player')
            return
        # Get inputs
        name = inputs[0][0]
        args = inputs[1]
        # Get arguments
        _, region = self.__parse_arg(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__display_not_found(region)
            return
        region = region_temp

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
                matchlist = self.__get_detailed_match_list(region, player['accountId'], Lv.queues_standard_list)
                masteries = self.__find_masteries(region, player['id'])
            except requests.HTTPError as e:
                self.__print_http_error(e)
                await self.__display_http_error(e)
                return
            # Create and Cache
            cached = Factory.create_player(region, player, ranks, matchlist, masteries)
            Cache.add(str_key, cached, Cache.CacheType.STR)

        await self.__bot.say(content='{}'.format(ctx.message.author.mention), embed=cached.embed(ctx))
    # endregion

    # region API Retrieval
    @staticmethod
    def __find_api(params, key_type, func):
        for p in params:
            if p is None:
                return None
        key_type = (*params, key_type)
        cached = Cache.retrieve(key_type, Cache.CacheType.API)
        if cached is None:
            try:
                new_data = func(*params)
                Cache.add(key_type, new_data, Cache.CacheType.API)
                return new_data
            except requests.HTTPError as e:
                raise e
        return cached

    def __find_masteries(self, region, player_id):
        return self.__find_api(
            params=[region, player_id],
            key_type=Cache.ApiKey.LoL.MASTERY,
            func=lambda r, pid: self.__watcher.champion_mastery.by_summoner(r, pid)
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
    # endregion

    # region Parse, Get
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
            matchlist = self.__find_match_list_full(region, player['accountId'])
            if index > matchlist['endIndex']:
                return None
        else:
            matchlist = self.__find_match_list_recent(region, player['accountId'])
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

    async def __display_not_in_range(self, min_value, max_value):
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

    # region Factories
    def __create_help(self):
        commands = []
        for c, i in self.__command_info_list_map.items():
            commands.append(DiscoHelp.DiscoHelpCommandPackage(
                c, i[0], i[1], i[2]
            ))

        return DiscoHelp.DiscoHelp(
            'LoL', commands
        )
    # endregion
