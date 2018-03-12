import re
from enum import Enum
from typing import List, Tuple, Union

import cassiopeia
import datapipelines
import discord
from cassiopeia import *
from discord.ext import commands

from data import utils

""" Self-contained command module for all things League of Legends.

    All Constant, Mappings, Enumerations, Utility Methods relating to LoL and LoL only will be here.
"""


class Error(Enum):
    """
    Enumeration to hold different types of errors.
    """
    REGION_NOT_FOUND = 0
    PLAYER_NOT_FOUND = 1
    MATCHES_NOT_FOUND = 2
    MASTERIES_NOT_FOUND = 3
    RANKS_NOT_FOUND = 4
    INVALID_AMOUNT = 5
    MATCH_NOT_FOUND = 6


class QueueInfo:
    """
    A structure to hold information on a Queue.
    """
    def __init__(self, has_lanes: bool=True, has_score: bool=True, has_vision: bool=True, has_monsters: bool=True,
                 has_towers: bool=True, has_heralds: bool=True, has_dragons: bool=True, has_barons: bool=True,
                 has_vilemaws: bool=True):
        self.has_lanes = has_lanes
        self.has_score = has_score
        self.has_vision = has_vision
        self.has_monsters = has_monsters
        self.has_towers = has_towers
        self.has_heralds = has_heralds
        self.has_dragons = has_dragons
        self.has_barons = has_barons
        self.has_vilemaws = has_vilemaws


class Constant:
    """
    Group of Constants. This includes any lists or dictionaries that contain information.
    """
    DEFAULT_MATCHES = 20
    DEFAULT_REGION = 'NA'
    EMBED_COLOR = 0x18719
    OP_GG_ICON_URL = 'http://opgg-static.akamaized.net/images/logo/l_logo.png'
    COMMAND_INFO = {
        'player': [
            'player <player> [r <region>]',
            'Given a player name, get info on that player.'
        ]
    }
    QUEUE_INFO = {
        cassiopeia.Queue.all_random_summoners_rift: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.all_random_urf: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.all_random_urf_snow: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.aram: QueueInfo(False, False, False, False, True, False, False, False, False),
        cassiopeia.Queue.aram_butchers_bridge: QueueInfo(False, False, False, False, True, False, False, False, False),
        cassiopeia.Queue.ascension: QueueInfo(False, True, False, False, False, False, False, False, False),
        cassiopeia.Queue.black_market_brawlers: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.blind_fives: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.blind_threes:
            QueueInfo(has_lanes=False, has_score=False, has_dragons=False, has_barons=False, has_heralds=False),
        cassiopeia.Queue.blood_hunt_assassin: QueueInfo(has_score=True, has_heralds=True),
        cassiopeia.Queue.coop_ai_beginner_fives: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.coop_ai_beginner_threes:
            QueueInfo(has_lanes=False, has_score=False, has_dragons=False, has_barons=False, has_heralds=False),
        cassiopeia.Queue.coop_ai_intermediate_fives: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.coop_ai_intermediate_threes:
            QueueInfo(has_lanes=False, has_score=False, has_dragons=False, has_barons=False, has_heralds=False),
        cassiopeia.Queue.coop_ai_intro_fives: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.coop_ai_intro_threes:
            QueueInfo(has_lanes=False, has_score=False, has_dragons=False, has_barons=False, has_heralds=False),
        cassiopeia.Queue.custom: QueueInfo(),
        cassiopeia.Queue.dark_star: QueueInfo(False, True, False, False, False, False, False, False, False),
        cassiopeia.Queue.definitely_not_dominion:
            QueueInfo(False, True, False, False, False, False, False, False, False),
        cassiopeia.Queue.doom_bots: QueueInfo(True, True, False, False, False, False, False, False, False),
        cassiopeia.Queue.doom_bots_difficult: QueueInfo(True, True, False, False, False, False, False, False, False),
        cassiopeia.Queue.guardian_invasion_normal:
            QueueInfo(False, True, False, False, False, False, False, False, False),
        cassiopeia.Queue.guardian_invasion_onslaught:
            QueueInfo(False, True, False, False, False, False, False, False, False),
        cassiopeia.Queue.hexakill_summoners_rift: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.hexakill_twisted_treeline:
            QueueInfo(has_lanes=False, has_score=False, has_dragons=False, has_barons=False, has_heralds=False),
        cassiopeia.Queue.mirror_mode_fives: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.nemesis_draft: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.nexus_siege: QueueInfo(False, True, False, False, True, False, False, False, False),
        cassiopeia.Queue.normal_draft_fives: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.one_for_all: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.overcharge: QueueInfo(False, True, False, False, False, False, False, False, False),
        cassiopeia.Queue.poro_king: QueueInfo(False, False, False, False, True, False, False, False, False),
        cassiopeia.Queue.project: QueueInfo(False, True, False, False, False, False, False, False, False),
        cassiopeia.Queue.ranked_flex_fives: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.ranked_flex_threes:
            QueueInfo(has_lanes=False, has_score=False, has_dragons=False, has_barons=False, has_heralds=False),
        cassiopeia.Queue.ranked_solo_fives: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.showdown_1v1: QueueInfo(False, False, False, False, True, False, False, False, False),
        cassiopeia.Queue.showdown_2v2: QueueInfo(False, False, False, False, True, False, False, False, False),
        cassiopeia.Queue.urf: QueueInfo(has_score=False, has_vilemaws=False),
        cassiopeia.Queue.urf_coop_ai: QueueInfo(has_score=False, has_vilemaws=False)
    }
    REGIONS_LIST = [
        'BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR', 'RU', 'PBE'
    ]
    SPLIT_FOR_TIMELINE = 40


