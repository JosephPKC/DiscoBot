# region Imports
import re
import requests
import string
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
from manager import CacheManager, DatabaseManager, FileManager, DataDragonManager
from structure import LoLPlayer, LoLMatchList, LoLMatchDetailed, \
    LoLMatchTimeline, LoLMasteries, LoLTotalMastery, LoLBestPlayers, \
    LoLStatus, LoLMatchSpectator, LoLChampion
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
        self.__data_dragon = DataDragonManager.DataDragonManager(self.__file, self.__cache)

    # region Commands

    # Commands that use Riotwatcher and Riot's API
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
        # Display Storage Structure
        await self.__bot.say('{}{}{}{}.png'.format(Lv.base_url,
                                                   self.__data_dragon.get_current_patch(),
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
        amount = await self.__get_amount(amount, Lv.default_recent_matches_amount,
                                         Lv.range_recent_matches[0],
                                         Lv.range_recent_matches[1])

        # Check Cache
        str_key = (region, name, Gv.CacheKeyType.STR_LOL_MATCH_LIST)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
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
            index = await self.__get_index(inputs[1])
            if index is None:
                await self.__bot.say('Second parameter must be a number.')
                return
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
        # Get match ID
        if index is not None:
            match_id = await self.__find_match_id(region, name, index)

        # Check Cache
        str_key = (region, match_id, Gv.CacheKeyType.STR_LOL_MATCH_DETAILED)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data Objects via API

            match = self.__find_match(region, match_id)
            if match is None:
                await self.__bot.say('Match **{}** not found in region **{}**.'.format(match_id, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_match_detailed(region, match)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        # Display Storage Structure
        for s in cached.to_str(use_rune, use_detail, use_timeline):
            await self.__bot.say('```{}```'.format(s))

    @lol.command(name='timeline', aliases=[],
                 pass_context=True, help='Get match timeline.')
    async def timeline(self, ctx, *, cmd_input: str=None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('timeline'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('timeline'))
            return
        # Can be one input or two
        if len(inputs) < 2:
            match_id = inputs[0]
            name = None
            index = None
        else:
            match_id = None
            name = inputs[0]
            index = await self.__get_index(inputs[1])
            if index is None:
                await self.__bot.say('Second parameter must be a number.')
                return
        # Get and Check Region
        _, region, _ = self.__parse_args(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__bot.say('Region **{}** not found.'.format(region))
            return
        region = region_temp
        # Get match id
        if index is not None:
            match_id = await self.__find_match_id(region, name, index)

        # Check Cache
        str_key = (region, match_id, Gv.CacheKeyType.STR_LOL_MATCH_TIMELINE)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data Objects via API

            timeline = self.__find_match_timeline(region, match_id)
            if timeline is None:
                await self.__bot.say('Match **{}** not found in region **{}**.'.format(match_id, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_match_timeline(region, match_id, timeline)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        # Display Storage Structure
        for s in cached.to_str():
            await self.__bot.say('```{}```'.format(s))

    @lol.command(name='masteries', aliases=[],
                 pass_context=True, help='Get champion masteries.')
    async def masteries(self, ctx, *, cmd_input: str = None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('masteries'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('masteries'))
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
        _, amount, others = self.__parse_args(others, 'a', True)
        amount = await self.__get_amount(amount, Lv.default_recent_matches_amount,
                                         Lv.range_masteries[0],
                                         Lv.range_masteries[1])

        # Check Desc.
        use_asc, _, _ = self.__parse_args(others, 'asc')

        # Check Cache
        str_key = (region, name, Gv.CacheKeyType.STR_LOL_MASTERY)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data via API
            player = self.__find_player(region, name)
            if player is None:
                await self.__bot.say('Player **{}** not found in region **{}**.'.format(name, region))
                return
            masteries = self.__find_masteries(region, player['id'])
            if masteries is None:
                await self.__bot.say('Player **{}** not found in region **{}**.'.format(name, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_masteries(region, masteries, player)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        # Display Storage Structure
        for s in cached.to_str(amount, use_asc):
            await self.__bot.say('```{}```'.format(s))

    @lol.command(name='mastery', aliases=[],
                 pass_context=True, help='Get champion mastery.')
    async def mastery(self, ctx, *, cmd_input: str = None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('mastery'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) < 2 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('mastery'))
            return
        name = inputs[0]
        champion = inputs[1]
        # Get and Check Region
        _, region, _ = self.__parse_args(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__bot.say('Region **{}** not found.'.format(region))
            return
        region = region_temp

        # Check Cache
        str_key = (region, name, champion, Gv.CacheKeyType.STR_LOL_MASTERY)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data via API
            player = self.__find_player(region, name)
            if player is None:
                await self.__bot.say('Player **{}** not found in region **{}**.'.format(name, region))
                return
            champion_id = self.__database.select_lol_champion_inverted(champion)
            if champion_id is None:
                await self.__bot.say('Champion **{}** does not exist.'.format(champion))
                return
            mastery = self.__find_mastery(region, player['id'], champion_id)
            if mastery is None:
                await self.__bot.say('Player **{}** not found in region **{}**.'.format(name, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_masteries_mastery(mastery)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        # Display Storage Structure
        for s in cached.to_str():
            await self.__bot.say('```{}```'.format(s))

    @lol.command(name='totalmastery', aliases=[],
                 pass_context=True, help='Get total mastery.')
    async def totalmastery(self, ctx, *, cmd_input: str = None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('totalmastery'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('totalmastery'))
            return
        name = inputs[0]
        # Get and Check Region
        _, region, _ = self.__parse_args(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__bot.say('Region **{}** not found.'.format(region))
            return
        region = region_temp

        # Check Cache
        str_key = (region, name, Gv.CacheKeyType.STR_LOL_TOTAL_MASTERY)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data via API
            player = self.__find_player(region, name)
            if player is None:
                await self.__bot.say('Player **{}** not found in region **{}**.'.format(name, region))
                return
            total_mastery = self.__find_total_mastery(region, player['id'])
            if total_mastery is None:
                await self.__bot.say('Player **{}** not found in region **{}**.'.format(name, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_total_mastery(region, total_mastery, player)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        # Display Storage Structure
        for s in cached.to_str():
            await self.__bot.say('```{}```'.format(s))

    @lol.command(name='challengers', aliases=[],
                 pass_context=True, help='Get all challengers.')
    async def challengers(self, ctx, *, cmd_input: str = None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('challengers'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('challengers'))
            return
        queue = inputs[0]
        try:
            queue_id = Lv.queues_string_map_inverted[queue.lower()]
        except KeyError:
            await self.__bot.say('**{}** is invalid. Use either solo, solosr, flexsr, or flextt.'.format(queue))
            return
        # Get and Check Region
        _, region, others = self.__parse_args(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__bot.say('Region **{}** not found.'.format(region))
            return
        region = region_temp
        # Get and Check Amount
        _, amount, _ = self.__parse_args(others, 'a', True)
        amount = await self.__get_amount(amount, Lv.default_best_players_amount,
                                         Lv.range_best_players[0],
                                         Lv.range_best_players[1])

        # Check Cache
        str_key = (region, queue_id, Gv.CacheKeyType.STR_LOL_CHALLENGERS)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data via API
            challengers = self.__find_challengers(region, queue_id)
            if challengers is None:
                await self.__bot.say(
                    'Something went wrong fetching **{}** challengers in Region **{}**'
                    .format(queue, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_best_players(region, queue_id, challengers)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        # Display Storage Structure
        for s in cached.to_str(amount):
            await self.__bot.say('```{}```'.format(s))

    @lol.command(name='masters', aliases=[],
                 pass_context=True, help='Get all masters.')
    async def masters(self, ctx, *, cmd_input: str = None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('masters'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('masters'))
            return
        queue = inputs[0]
        try:
            queue_id = Lv.queues_string_map_inverted[queue.lower()]
        except KeyError:
            await self.__bot.say('**{}** is invalid. Use either solo, solosr, flexsr, or flextt.'.format(queue))
            return
        # Get and Check Region
        _, region, others = self.__parse_args(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__bot.say('Region **{}** not found.'.format(region))
            return
        region = region_temp
        # Get and Check Amount
        _, amount, _ = self.__parse_args(others, 'a', True)
        amount = await self.__get_amount(amount, Lv.default_best_players_amount,
                                         Lv.range_best_players[0],
                                         Lv.range_best_players[1])

        # Check Cache
        str_key = (region, queue_id, Gv.CacheKeyType.STR_LOL_MASTERS)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data via API
            masters = self.__find_masters(region, queue_id)
            if masters is None:
                await self.__bot.say(
                    'Something went wrong fetching **{}** challengers in Region **{}**'.format(queue, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_best_players(region, queue_id, masters)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        # Display Storage Structure
        for s in cached.to_str(amount):
            await self.__bot.say('```{}```'.format(s))

    @lol.command(name='status', aliases=[],
                 pass_context=True, help='Get server status.')
    async def status(self, ctx, *, cmd_input: str = None):
        print('Command: {}'.format(ctx.command))
        # Parse into Inputs and Args
        _, args = self.__parse_inputs_and_args(cmd_input)
        # Get and Check Region
        _, region, others = self.__parse_args(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__bot.say('Region **{}** not found.'.format(region))
            return
        region = region_temp

        # Check Cache
        str_key = (region, Gv.CacheKeyType.STR_LOL_STATUS)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data via API
            status = self.__find_status(region)
            if status is None:
                await self.__bot.say('Region **{}** does not exist.'.format(region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_status(region, status)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        # Display Storage Structure
        for s in cached.to_str():
            await self.__bot.say('```{}```'.format(s))

    @lol.command(name='spectate', aliases=[],
                 pass_context=True, help='Get specate info.')
    async def spectate(self, ctx, *, cmd_input: str = None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('spectate'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('spectate'))
            return
        name = inputs[0]
        # Get and Check Region
        _, region, others = self.__parse_args(args, 'r', True)
        region_temp = self.__get_region(region)
        if region_temp is None:
            await self.__bot.say('Region **{}** not found.'.format(region))
            return
        region = region_temp

        # Check Cache
        str_key = (region, Gv.CacheKeyType.STR_LOL_SPECTATE)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data via API
            player = self.__find_player(region, name)
            if player is None:
                await self.__bot.say('Player **{}** not found in region **{}**.'
                                     .format(name, region))
                return
            spectate = self.__find_spectate(region, player['id'])
            if spectate is None:
                await self.__bot.say('Player **{}** in region **{}** is not in a valid game.'
                                     .format(name, region))
                return
            # Create and Cache Storage Structure
            cached = self.__create_spectate(region, spectate)
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        # Display Storage Structure
        await self.__bot.say('```Download and run this .bat file to spectate.```')
        file = self.__create_spectate_bat(region, cached.encryption_key, cached.match_id)
        await self.__bot.send_file(ctx.message.channel, file)
        for s in cached.to_str():
            await self.__bot.say('```{}```'.format(s))

    # Commands that use Data Dragon URLs
    @lol.command(name='champion', aliases=[],
                 pass_context=True, help='Get champion info.')
    async def champion(self, ctx, *, cmd_input: str = None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('champion'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('champion'))
            return
        name = inputs[0]
        # Get and Check Flags
        use_lore, _, others = self.__parse_args(args, 'l', True)
        use_tips, _, others = self.__parse_args(args, 't', True)
        use_art, _, _ = self.__parse_args(args, 'a', True)

        # Check Cache
        str_key = (name, Gv.CacheKeyType.STR_LOL_CHAMPION)
        str_arts_key = (name, Gv.CacheKeyType.STR_LOL_CHAMPION_ART)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        arts = self.__cache.retrieve(str_arts_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data via API
            json_name = self.__database.select_lol_champion_json_inverted(name)
            if json_name is None:
                await self.__bot.say('**{}** does not exist.'.format(name))
                return
            champion = self.__data_dragon.get_champion(json_name)
            if champion is None:
                await self.__bot.say('**{}** does not exist.'.format(name))
                return
            # Create and Cache Storage Structure
            cached = self.__create_champion(champion[0])
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
            if arts is None:
                arts = champion[1]
                self.__cache.add(str_arts_key, arts, CacheManager.CacheType.STR)
        # Display Storage Structure
        for s in cached.to_str(use_lore, use_tips):
            await self.__bot.say('```{}```'.format(s))
        await self.__bot.say('Official: {}\n'
                             .format( cached.official_url))
        if use_art:
            for a in arts:
                title = a[0]
                if title == 'default':
                    title = 'Default'
                await self.__bot.say('{}\n{}\n'.format(title, a[1]))

    @lol.command(name='skins', aliases=[],
                 pass_context=True, help='Get champion skin arts.')
    async def skins(self, ctx, *, cmd_input: str = None):
        print('Command: {}'.format(ctx.command))
        if cmd_input is None:
            await self.__bot.say(self.__get_command_usage('skins'))
            return
        # Parse into Inputs and Args
        inputs, args = self.__parse_inputs_and_args(cmd_input)
        if len(inputs) == 0 or inputs[0] == '':
            await self.__bot.say(self.__get_command_usage('skins'))
            return
        name = inputs[0]

        # Check Cache
        str_key = (name, Gv.CacheKeyType.STR_LOL_CHAMPION_ART)
        cached = self.__cache.retrieve(str_key, CacheManager.CacheType.STR)
        if cached is None:
            # Get Data via API
            json_name = self.__database.select_lol_champion_json_inverted(name)
            if json_name is None:
                await self.__bot.say('**{}** does not exist.'.format(name))
                return
            champion = self.__data_dragon.get_champion(json_name)
            if champion is None:
                await self.__bot.say('**{}** does not exist.'.format(name))
                return
            # Create and Cache Storage Structure
            cached = champion[1]
            self.__cache.add(str_key, cached, CacheManager.CacheType.STR)
        # Display Storage Structure
        for a in cached:
            title = a[0]
            if title == 'default':
                title = 'Default'
            await self.__bot.say('{}\n{}\n'.format(title, a[1]))
    # endregion

    # region Command Helpers
    async def __get_amount(self, amount, default_value, min_value, max_value=-1):
        error_string = 'Amount should be between {} and {}.'\
            .format(min_value, max_value) \
            if max_value > -1 \
            else 'Amount should be at least {}.'\
            .format(min_value)
        if amount is None:
            return default_value
        elif 0 < max_value < int(amount):
            await self.__bot.say(error_string)
            return max_value
        elif int(amount) < min_value:
            await self.__bot.say(error_string)
            return min_value
        else:
            return int(amount)

    async def __get_index(self, index):
        try:
            index = int(index)
            return await self.__get_amount(index, Lv.default_match_index,
                                           Lv.range_match_index[0],
                                           Lv.range_match_index[1])
        except ValueError:
            return None

    async def __find_match_id(self, region, name, index):
        player = self.__find_player(region, name)
        if player is None:
            self.__bot.say('Player **{}** not found in region **{}**.'.format(name, region))
            return
        if index > 20:
            matchlist = self.__find_match_list_full(region, player['accountId'])
            if index > matchlist['endIndex']:
                await self.__bot.say('Match **{}** not found for player **{}** in'
                                     ' region **{}**.'
                                     .format(index, player, region))
                return
        else:
            matchlist = self.__find_match_list(region, player['accountId'])
        if matchlist is None:
            await self.__bot.say(
                'Recent matches not found for player **{}** in region **{}**.'.format(name, region))
            return
        match_id = matchlist['matches'][index - 1]['gameId']
        return match_id

    @staticmethod
    def __create_spectate_bat(region, encryption_key, match_id):
        name = 'spectate_{}.bat'.format(match_id)
        with open('data/spectate/{}'.format(name), 'w')as file:
            file.write(
                '@cd /d \"C:\\Riot Games\\League of Legends\\'
                'RADS\\solutions\\lol_game_client_sln\\releases\\'
                '0.0.1.202\\deploy\"\n'
                '\tif exist \"League of Legends.exe\" (\n'
                '\t\t@start \"\" \"League of Legends.exe\" \"8394\" \"LoLLauncher.exe\" \"\"'
                ' \"spectator spectator.{}.lol.riotgames.com:80'
                ' {} {} {}" "-UseRads\"\n'
                '\t\tgoto :eof\n\t)\n'.format(Lv.regions_spectate_string_map[region],
                                              encryption_key, match_id, region.upper())
            )
        return 'data/spectate/' + name
    # endregion

    # region Retrieval, API Calls
    def __find_api(self, params, api_key, api_function):
        for p in params:
            if p is None:
                return None
        cached = self.__cache.retrieve(api_key, CacheManager.CacheType.API)
        if cached is None:
            try:
                new_data = api_function()
                self.__cache.add(api_key, new_data, CacheManager.CacheType.API)
                return new_data
            except requests.HTTPError as e:
                self.__print_http_error(e)
                return None
        return cached

    def __find_player(self, region, name):
        params = [region, name]
        api_key = (region, name, Gv.CacheKeyType.API_LOL_PLAYER)

        def api_function(): return self.__watcher.summoner.by_name(region, name)
        return self.__find_api(params, api_key, api_function)

    def __find_ranks(self, region, player_id):
        params = [region, player_id]
        api_key = (region, player_id, Gv.CacheKeyType.API_LOL_RANKS)

        def api_function(): return self.__watcher.league.positions_by_summoner(
            region, player_id)
        return self.__find_api(params, api_key, api_function)

    def __find_match_list(self, region, account_id):
        params = [region, account_id]
        api_key = (region, account_id, Gv.CacheKeyType.API_LOL_MATCH_LIST)

        def api_function(): return self.__watcher.match.matchlist_by_account_recent(
            region, account_id)
        return self.__find_api(params, api_key, api_function)

    def __find_match_list_full(self, region, account_id):
        params = [region, account_id]
        api_key = (region, account_id, Gv.CacheKeyType.API_LOL_MATCH_LIST_FULL)

        def api_function(): return self.__watcher.match.matchlist_by_account(
            region, account_id)
        return self.__find_api(params, api_key, api_function)

    def __find_match(self, region, match_id):
        params = [region, match_id]
        api_key = (region, match_id, Gv.CacheKeyType.API_LOL_MATCH)

        def api_function(): return self.__watcher.match.by_id(region, match_id)
        return self.__find_api(params, api_key, api_function)

    def __find_match_timeline(self, region, match_id):
        if region is None or match_id is None:
            return None
        api_key = (region, match_id, Gv.CacheKeyType.API_LOL_MATCH_TIMELINE)
        cached = self.__cache.retrieve(api_key, CacheManager.CacheType.API)
        if cached is None:
            Gv.print_cache(api_key, False)
            try:
                match = self.__watcher.match.timeline_by_match(region, match_id)
                self.__cache.add(api_key, match, CacheManager.CacheType.API)
                return match
            except requests.HTTPError as e:
                self.__print_http_error(e)
                return None
        else:
            Gv.print_cache(api_key, True)
            return cached

    def __find_masteries(self, region, player_id):
        params = [region, player_id]
        api_key = (region, player_id, Gv.CacheKeyType.API_LOL)

        def api_function(): return self.__watcher.champion_mastery.by_summoner(
            region, player_id)
        return self.__find_api(params, api_key, api_function)

    def __find_mastery(self, region, player_id, champion_id):
        params = [region, player_id, champion_id]
        api_key = (region, player_id, champion_id,
                   Gv.CacheKeyType.API_LOL_MASTERY)

        def api_function(): return self.__watcher.champion_mastery.by_summoner_by_champion(
            region, player_id, champion_id)
        return self.__find_api(params, api_key, api_function)

    def __find_total_mastery(self, region, player_id):
        params = [region, player_id]
        api_key = (region, player_id, Gv.CacheKeyType.API_LOL_TOTAL_MASTERY)

        def api_function(): return self.__watcher.champion_mastery.scores_by_summoner(
            region, player_id)
        return self.__find_api(params, api_key, api_function)

    def __find_challengers(self, region, queue_id):
        params = [region, queue_id]
        api_key = (region, queue_id, Gv.CacheKeyType.API_LOL_CHALLENGERS)

        def api_function(): return self.__watcher.league.challenger_by_queue(
            region, queue_id)
        return self.__find_api(params, api_key, api_function)

    def __find_masters(self, region, queue_id):
        params = [region, queue_id]
        api_key = (region, queue_id, Gv.CacheKeyType.API_LOL_MASTERS)

        def api_function(): return self.__watcher.league.masters_by_queue(region, queue_id)
        return self.__find_api(params, api_key, api_function)

    def __find_status(self, region):
        params = [region]
        api_key = (region, Gv.CacheKeyType.API_LOL_MASTERS)

        def api_function(): return self.__watcher.lol_status.shard_data(region)
        return self.__find_api(params, api_key, api_function)

    def __find_spectate(self, region, player_id):
        params = [region, player_id]
        api_key = (region, player_id, Gv.CacheKeyType.API_LOL_SPECTATE)

        def api_function(): return self.__watcher.spectator.by_summoner(region, player_id)
        return self.__find_api(params, api_key, api_function)
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
            matches.append(self.__create_match_list_match(region, player, match, m))
        return LoLMatchList.LoLMatchList(region, player['name'], player['id'], player['accountId'], matches)

    def __create_match_list_match(self, region, player, match, match_details):
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
                                     match['gameDuration'],
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

        # timelines = []
        # times = ['0-10', '10-20', '20-30', '30-end']
        # headers = ['creepsPerMinDeltas', 'csDiffPerMinDeltas', 'xpPerMinDeltas',
        #            'xpDiffPerMinDeltas', 'goldPerMinDeltas', 'damageTakenPerMinDeltas',
        #            'damageTakenDiffPerMinDeltas']
        # for h in headers:
        #     data = timeline[h]
        #     timeline_single = []
        #     for t in times[:len(data)]:
        #         timeline_single.append([t, data[t]])
        #     timelines.append(LoLMatchDetailed.LoLMatchDetailedTimelinePackage(timeline_single))

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
            [queue_results['hasScore'], stats['totalPlayerScore']],
            queue_results['hasLanes']
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

    def __create_match_timeline(self, region, match_id, timeline):
        match = self.__find_match(region, match_id)
        teams = self.__create_match_timeline_team(timeline, match)
        num_of_players = len(timeline['frames'][0]['participantFrames'])
        events = []
        for f in timeline['frames']:
            for e in f['events']:
                event = self.__create_match_timeline_event(e, teams, num_of_players)
                if event is not None:
                    events.append(event)

        return LoLMatchTimeline.LoLMatchTimeline(
            region, match_id, teams, events
        )

    def __create_match_timeline_team(self, timeline, match):
        players_per_team = len(timeline['frames'][0]['participantFrames']) // 2
        players = []
        for p in match['participantIdentities']:
            champion_id = match['participants'][p['participantId'] - 1]['championId']
            champion_results = self.__database.select_lol_champion(champion_id)
            players.append([p['player']['summonerName'], champion_results])

        return [
            LoLMatchTimeline.LoLMatchTimelineTeam(
                100, match['teams'][0]['win'] == 'Win', players[:players_per_team]
            ),
            LoLMatchTimeline.LoLMatchTimelineTeam(
                200, match['teams'][1]['win'] == 'Win', players[players_per_team:]
            )
        ]

    def __create_match_timeline_event(self, event, teams_pair, num_of_players):
        allowed_types = ['CHAMPION_KILL', 'BUILDING_KILL', 'ELITE_MONSTER_KILL']
        if event['type'] not in allowed_types:
            return None
        if event['type'] == allowed_types[0]:
            return self.__create_match_timeline_event_champion_kill(
                event, teams_pair, num_of_players
            )
        elif event['type'] == allowed_types[1]:
            return self.__create_match_timeline_event_building_kill(
                event, teams_pair, num_of_players
            )
        else:
            return self.__create_match_timeline_event_elite_monster_kill(
                event, teams_pair, num_of_players
            )

    @staticmethod
    def __create_match_timeline_event_champion_kill(event, teams_pair, num_of_players):
        team = 200 if event['victimId'] <= num_of_players // 2 else 100
        if team == 100:
            allies = teams_pair[0]
            enemies = teams_pair[1]
        else:
            allies = teams_pair[1]
            enemies = teams_pair[0]
        if event['killerId'] > 0:
            killer = allies.player_pair_list[Lv.player_to_in_team(event['killerId'],
                                                                  num_of_players)][1]
        else:
            killer = 'Team {}'.format(int(team / 100))
        victim = enemies.player_pair_list[Lv.player_to_in_team(event['victimId'],
                                                               num_of_players)][1]

        assists = []
        for a in event['assistingParticipantIds']:
            assists.append(allies.player_pair_list[
                               Lv.player_to_in_team(a, num_of_players)][1])
        return LoLMatchTimeline.LoLMatchTimelineEvent(
            event['type'], event['timestamp'], None, killer, victim, assists, team
        )

    @staticmethod
    def __create_match_timeline_event_building_kill(event, teams_pair, num_of_players):
        team = 200 if event['teamId'] == 100 else 100
        if team == 100:
            allies = teams_pair[0]
        else:
            allies = teams_pair[1]
        if event['killerId'] > 0:
            killer = allies.player_pair_list[Lv.player_to_in_team(event['killerId'],
                                                                  num_of_players)][1]
        else:
            killer = 'Team {}'.format(int(team / 100))

        if event['buildingType'] == 'INHIBITOR_BUILDING':
            description = '{} {}'.format(Lv.events_string_map[event['laneType']],
                                         Lv.events_string_map[event['buildingType']])
        elif event['towerType'] == 'NEXUS_TURRET':
            description = Lv.events_string_map[event['towerType']]
        else:
            description = '{} {}'.format(Lv.events_string_map[event['laneType']],
                                         Lv.events_string_map[event['towerType']])

        assists = []
        for a in event['assistingParticipantIds']:
            assists.append(allies.player_pair_list[
                               Lv.player_to_in_team(a, num_of_players)][1])
        return LoLMatchTimeline.LoLMatchTimelineEvent(
            event['type'], event['timestamp'], description, killer, None, assists, team
        )

    @staticmethod
    def __create_match_timeline_event_elite_monster_kill(event, teams_pair, num_of_players):
        team = 100 if event['killerId'] <= num_of_players // 2 else 200
        if team == 100:
            allies = teams_pair[0]
        else:
            allies = teams_pair[1]
        if event['killerId'] > 0:
            killer = allies.player_pair_list[Lv.player_to_in_team(event['killerId'],
                                                                  num_of_players)][1]
        else:
            killer = 'Team {}'.format(int(team / 100))

        if event['monsterType'] == 'DRAGON':
            description = Lv.events_string_map[event['monsterSubType']]
        else:
            description = Lv.events_string_map[event['monsterType']]

        return LoLMatchTimeline.LoLMatchTimelineEvent(
            event['type'], event['timestamp'], description, killer, None, [], team
        )

    def __create_masteries(self, region, masteries, player):
        mastery_list = []
        for m in masteries:
            mastery = self.__create_masteries_mastery(m)
            mastery_list.append(mastery)

        return LoLMasteries.LoLMasteries(
            region, player['name'], player['id'], mastery_list
        )

    def __create_masteries_mastery(self, mastery_info):
        champion_results = self.__database.select_lol_champion(mastery_info['championId'])
        return LoLMasteries.LoLMasteriesMastery(
            [mastery_info['championId'], champion_results],
            mastery_info['championLevel'], mastery_info['championPoints'],
            mastery_info['championPointsSinceLastLevel'],
            mastery_info['championPointsUntilNextLevel'],
            mastery_info['chestGranted'], mastery_info['tokensEarned']
        )

    @staticmethod
    def __create_total_mastery(region, total_mastery, player):
        return LoLTotalMastery.LoLTotalMastery(
            region, player['name'], player['id'], total_mastery
        )

    def __create_best_players(self, region, queue_id, best_players):
        players = []
        for p in best_players['entries']:
            players.append(self.__create_best_players_player(p))
        players = sorted(players, key=lambda x: -x.lp)
        return LoLBestPlayers.LoLBestPlayers(
            region, best_players['tier'], queue_id, best_players['name'], players
        )

    @staticmethod
    def __create_best_players_player(entry):
        return LoLBestPlayers.LoLBestPlayersPlayer(
            entry['playerOrTeamId'], entry['playerOrTeamName'],
            entry['leaguePoints'], entry['rank'], entry['wins'], entry['losses'],
            entry['veteran'], entry['inactive'], entry['freshBlood'], entry['hotStreak']
        )

    @staticmethod
    def __create_status(region, status):
        services = []
        for s in status['services']:
            incidents = []
            for i in s['incidents']:
                for u in i['updates']:
                    incidents.append(LoLStatus.LoLStatusServiceIncident(
                        u['content']
                    ))
            services.append(LoLStatus.LoLStatusService(
                s['name'], s['status'], incidents
            ))
        return LoLStatus.LoLStatus(
            region, status['name'], services
        )

    def __create_spectate(self, region, spectate):
        queue_results = self.__database.select_lol_queue(spectate['gameQueueConfigId'])
        queue = '{}: {}{}'.format(queue_results['map'],
                                  queue_results['mode'],
                                  '' if queue_results['extra'] is None
                                  else ' {}'.format(queue_results['extra']))

        team1 = self.__create_spectate_team(spectate, 100)
        team2 = self.__create_spectate_team(spectate, 200)

        return LoLMatchSpectator.LoLMatchSpectator(
            region, spectate['gameId'], queue, spectate['observers']['encryptionKey'],
            spectate['gameLength'], [team1, team2]
        )

    def __create_spectate_team(self, spectate, team_id):
        size = len(spectate['participants'])
        if team_id == 100:
            participants = spectate['participants'][:size // 2]
        else:
            participants = spectate['participants'][size // 2:]

        players = []
        for p in participants:
            spell1 = self.__database.select_lol_summoner_spell(p['spell1Id'])
            spell2 = self.__database.select_lol_summoner_spell(p['spell2Id'])
            champion = self.__database.select_lol_champion(p['championId'])

            runes = []
            for r in p['perks']['perkIds']:
                runes.append(self.__database.select_lol_rune(r)['name'])
            primary = self.__database.select_lol_rune_style(p['perks']['perkStyle'])
            secondary = self.__database.select_lol_rune_style(p['perks']['perkSubStyle'])

            players.append(LoLMatchSpectator.LoLMatchSpectatorTeamPlayer(
                p['summonerName'], [spell1, spell2], champion, p['bot'],
                runes, primary, secondary
            ))

        return LoLMatchSpectator.LoLMatchSpectatorTeam(
            team_id, players
        )

    def __create_champion(self, data):
        stats = data['stats']
        champ_stats = LoLChampion.LoLChampionStats(
            stats['movespeed'], stats['attackrange'], [stats['hp'], stats['hpperlevel']],
            [stats['mp'], stats['mpperlevel']], [stats['armor'], stats['armorperlevel']],
            [stats['spellblock'], stats['spellblockperlevel']],
            [stats['hpregen'], stats['hpregenperlevel']],
            [stats['mpregen'], stats['mpregenperlevel']],
            [stats['crit'], stats['critperlevel']],
            [stats['attackdamage'], stats['attackdamageperlevel']],
            [stats['attackspeedoffset'], stats['attackspeedperlevel']]
        )

        spells = []
        description = self.__parse_spell_description(data['passive']['description'], [], [])
        spells.append(LoLChampion.LoLChampionSpell(
            data['passive']['name'], description, None, None, None
        ))
        for s in data['spells']:
            description = self.__parse_spell_description(s['tooltip'], s['effectBurn'], s['vars'])
            cost = s['resource'].replace('{{ cost }}', s['costBurn'])
            cost = self.__parse_spell_description(cost, s['effectBurn'], s['vars'])
            spells.append(LoLChampion.LoLChampionSpell(
                s['name'], description, s['cooldownBurn'], cost, s['rangeBurn']
            ))

        official = Lv.base_official_champion_url + data['id']

        return LoLChampion.LoLChampion(
            data['id'], data['title'], data['key'], data['lore'],
            [data['allytips'], data['enemytips']], data['tags'], champ_stats, spells,
            '', official
        )
    # endregion

    # region Parsing
    @staticmethod
    def __parse_inputs_and_args(inp, arg_prefix=Gv.argument_prefix):
        try:
            splits = re.split(' ?{}'.format(arg_prefix), inp)
            inp_splits = re.split(' ? ', splits[0])
            return inp_splits, splits[1:]
        except TypeError:
            return None, []

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

    @staticmethod
    def __parse_spell_description(spell, effects, vars,):
        description = spell
        description = re.sub('<br><br>', '\n\t', description)
        description = re.sub('<br>', '\n\t', description)
        description = re.sub('<br /><br />', '\n\t', description)
        description = re.sub('<br />', '\n\t', description)
        description = re.sub('</span>', '', description)

        description = re.sub('<[a-zA-Z0-9]*>', '', description)
        description = re.sub('</[a-zA-Z0-9]*>', '', description)
        description = re.sub('<span class="[a-zA-Z0-9]*">', '', description)
        description = re.sub('<span class=\"[a-zA-Z0-9]*\">', '', description)
        description = re.sub('<span class="size\d* color[a-zA-Z0-9]*">\d*', '', description)

        for i, e in enumerate(effects):
            if e is not None:
                description = description.replace('{{{{ e{} }}}}'.format(i), e)
        for v in vars:
            description = description. \
                replace('{{{{ {} }}}}'.format(v['key']),
                        '{} {}'.format(str(v['coeff']), Lv.spell_effect_burn_map[v['link']]))
        description = re.sub('{{ [a-z][0-9]?\*?[0-9]+ }}', 'X (Based on In-Game Data)', description)
        return description

    @staticmethod
    def __get_command_usage(command, prefix=Gv.argument_prefix, value_prefix=Gv.argument_value_prefix):
        if command == 'player':
            return 'player *name* [{}r{}*region*]'\
                .format(prefix, value_prefix)
        elif command == 'matchlist':
            return 'matchlist *name* [{}r{}*region*] [{]a{}*amount* 1-20]'\
                .format(prefix, value_prefix, prefix, value_prefix)
        elif command == 'match':
            return 'match *id*|*name* *index* [{}r{}*region*] [{}rd] [{}d] [{}t]'\
                .format(prefix, value_prefix, prefix, prefix, prefix)
        elif command == 'timeline':
            return 'timeline *id*|*name* *index* [{}r{}*region*]' \
                .format(prefix, value_prefix)
        elif command == 'buildorder':
            return 'buildorder *name* *id*|*name* *index* [{}r{}*region*]' \
                .format(prefix, value_prefix, prefix, prefix, prefix)
        elif command == 'masteries':
            return 'masteries *name* [{}r{}*region*] [{}a{}*amount* 1+] [{}asc]' \
                .format(prefix, value_prefix, prefix, value_prefix, prefix)
        elif command == 'mastery':
            return 'mastery *name* *champion* [{}r{}*region*]' \
                .format(prefix, value_prefix)
        elif command == 'totalmastery':
            return 'totalmastery *name* [{}r{}*region*]' \
                .format(prefix, value_prefix)
        elif command == 'challengers':
            return 'challengers *queue* [{}r{}*region*] [{}a{}*amount*]' \
                .format(prefix, value_prefix, prefix, value_prefix)
        elif command == 'masters':
            return 'masters *queue* [{}r{}*region*] [{}a{}*amount*]' \
                .format(prefix, value_prefix, prefix, value_prefix)
        elif command == 'status':
            return 'status [{}r{}*region*]' \
                .format(prefix, value_prefix)
        elif command == 'spectate':
            return 'spectate *name* [{}r{}*region*]' \
                .format(prefix, value_prefix)
        elif command == 'champion':
            return 'champion *name* [{}l] [{}t] [{}a]' \
                .format(prefix, prefix, prefix)
        elif command == 'skins':
            return 'skins *name*' \
                .format(prefix, prefix, prefix)
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
