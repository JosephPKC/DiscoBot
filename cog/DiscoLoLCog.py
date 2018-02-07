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
from structure import LoLPlayer
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
        print(ctx.command)
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
        print(ctx.command)
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
        cached = self.__cache.retrieve((region, name, Gv.CacheKeyType.STR_LOL_PLAYER),
                                       CacheManager.CacheType.STR)
        if cached is None:
            self.__print_cache((region, name, Gv.CacheKeyType.STR_LOL_PLAYER), False)
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
            cached = LoLPlayer.create_lol_player(region, player, ranks)
            self.__cache.add((region, name, Gv.CacheKeyType.STR_LOL_PLAYER),
                             cached, CacheManager.CacheType.STR)
        else:
            self.__print_cache((region, name, Gv.CacheKeyType.STR_LOL_PLAYER), True)
        # Display Storage Structure
        await self.__bot.say('{}{}{}{}.png'.format(Lv.base_url, self.__current_patch,
                                                   Lv.profile_icon_url_part,
                                                   cached.icon))
        for s in cached.to_str():
            await self.__bot.say('```{}```'.format(s))
    # endregion

    # region Retrieval, API Calls
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

    def __find_player(self, region, name):
        if region is None or name is None:
            return None
        cached = self.__cache.retrieve((region, name,
                                        Gv.CacheKeyType.API_LOL_PLAYER),
                                       CacheManager.CacheType.API)
        if cached is None:
            self.__print_cache((region, name, Gv.CacheKeyType.API_LOL_PLAYER), False)
            try:
                player = self.__watcher.summoner.by_name(region, name)
                self.__cache.add((region, name, Gv.CacheKeyType), player, CacheManager.CacheType.API)
                return player
            except requests.HTTPError as e:
                self.__print_http_error(e)
                return None
        else:
            self.__print_cache((region, name, Gv.CacheKeyType.API_LOL_PLAYER), True)
            return cached

    def __find_ranks(self, region, player_id):
        if region is None or player_id is None:
            return None
        cached = self.__cache.retrieve((region, player_id,
                                        Gv.CacheKeyType.API_LOL_RANKS),
                                       CacheManager.CacheType.API)
        if cached is None:
            self.__print_cache((region, player_id, Gv.CacheKeyType.API_LOL_RANKS), False)
            try:
                ranks = self.__watcher.league.positions_by_summoner(region, player_id)
                self.__cache.add((region, player_id, Gv.CacheKeyType.API_LOL_RANKS),
                                 ranks, CacheManager.CacheType.API)
                return ranks
            except requests.HTTPError as e:
                self.__print_http_error(e)
                return None
        else:
            self.__print_cache((region, player_id, Gv.CacheKeyType.API_LOL_RANKS), True)
            return cached
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

    def __get_latest_patch(self):
        self.__file.download_file(Gv.FileType.JSON, Lv.version_file, Lv.version_url)
        with open(Lv.version_path, 'r', encoding='utf-8') as file:
            json_file = json.loads(file.read())
        return json_file[0]

    async def __display_not_yet_implemented(self, command_name):
        await self.__bot.say('{} has not yet been implemented. <:dab:390040479951093771>'.format(command_name))

    @staticmethod
    def __get_command_usage(command, prefix=Gv.argument_prefix, value_prefix=Gv.argument_value_prefix):
        if command == 'player':
            return 'player *name* [{}r{}*region*]'.format(prefix, value_prefix)
        else:
            return ''

    @staticmethod
    def __print_cache(key, found):
        print('{}: {}.'.format('FOUND' if found else 'NOT FOUND', key))

    @staticmethod
    def __print_http_error(e):
        if e.response.status_code == 403:
            print('HTTP Error {}. Is the API Key expired?'.format(e.response.status_code))
        elif e.response.status_code == 404:
            print('HTTP Error {}. Query not found.'.format(e.response.status_code))
        else:
            print('HTTP Error {}'.format(e.response.status_code))