class Converter:
    """
    Group of Converters, which are mappings from one type to another (usually a string).
    """
    FROM_LANE_TO_STRING = {
        data.Lane.bot_lane: 'Bottom',
        data.Lane.jungle: 'Jungle',
        data.Lane.mid_lane: 'Middle',
        data.Lane.top_lane: 'Top'
    }
    FROM_QUEUE_TO_STRING = {
        cassiopeia.Queue.all_random_summoners_rift: 'Summoner\'s Rift: All Random',
        cassiopeia.Queue.all_random_urf: 'Summoner\'s Rift: All Random URF',
        cassiopeia.Queue.all_random_urf_snow: 'Summoner\'s Rift: All Random Snow URF',
        cassiopeia.Queue.aram: 'Howling Abyss: ARAM',
        cassiopeia.Queue.aram_butchers_bridge: 'Butcher\'s Bridge: ARAM',
        cassiopeia.Queue.ascension: 'Ascension',
        cassiopeia.Queue.black_market_brawlers: 'Black Market Brawlers',
        cassiopeia.Queue.blind_fives: 'Summoner\'s Rift: Blind Pick',
        cassiopeia.Queue.blind_threes: 'Twisted Treeline: Blind Pick',
        cassiopeia.Queue.blood_hunt_assassin: 'Blood Hunt: Assassin',
        cassiopeia.Queue.coop_ai_beginner_fives: 'Summoner\'s Rift: Coop vs. Beginner AI',
        cassiopeia.Queue.coop_ai_beginner_threes: 'Twisted Treeline: Coop vs. Beginner AI',
        cassiopeia.Queue.coop_ai_intermediate_fives: 'Summoner\'s Rift: Coop vs. Intermediate AI',
        cassiopeia.Queue.coop_ai_intermediate_threes: 'Twisted Treeline: Coop vs. Intermediate AI',
        cassiopeia.Queue.coop_ai_intro_fives: 'Summoner\'s Rift: Coop vs. Intro AI',
        cassiopeia.Queue.coop_ai_intro_threes: 'Twisted Treeline: Coop vs. Intro AI',
        cassiopeia.Queue.custom: 'Custom',
        cassiopeia.Queue.dark_star: 'Darkstar: Singularity',
        cassiopeia.Queue.definitely_not_dominion: 'Definitely Not Dominion',
        cassiopeia.Queue.doom_bots: 'Doom Bots',
        cassiopeia.Queue.doom_bots_difficult: 'Doom Bots Vote',
        cassiopeia.Queue.guardian_invasion_normal: 'Star Guardians: Invasion',
        cassiopeia.Queue.guardian_invasion_onslaught: 'Star Guardians: Invasion Onslaught',
        cassiopeia.Queue.hexakill_summoners_rift: 'Summoner\'s Rift: Hexakill',
        cassiopeia.Queue.hexakill_twisted_treeline: 'Twisted Treeline: Hexakill',
        cassiopeia.Queue.mirror_mode_fives: 'Summoner\'s Rift: Mirror Mode',
        cassiopeia.Queue.nemesis_draft: 'Summoner\'s Rift: Nemesis Draft',
        cassiopeia.Queue.nexus_siege: 'Nexus Siege',
        cassiopeia.Queue.normal_draft_fives: 'Summoner\'s Rift: Normal Draft',
        cassiopeia.Queue.one_for_all: 'Summoner\'s Rift: One For All',
        cassiopeia.Queue.overcharge: 'PROJECT//: Overcharge',
        cassiopeia.Queue.poro_king: 'Legend of the Poro King',
        cassiopeia.Queue.project: 'PROJECT//: Overcharge',
        cassiopeia.Queue.ranked_flex_fives: 'Summoner\'s Rift: Ranked Flex',
        cassiopeia.Queue.ranked_flex_threes: 'Twisted Treeline: Ranked Flex',
        cassiopeia.Queue.ranked_solo_fives: 'Summoner\'s Rift: Ranked Solo/Duo',
        cassiopeia.Queue.showdown_1v1: 'Snowdown Showdown 1v1',
        cassiopeia.Queue.showdown_2v2: 'Snowdown Showdown 2v2',
        cassiopeia.Queue.urf: 'Summoner\'s Rift: URF',
        cassiopeia.Queue.urf_coop_ai: 'Summoner\'s Rift: Coop vs AI URF'
    }
    FROM_ROLE_TO_STRING = {
        data.Role.adc: 'Carry',
        data.Role.jungle: 'Jungle',
        data.Role.middle: 'Middle',
        data.Role.support: 'Support',
        data.Role.top: 'Top',
        'DUO': 'Duo',
        'SOLO': 'Solo'
    }
    FROM_RUNE_PATH_TO_STRING = {
        data.RunePath.domination: 'Domination',
        data.RunePath.inspiration: 'Inspiration',
        data.RunePath.precision: 'Precision',
        data.RunePath.resolve: 'Resolve',
        data.RunePath.sorcery: 'Sorcery'
    }
    FROM_SEASON_TO_STRING = {
        cassiopeia.Season.preseason_3: 'Preseason 3',
        cassiopeia.Season.preseason_4: 'Preseason 2014',
        cassiopeia.Season.preseason_5: 'Preseason 2015',
        cassiopeia.Season.preseason_6: 'Preseason 2016',
        cassiopeia.Season.preseason_7: 'Preseason 2017',
        cassiopeia.Season.preseason_8: 'Preseason 2018',
        cassiopeia.Season.season_3: 'Season 3',
        cassiopeia.Season.season_4: 'Season 2014',
        cassiopeia.Season.season_5: 'Season 2015',
        cassiopeia.Season.season_6: 'Season 2016',
        cassiopeia.Season.season_7: 'Season 2017',
        cassiopeia.Season.season_8: 'Season 2018',
    }


