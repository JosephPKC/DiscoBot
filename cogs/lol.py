import re
from enum import Enum
from typing import List, Tuple, Union

import cassiopeia
import datapipelines
import discord
from cassiopeia import data
from cassiopeia import *
from discord.ext import commands

from data import utils

""" Self-contained command module for all things League of Legends.

    All Constant, Mappings, Enumerations, Utility Methods relating to LoL and LoL only will be here.
"""


class Error(Enum):
    REGION_NOT_FOUND = 0
    PLAYER_NOT_FOUND = 1
    MATCHES_NOT_FOUND = 2
    MASTERIES_NOT_FOUND = 3
    RANKS_NOT_FOUND = 4
    INVALID_AMOUNT = 5


class Constant:
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

    REGIONS_LIST = [
        'BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR', 'RU', 'PBE'
    ]


class Converter:
    FROM_LANE_TO_STRING = {
        data.Lane.bot_lane: 'Bottom',
        data.Lane.jungle: 'Jungle',
        data.Lane.mid_lane: 'Middle',
        data.Lane.top_lane: 'Top Lane'
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
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid Command: {}. <:dab:390040479951093771>'.format(ctx.subcommand_passed))

    @lol.command(name='help', aliases=['?', 'commands'])
    async def _help(self, ctx: commands.Context) -> None:
        utils.print_command(ctx.command)
        msg = await ctx.send(content=ctx.author.mention, embed=self.help)
        await self.react_to(msg, ['hellyeah', 'dorawinifred', 'cutegroot', 'dab'])

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

    # endregion

    # region ERROR
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
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
            embed.add_field(name=f'{i + 1}. __**{m.id}:**__',
                            value=f'\t**{result}**\n\t**{Converter.FROM_SEASON_TO_STRING[m.season]}**\n'
                                  f'\t**{Converter.FROM_QUEUE_TO_STRING[m.queue]}**\n'
                                  f'\t**Duration:** {m.duration}\n\t**Champion:** {champion} '
                                  f'{Converter.FROM_LANE_TO_STRING[player.lane]} {role}\n\t'
                                  f'**KDA:** {player.stats.kills} / {player.stats.deaths} / {player.stats.assists}\n'
                                  f'\t**CS:** {player.stats.total_minions_killed}  '
                                  f'**VS:** {player.stats.vision_score}',
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
            cs += player.stats.total_minions_killed
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
        else:
            return ''

    @staticmethod
    def get_op_gg_url(region: str, name: str) -> str:
        name = name.replace(' ', '+')
        return f'http://{region}.op.gg/summoner/userName={name}'

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