class LoL(object):
    def __init__(self, bot: commands.Bot, prefix: str, arg_prefix: str, val_prefix: str):
        self.bot = bot
        self.prefix = prefix
        self.arg_prefix = arg_prefix
        self.val_prefix = val_prefix
        self.help = self.create_help()

    # region COMMANDS
    @commands.group()
    async def lol(self, ctx: commands.Context) -> None:
        """ A command group that houses all commands found here.
        :param ctx: Context of the message.
        :return: None.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid Command: {}. <:dab:390040479951093771>'.format(ctx.subcommand_passed))

    @lol.command(name='help', aliases=['?', 'commands'])
    async def _help(self, ctx: commands.Context) -> None:
        utils.print_command(ctx.command)
        msg = await ctx.send(content=ctx.author.mention, embed=self.help)
        await self.react_to(msg, ['hellyeah', 'dorawinifred', 'cutegroot', 'dab'])

    @lol.command(name='buildorder', aliases=['events', 'history'])
    async def build_order(self, ctx: commands.Context, name: str, index: int, *, args: str = None) \
            -> None:
        utils.print_command(ctx.command, [name, index], args)
        # Validate Inputs, Parse and Extract Args.
        args = self.parse_args(args)
        # Get region
        _, region = self.parse_single_arg(args, 'r', True)
        region_temp = self.get_region(region)
        if region_temp is None:
            raise commands.UserInputError(self.get_error_message(Error.REGION_NOT_FOUND, region))
        region = region_temp
        # Retrieve Data
        # Get Summoner
        try:
            summoner = cassiopeia.get_summoner(name=name, region=region.upper())
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.PLAYER_NOT_FOUND, name, region))
        try:
            match = cassiopeia.get_match(id=index, region=region.upper())
        except datapipelines.NotFoundError:
            match = None
            raise commands.UserInputError(self.get_error_message(Error.MATCHES_NOT_FOUND, name, region))
        if match is None:
            # Summoner Name and Match Index given
            # Get Matches
            try:
                matches = cassiopeia.get_match_history(summoner=summoner, begin_index=index - 1, end_index=index)
            except datapipelines.NotFoundError:
                raise commands.UserInputError(self.get_error_message(Error.MATCHES_NOT_FOUND, name, region))
            # Get Match
            match = matches[summoner.name]
        # Create and Display Embed
        await self.display_embed(ctx, ctx.author.mention, self.create_build_order(ctx, match, summoner))

    @lol.command()
    async def match(self, ctx: commands.Context, identifier: str, index: int=None, *, args: str=None)\
            -> None:
        utils.print_command(ctx.command, [identifier, index], args)
        # Validate Inputs, Parse and Extract Args.
        try:
            mid = int(identifier)
        except ValueError:
            mid = None
        args = self.parse_args(args)
        # Get region
        _, region = self.parse_single_arg(args, 'r', True)
        region_temp = self.get_region(region)
        if region_temp is None:
            raise commands.UserInputError(self.get_error_message(Error.REGION_NOT_FOUND, region))
        region = region_temp
        # Get options
        use_bare, _ = self.parse_single_arg(args, 'b')
        # Retrieve Data
        if mid is not None:
            # Match ID given
            # Get Match
            try:
                match = cassiopeia.get_match(id=mid, region=region.upper())
            except datapipelines.NotFoundError:
                raise commands.UserInputError(self.get_error_message(Error.MATCHES_NOT_FOUND, identifier, region))
        elif index is None:
            # Summoner Name given but no index
            raise commands.MissingRequiredArgument(index)
        else:
            # Summoner Name and Match Index given
            # Get Summoner
            try:
                summoner = cassiopeia.get_summoner(name=identifier, region=region.upper())
            except datapipelines.NotFoundError:
                raise commands.UserInputError(self.get_error_message(Error.PLAYER_NOT_FOUND, identifier, region))
            # Get Matches
            try:
                matches = cassiopeia.get_match_history(summoner=summoner, begin_index=index - 1, end_index=index)
            except datapipelines.NotFoundError:
                raise commands.UserInputError(self.get_error_message(Error.MATCHES_NOT_FOUND, identifier, region))
            # Get Match
            match = list(matches)[0]
        # Create and Display Embed
        await self.display_embed(ctx, ctx.author.mention, self.create_match(ctx, match, use_bare))

    @lol.command(aliases=['matchlist', 'recent'])
    async def matches(self, ctx: commands.Context, name: str, *, args: str=None) -> None:
        utils.print_command(ctx.command, [name], args)
        # Validate Inputs, Parse and Extract Args.
        args = self.parse_args(args)
        # Get region
        _, region = self.parse_single_arg(args, 'r', True)
        region_temp = self.get_region(region)
        if region_temp is None:
            raise commands.UserInputError(self.get_error_message(Error.REGION_NOT_FOUND, region))
        region = region_temp
        # Get amount
        _, amount = self.parse_single_arg(args, 'a', True)
        amount = self.get_amount(amount)
        if amount is None:
            raise commands.BadArgument(self.get_error_message(Error.INVALID_AMOUNT, 1, 20))
        # Retrieve Data
        # Get Summoner
        try:
            summoner = cassiopeia.get_summoner(name=name, region=region.upper())
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.PLAYER_NOT_FOUND, name, region))
        # Get matches
        try:
            matches = cassiopeia.get_match_history(summoner=summoner, end_index=amount)
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.MATCHES_NOT_FOUND, name, region))
        # Create and Display Embed
        await self.display_embed(ctx, ctx.author.mention, self.create_matches(ctx, summoner, matches))

    @lol.command(aliases=['summoner', 'profile'])
    async def player(self, ctx: commands.Context, name: str, *, args: str=None) -> None:
        utils.print_command(ctx.command, [name], args)
        # Validate Inputs, Parse and Extract Args.
        args = self.parse_args(args)
        # Get region
        _, region = self.parse_single_arg(args, 'r', True)
        region_temp = self.get_region(region)
        if region_temp is None:
            raise commands.UserInputError(self.get_error_message(Error.REGION_NOT_FOUND, region))
        region = region_temp
        # Retrieve Data
        # Get Summoner
        try:
            summoner = cassiopeia.get_summoner(name=name, region=region.upper())
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.PLAYER_NOT_FOUND, name, region))
        # Get Matches
        try:
            matches = cassiopeia.get_match_history(summoner=summoner, end_index=20)
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.MATCHES_NOT_FOUND, name, region))
        # Get Masteries
        try:
            masteries = cassiopeia.get_champion_masteries(summoner=summoner, region=summoner.region)
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.MASTERIES_NOT_FOUND, name, region))
        # Get Leagues
        try:
            leagues = cassiopeia.get_league_positions(summoner=summoner)
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.RANKS_NOT_FOUND, name, region))
        # Create and Display Embed
        await self.display_embed(ctx, ctx.author.mention,
                                 self.create_player(ctx, summoner, matches, masteries, leagues))

    @lol.command(aliases=['events', 'history'])
    async def timeline(self, ctx: commands.Context, identifier: str, index: int = None, *, args: str = None) \
            -> None:
        """Until Cassiopeia fixes"""
        utils.print_command(ctx.command, [identifier, index], args)
        # Validate Inputs, Parse and Extract Args.
        try:
            mid = int(identifier)
        except ValueError:
            mid = None
        args = self.parse_args(args)
        # Get region
        _, region = self.parse_single_arg(args, 'r', True)
        region_temp = self.get_region(region)
        if region_temp is None:
            raise commands.UserInputError(self.get_error_message(Error.REGION_NOT_FOUND, region))
        region = region_temp
        # Retrieve Data
        if mid is not None:
            # Match ID given
            # Get Match
            try:
                match = cassiopeia.get_match(id=mid, region=region.upper())
            except datapipelines.NotFoundError:
                raise commands.UserInputError(self.get_error_message(Error.MATCHES_NOT_FOUND, identifier, region))
        elif index is None:
            # Summoner Name given but no index
            raise commands.MissingRequiredArgument(index)
        else:
            # Summoner Name and Match Index given
            # Get Summoner
            try:
                summoner = cassiopeia.get_summoner(name=identifier, region=region.upper())
            except datapipelines.NotFoundError:
                raise commands.UserInputError(self.get_error_message(Error.PLAYER_NOT_FOUND, identifier, region))
            # Get Matches
            try:
                matches = cassiopeia.get_match_history(summoner=summoner, begin_index=index - 1, end_index=index)
            except datapipelines.NotFoundError:
                raise commands.UserInputError(self.get_error_message(Error.MATCHES_NOT_FOUND, identifier, region))
            # Get Match
            match = matches[summoner.name]
        # Create and Display Embed
        await self.display_embed(ctx, ctx.author.mention, self.create_timeline(ctx, match))
    # endregion

    # region ERROR
    @staticmethod
    async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingRequiredArgument):
            splits = re.split(' ', error.__str__())
            string = f'**{splits[0]}**'
            await ctx.send(' '.join([string] + splits[1:]))
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error)
        elif isinstance(error, commands.UserInputError):
            await ctx.send(error)
        else:
            raise error
    # endregion

    # region EMBED FACTORIES
    @staticmethod
    def create_help() -> discord.Embed:
        return discord.Embed(title='Helps')

    def create_build_order(self, ctx: commands.Context, match: cassiopeia.Match, summoner: cassiopeia.Summoner)\
            -> List[discord.Embed]:
        embeds = []
        embed = utils.create_embed_template(
            description=f'Build Order for __**{Summoner.name}**__ '
                        f'in Match __**{match.id}**__ in __**{match.region.value}**__.',
            color=Constant.EMBED_COLOR, requester=ctx.author, author=f'Match History: {summoner.name}, {match.id}',
            author_url=self.get_match_history_url(match.region.value, match.platform.value, match.id)
        )
        participants = match.blue_team.participants + match.red_team.participants
        pid = None
        for p in participants:
            if p.summoner.name == summoner.name:
                pid = p.id
                break
        events = []
        for f in match.timeline.frames:
            for e in f.events:
                if e.type in ['ITEM_PURCHASED', 'ITEM_SOLD', 'ITEM_DESTROYED', 'ITEM_UNDO']:
                    events.append(e)
        for i, e in enumerate(events):
            string = ''
            if pid == e.participantId:
                item = cassiopeia.get_items('NA')[e.item_id].name
                if e.type == 'ITEM_PURCHASED':
                    string = f'Bought {item}.'
                elif e.type == 'ITEM_SOLD':
                    string = f'Sold {item}.'
                elif e.type == 'ITEM_DESTROYED':
                    string = f'Used {item}.'
                else:
                    string = f'Undid {item}.'
            if string != '':
                timestamp = self.get_time_stamp(e.timestamp)
                timestamp = f'{timestamp[0]}:{timestamp[1]:02d}'
                embed.add_field(name=f'@**{timestamp}:**\n', value=string, inline=False)
            if i % Constant.SPLIT_FOR_TIMELINE >= Constant.SPLIT_FOR_TIMELINE - 1:
                embeds.append(embed)
                embed = utils.create_embed_template(
                    description=f'Build Order for __**{Summoner.name}**__ '
                                f'in Match __**{match.id}**__ in __**{match.region.value}**__.',
                    color=Constant.EMBED_COLOR, requester=ctx.author,
                    author=f'Match History: {summoner.name}, {match.id}',
                    author_url=self.get_match_history_url(match.region.value, match.platform.value, match.id)
                )
            if len(events) - i == 1:
                embeds.append(embed)
        return embeds

    def create_match(self, ctx: commands.Context, match: cassiopeia.Match, use_bare: bool=False)\
        -> List[discord.Embed]:
        embeds = []
        embed = utils.create_embed_template(
            description=f'Overview of Match __**{match.id}**__ in __**{match.region.value}**__.',
            color=Constant.EMBED_COLOR, requester=ctx.author, author=f'Match History: {match.id}',
            author_url=self.get_match_history_url(match.region.value, match.platform.value, match.id)
        )
        queue = Constant.QUEUE_INFO[match.queue]
        # Add Core Info
        embed.add_field(name='__Core Info:__',
                        value=f'**{Converter.FROM_SEASON_TO_STRING[match.season]}**\n'
                              f'**{Converter.FROM_QUEUE_TO_STRING[match.queue]}**\n'
                              f'**Duration:** {match.duration}\n',
                        inline=False)
        # Add Team Info
        for t in [match.blue_team, match.red_team]:
            result = 'VICTORY' if t.win else 'DEFEAT'
            string = f'**{result}**\n'
            if queue.has_towers:
                string += f'**Towers:** {t.tower_kills}'
                if t.first_tower:
                    string += '  Got **First Tower.**'
                string += '\n'
                string += f'**Inhibitors:** {t.inhibitor_kills}'
                if t.first_inhibitor:
                    string += '  Got **First Inhibitor.**'
                string += '\n'
            if queue.has_dragons:
                string += f'**Dragons:** {t.dragon_kills}'
                if t.first_dragon:
                    string += '  Got **First Dragon.**'
                string += '\n'
            if queue.has_barons:
                string += f'**Barons:** {t.baron_kills}'
                if t.first_baron:
                    string += '  Got **First Baron.**'
                string += '\n'
            if queue.has_heralds:
                string += f'**Herald:** {t.rift_herald_kills}'
                if t.first_rift_herald:
                    string += '  Got **First Herald.**'
                string += '\n'
            if queue.has_vilemaws:
                string += f'**Vile\'Maws:** {t.vilemaw_kills}\n'
            if t.first_blood:
                string += 'Got **First Blood.**\n'
            # Bans are bugged
            # if t.bans:
            #     string += '**BANS:**\n'
            #     for i, b in enumerate(t.bans):
            #         champion = cassiopeia.get_champion(b.key, 'NA')
            #         champion = champion.name if champion is not None else 'None'
            #         string += f'{i + 1}. {champion}\n'

            embed.add_field(name=f'__TEAM {t.side.value // 100}__',
                            value=string,
                            inline=True)
        embeds.append(embed)
        for t in [match.blue_team, match.red_team]:
            for p in t.participants:
                embed = utils.create_embed_template(
                    description=f'Overview of __**Team {t.side.value // 100}**__\'s __**{p.summoner.name}**__.',
                    color=Constant.EMBED_COLOR, requester=ctx.author, author=f'OP.GG: {p.summoner.name}',
                    author_url = self.get_op_gg_url(p.summoner.region.value, p.summoner.name),
                    icon_url = Constant.OP_GG_ICON_URL
                )
                stats = p.stats
                # Add Overview & Items
                champion = cassiopeia.get_champion(p.champion.key, 'NA').name
                role = Converter.FROM_ROLE_TO_STRING[p.role] if p.role is not None else ' '
                string = f'**Champion:** {champion}'
                if queue.has_lanes:
                    string += f' {Converter.FROM_LANE_TO_STRING[p.lane]} {role}'
                string += '\n'
                string += f'**Previously:** {p.rank_last_season.value}\n'
                string += f'**Summoner Spells:** {p.summoner_spell_d.name} {p.summoner_spell_f.name}\n'
                string += '**Final Items:**\n'
                for i, j in enumerate(stats.items):
                    item = cassiopeia.get_items('NA')[j.id].name if j is not None else 'None'
                    string += f'{i + 1}. {item}\n'
                embed.add_field(name='__OVERVIEW:__', value=string)
                # Add Core Stats: KDA, CS, Monsters, VS, CC, Gold, Score
                string = f'**KDA:** {stats.kills} / {stats.deaths} / {stats.assists}  '
                string += f'**Level:** {stats.level}\n'
                if queue.has_score:
                    string += f'**Score:** {stats.total_player_score}\n'
                    string += f'\t**Combat:** {stats.combat_player_score}\n'
                    string += f'\t**Objective:** {stats.objective_player_score}\n'
                cs = stats.total_minions_killed + (stats.neutral_minions_killed if queue.has_monsters else 0)
                string += f'**CS:** {cs}'
                if queue.has_monsters:
                    string += f'  **Monsters:** {stats.neutral_minions_killed}\n'
                    string += f'\t**In Team Jungle:** {stats.neutral_minions_killed_team_jungle}\n'
                    string += f'\t**In Enemy Jungle:** {stats.neutral_minions_killed_enemy_jungle}\n'
                else:
                    string += '\n'
                if queue.has_vision:
                    string += f'**Vision Score:** {stats.vision_score}\n'
                    string += f'\t**Control Wards Bought:** {stats.vision_wards_bought_in_game}\n'
                    string += f'\t**Wards Placed:** {stats.wards_placed}\n'
                    string += f'\t**Wards Killed:** {stats.wards_killed}\n'
                string += f'**Crowd Control:** {stats.total_time_crowd_control_dealt}\n'
                string += f'**Gold Spent / Earned:** {stats.gold_spent} / {stats.gold_earned}\n'
                embed.add_field(name='__BASIC:__', value=string)
                # Add Advanced Stats:
                if not use_bare:
                    string = f'**Killing Sprees:** {stats.killing_sprees}  **Largest:** {stats.largest_killing_spree}\n'
                    string += f'**Largest Multi Kill:** {stats.largest_multi_kill}\n'
                    string += f'\t**Double Kills:** {stats.double_kills}\n'
                    string += f'\t**Triple Kills:** {stats.triple_kills}\n'
                    string += f'\t**Quadra Kills:** {stats.quadra_kills}\n'
                    string += f'\t**Penta Kills:** {stats.penta_kills}\n'
                    string += f'\t**Unreal Kills:** {stats.unreal_kills}\n'
                    if stats.first_blood_kill or stats.first_blood_assist:
                        string += '\tGot **First Blood**.\n'
                    string += f'**Total Damage Dealt:** {stats.total_damage_dealt}\n'
                    string += f'\t**Magical:** {stats.magic_damage_dealt}\n'
                    string += f'\t**Physical:** {stats.physical_damage_dealt}\n'
                    string += f'\t**True:** {stats.true_damage_dealt}\n'
                    string += f'**Total To Champions:** {stats.total_damage_dealt_to_champions}\n'
                    string += f'\t**Magical:** {stats.magic_damage_dealt_to_champions}\n'
                    string += f'\t**Physical:** {stats.physical_damage_dealt_to_champions}\n'
                    string += f'\t**True:** {stats.true_damage_dealt_to_champions}\n'
                    string += f'**Total Damage Taken:** {stats.total_damage_taken}\n'
                    string += f'\t**Magical:** {stats.magical_damage_taken}\n'
                    string += f'\t**Physical:** {stats.physical_damage_taken}\n'
                    string += f'\t**True:** {stats.true_damage_taken}\n'
                    string += f'**Damage Self Mitigated:** {stats.damage_self_mitigated}\n'
                    string += f'**Total Healing:** {stats.total_heal}\n'
                    string += f'**Largest Critical Strike:** {stats.largest_critical_strike}\n'
                    string += f'**Damage to Objectives:** {stats.damage_dealt_to_objectives}\n'
                    if queue.has_towers:
                        string += f'\t**Damage to Towers:** {stats.damage_dealt_to_turrets}\n'
                        string += f'\t**Tower Kills:** {stats.turret_kills}'
                        if stats.first_tower_kill or stats.first_tower_assist:
                            string += '  Got **First Tower**.'
                        string += '\n'
                        string += f'\t**Inhibitor Kills:** {stats.inhibitor_kills}'
                        if stats.first_inhibitor_kill or stats.first_inhibitor_assist:
                            string += '  Got **First Inhibitor**.'
                        string += '\n'
                    embed.add_field(name='__ADVANCED:__', value=string)
                # Add Runes
                runes = list(p.runes)
                string = f'**Primary:** {runes[0].path.value}\n'
                for r in runes[:4]:
                    if r.is_keystone:
                        rune = f'**{r.name}**'
                    else:
                        rune = f'{r.name}'
                    string += f'\t{rune}\n'
                string += f'**Secondary:** {runes[4].path.value}\n'
                for r in runes[4:]:
                    string += f'\t{r.name}\n'
                embed.add_field(name='__RUNES:__', value=string)
                embeds.append(embed)
        return embeds

    def create_matches(self, ctx: commands.Context, summoner: cassiopeia.Summoner, matches: cassiopeia.MatchHistory)\
            -> List[discord.Embed]:
        embed = utils.create_embed_template(
            description=f'{len(matches)} most recent matches of '
                        f'__**{summoner.name}**__ in __**{summoner.region.value}**__.',
            color=Constant.EMBED_COLOR, requester=ctx.author, thumbnail=summoner.profile_icon.url,
            author=f'OP.GG: {summoner.name}', author_url=self.get_op_gg_url(summoner.region.value, summoner.name),
            icon_url=Constant.OP_GG_ICON_URL
        )
        # Add Basic Info
        for i, m in enumerate(matches):
            player = m.participants[summoner]
            result = 'VICTORY' if player.team.win else 'DEFEAT'
            role = Converter.FROM_ROLE_TO_STRING[player.role] if player.role is not None else ' '
            champion = cassiopeia.get_champion(player.champion.key, 'NA').name
            queue = Constant.QUEUE_INFO[m.queue]
            lane = f'{Converter.FROM_LANE_TO_STRING[player.lane]} {role}' if queue.has_lanes else ''
            cs = player.stats.total_minions_killed + (player.stats.neutral_minions_killed if queue.has_monsters else 0)
            vs = f'**VS:** {player.stats.vision_score}' if queue.has_vision else ''
            embed.add_field(name=f'{i + 1}. __**{m.id}:**__',
                            value=f'\t**{result}**\n\t**{Converter.FROM_SEASON_TO_STRING[m.season]}**\n'
                                  f'\t**{Converter.FROM_QUEUE_TO_STRING[m.queue]}**\n'
                                  f'\t**Duration:** {m.duration}\n\t**Champion:** {champion} {lane}\n\t'
                                  f'**KDA:** {player.stats.kills} / {player.stats.deaths} / {player.stats.assists}\n'
                                  f'\t**CS:** {cs}  {vs}',
                            inline=False)
        return [embed]

    def create_player(self, ctx: commands.Context, summoner: cassiopeia.Summoner, matches: cassiopeia.MatchHistory,
                      masteries: cassiopeia.ChampionMasteries, leagues: cassiopeia.LeagueEntries) \
            -> List[discord.Embed]:
        embed = utils.create_embed_template(
            description=f'Overview of __**{summoner.name}**__ in __**{summoner.region.value}**__.',
            color=Constant.EMBED_COLOR, requester=ctx.author, thumbnail=summoner.profile_icon.url,
            author=f'OP.GG: {summoner.name}', author_url=self.get_op_gg_url(summoner.region.value, summoner.name),
            icon_url=Constant.OP_GG_ICON_URL
        )
        # Add Basic Info
        embed.add_field(name='__Core:__', value=f'**Level:** {summoner.level}', inline=False)
        # Add Recent Game Info
        games, wins, kills, deaths, assists, vision, cs = len(matches), 0, 0, 0, 0, 0, 0
        for m in matches:
            player = m.participants[summoner]
            if player.team.win:
                wins += 1
            kills += player.stats.kills
            deaths += player.stats.deaths
            assists += player.stats.assists
            vision += player.stats.vision_score
            cs += player.stats.total_minions_killed + player.stats.neutral_minions_killed
        losses = games - wins
        if games > 0:
            kills /= games
            deaths /= games
            assists /= games
            vision /= games
            cs /= games
        win_rate = wins / games * 100 if games > 0 else 0
        embed.add_field(name=f'__Recent {games} Games:__',
                        value=f'**W/L:** {wins}W / {losses}L\n**Win Rate:** {win_rate:.2f}%\n'
                              f'**KDA:** {kills:.2f} / {deaths:.2f} / {assists: .2f}  '
                              f'**R:** {(kills + assists) / (deaths + 1):.2f}\n'
                              f'**CS:** {cs:.2f}  **VS:** {vision:.2f}')
        # Add Mastery Info
        mastery_string = ''
        top_5 = list(masteries)[:5]
        if len(top_5) < 1:
            mastery_string += 'No champions mastered.'
        for i, m in enumerate(top_5):
            champion = cassiopeia.get_champion(m.champion.key, region='NA')
            mastery_string += f'{i + 1}. **{champion.name}** (**{m.level}**) {m.points} pts.\n'
        embed.add_field(name=f'__Top {len(top_5)} Champions:__', value=mastery_string)
        # Add Ranked Info
        win_rate = wins / games * 100 if games > 0 else 0
        for l in leagues:
            ranked_string = f'**Name:** {l.name}\n**Rank:** {l.tier.value} {l.division.value}\n' \
                            f'**W/L:** {l.wins}W / {l.losses}L' \
                            f'  **Win Rate:** {win_rate:.2f}%\n**LP:** {l.league_points}\n'
            if l.fresh_blood:
                ranked_string += 'Fresh Blood. '
            if l.hot_streak:
                ranked_string += 'Hot Streak. '
            if l.veteran:
                ranked_string += 'Veteran. '
            embed.add_field(name=f'__{utils.get_sanitized_value(l.queue.value)}:__',
                            value=ranked_string)
        return [embed]

    def create_timeline(self, ctx: commands.Context, match: cassiopeia.Match) -> List[discord.Embed]:
        embeds = []
        embed = utils.create_embed_template(
            description=f'Timeline of Match __**{match.id}**__ in __**{match.region.value}**__.',
            color=Constant.EMBED_COLOR, requester=ctx.author, author=f'Match History: {match.id}',
            author_url=self.get_match_history_url(match.region.value, match.platform.value, match.id)
        )
        participants = match.blue_team.participants + match.red_team.participants
        events = []
        for f in match.timeline.frames:
            for e in f.events:
                if e.type in ['CHAMPION_KILL', 'BUILDING_KILL', 'ELITE_MONSTER_KILL']:
                    events.append(e)
        for i, e in enumerate(events):
            string = ''
            if e.type == 'CHAMPION_KILL':
                killer = participants[e.killer_id - 1]
                team = killer.side.value // 100
                champion = cassiopeia.get_champion(killer.champion.key, 'NA')
                killer = f'{champion.name} ({killer.summoner.name})'
                victim = participants[e.victim_id - 1]
                champion = cassiopeia.get_champion(victim.champion.key, 'NA')
                victim = f'{champion.name} ({victim.summoner.name})'
                event = f'**Team {team}** has slain **{victim}**\n'
                event += f'\tBy **{killer}**\n'
                if e.assisting_participants:
                    event += '\tAssisted By:\n'
                for a in e.assisting_participants:
                    assist = participants[a - 1]
                    champion = cassiopeia.get_champion(assist.champion.key, 'NA')
                    assist = f'{champion.name} ({assist.summoner.name})'
                    event += f'\t\t**{assist}**\n'
                string += f'{event}'
            elif e.type == 'BUILDING_KILL':
                killer = participants[e.killer_id - 1]
                team = killer.side.value // 100
                champion = cassiopeia.get_champion(killer.champion.key, 'NA')
                killer = f'{champion.name} ({killer.summoner.name})'
                # Until timeline's event.lane_type is fixed
                # if e.lane_type == 'MID_LANE':
                #     lane = 'Middle'
                # elif e.lane_type == 'BOT_LANE':
                #     lane = 'Bottom'
                # elif e.lane_type == 'TOP_LANE':
                #     lane = 'Top'
                # else:
                #     lane = None
                if e.tower_type == 'NEXUS_TURRET':
                    victim = 'Nexus Tower'
                elif e.building_type == 'INHIBITOR_BUILDING':
                    victim = 'Inhibitor'
                elif e.tower_type == 'INNER_TURRET':
                    victim = 'Inner Tower'
                elif e.tower_type == 'OUTER_TURRET':
                    victim = 'Outer Tower'
                elif e.tower_type == 'BASE_TURRET':
                    victim = 'Base Tower'
                event = f'**Team {team}** has destroyed the **{victim}**\n'
                event += f'\tBy **{killer}**\n'
                if e.assisting_participants:
                    event += '\tAssisted By:\n'
                for a in e.assisting_participants:
                    assist = participants[a - 1]
                    champion = cassiopeia.get_champion(assist.champion.key, 'NA')
                    assist = f'{champion.name} ({assist.summoner.name})'
                    event += f'\t\t**{assist}**\n'
                string += f'{event}'
            elif e.type == 'ELITE_MONSTER_KILL':
                killer = participants[e.killer_id - 1]
                team = killer.side.value // 100
                champion = cassiopeia.get_champion(killer.champion.key, 'NA')
                killer = f'{champion.name} ({killer.summoner.name})'
                if e.monster_type == 'BARON_NASHOR':
                    victim = 'Baron'
                elif e.monster_type == 'RIFTHERALD':
                    victim = 'Rift Herald'
                elif e.monster_type == 'VILE_MAW':
                    victim = 'Vile\'Maw'
                elif e.monster_type == 'DRAGON':
                    victim = 'Dragon'
                    # Monster Sub Type is bugged
                    # if e.monster_sub_type == 'WATER_DRAGON':
                    #     victim = 'Ocean Dragon'
                    # elif e.monster_sub_type == 'AIR_DRAGON':
                    #     victim = 'Cloud Dragon'
                    # elif e.monster_sub_type == 'EARTH_DRAGON':
                    #     victim = 'Mountain Dragon'
                    # elif e.monster_sub_type == 'FIRE_DRAGON':
                    #     victim = 'Infernal Dragon'
                    # elif e.monster_sub_type == 'ELDER_DRAGON':
                    #     victim = 'Elder Dragon'
                event = f'**Team {team}** has slain the **{victim}**\n'
                event += f'\tBy **{killer}**\n'
                string += f'{event}'
            if string != '':
                timestamp = self.get_time_stamp(e.timestamp)
                timestamp = f'{timestamp[0]}:{timestamp[1]:02d}'
                embed.add_field(name=f'@**{timestamp}:**\n', value=string, inline=False)
            # TODO: Add events for Ascension, Poro King
            if i % Constant.SPLIT_FOR_TIMELINE >= Constant.SPLIT_FOR_TIMELINE - 1:
                embeds.append(embed)
                embed = utils.create_embed_template(
                    description=f'Timeline of Match __**{match.id}**__ in __**{match.region.value}**__.',
                    color=Constant.EMBED_COLOR, requester=ctx.author, author=f'Match History: {match.id}',
                    author_url=self.get_match_history_url(match.region.value, match.platform.value, match.id)
                )
            if len(events) - i == 1:
                embeds.append(embed)
        return embeds
    # endregion

    # region HELPERS
    # region BUILDERS

    # endregion

    # region DISPLAYS
    @staticmethod
    async def display_embed(ctx: commands.Context, content: str=None, embeds: list=None) -> None:
        for i, e in enumerate(embeds):
            if i == 0:
                await ctx.send(content=content, embed=e)
            else:
                await ctx.send(embed=e)

    # endregion
    # region GETTERS
    @staticmethod
    def get_error_message(error_type: Error, *args) -> str:
        if error_type == Error.REGION_NOT_FOUND:
            return f'**{args[0]}** not found.'
        elif error_type == Error.PLAYER_NOT_FOUND:
            return f'**{args[0]}** not found in **{args[1]}**.'
        elif error_type == Error.MATCHES_NOT_FOUND:
            return f'Matches not found for **{args[0]}** in **{args[1]}**.'
        elif error_type == Error.MASTERIES_NOT_FOUND:
            return f'Masteries not found for **{args[0]}** in **{args[1]}**.'
        elif error_type == Error.RANKS_NOT_FOUND:
            return f'Ranks not found for **{args[0]}** in **{args[1]}**.'
        elif error_type == Error.INVALID_AMOUNT:
            return f'Amount must be an integer between **{args[0]}** and **{args[1]}**.'
        elif error_type == Error.MATCHES_NOT_FOUND:
            return f'Match **{args[0]}** not found in **{args[1]}**.'
        else:
            return ''

    @staticmethod
    def get_match_history_url(region: str, platform: str, match_id: int, player_id: int=None):
        if region == 'kr':
            url = f'https://matchhistory.leagueoflegends.co.kr/ko/#match-details/KR/{match_id}'
        else:
            url = f'https://matchhistory.{region}.leagueoflegends.com/en/#match-details/{platform}/{match_id}'
        if player_id is not None:
            url += f'/{player_id}'
        url += '?tab=overview'
        return url

    @staticmethod
    def get_op_gg_url(region: str, name: str) -> str:
        name = name.replace(' ', '+')
        return f'http://{region}.op.gg/summoner/userName={name}'

    @staticmethod
    def get_time_stamp(time):
        time = time / 1000 / 60
        return int(time), int(time % 1 * 60)

    @staticmethod
    def get_within_bounds(value: int, min_value: int, max_value: int, default: int) -> Union[int, None]:
        if value is None:
            return default
        if 0 < max_value < value:
            return None
        if value < min_value:
            return None
        return value

    def get_amount(self, amount: int) -> Union[int, None]:
        try:
            return self.get_within_bounds(amount, 1, 20, 20)
        except ValueError:
            return None

    @staticmethod
    def get_region(region: str) -> str:
        if region is None:
            return 'NA'
        return region if region.upper() in Constant.REGIONS_LIST else None
    # endregion

    # region PARSERS
    def parse_args(self, args: str) -> Union[List[str], None]:
        try:
            return re.split(' ?{}'.format(self.arg_prefix), args)
        except TypeError:
            return None
        except ValueError:
            return None

    def parse_single_arg(self, args: list, arg: str, has_value: bool=False) \
            -> Union[Tuple[bool, Union[str, None]], None]:
        if args is None:
            return False, None
        value = None
        found = False
        for a in args:
            try:
                split = re.split(self.val_prefix, a)
            except ValueError:
                return None
            if split[0] == arg:
                found = True
                if has_value and len(split) > 1:
                    value = split[1]
                break
        return found, value
    # endregion
    # endregion

    async def react_to(self, msg: discord.Message, emojis: list) -> None:
        for e in self.bot.emojis:
            if e.name in emojis:
                await msg.add_reaction(e)
