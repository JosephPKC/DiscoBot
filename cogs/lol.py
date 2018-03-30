import re
from enum import Enum
from typing import Any, List, Optional, Tuple, Union
import cassiopeia
import datapipelines
import discord
from cassiopeia import *
from discord.ext import commands

from data import utils

""" LoL Cog
- A self-contained cog that contains commands, data, enumerations, etc relating to LoL.
"""


class Error(Enum):
    """
    Enumeration to hold different types of errors.
    """
    NF_REGION = 0
    NF_PLAYER = 1
    NF_CHAMPION = 2
    NF_LEAGUES = 3
    INV_AMOUNT = 4
    NF_LIVE = 5
    INV_INDEX = 6


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
    Group of Constants.
    """
    # Defaults
    DEFAULT_MATCHES = 20
    DEFAULT_MASTERIES = 25
    DEFAULT_REGION = 'NA'
    DEFAULT_COLOR = 0x18719
    # URIs
    OP_GG_ICON_URL = 'http://opgg-static.akamaized.net/images/logo/l_logo.png'
    # Info
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
    # Lists
    REGIONS_LIST = [
        'BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR', 'RU', 'PBE'
    ]
    # Splits
    SPLIT = 25
    # Constants
    FROM_LANE_TO_STRING = {
        data.Lane.bot_lane: 'Bottom',
        data.Lane.jungle: 'Jungle',
        data.Lane.mid_lane: 'Middle',
        data.Lane.top_lane: 'Top',
        'NONE': ''
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
    async def lol(self, ctx: commands.Context) \
            -> None:
        """
        A command group that houses all commands found here.
        :param ctx: Context of the message.
        :return: None.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid Command: {}. <:dab:390040479951093771>'.format(ctx.subcommand_passed))

    @lol.command(name='help', aliases=['?', 'commands'])
    async def _help(self, ctx: commands.Context) \
            -> None:
        """
        Help Command: Displays each command attached to the LoL cog, and how to use them.
        :param ctx: Context of the message.
        :return: None.
        """
        utils.print_command(ctx.command)
        msg = await ctx.send(content=ctx.author.mention, embed=self.help)
        await self.react_to(msg, ['hellyeah', 'dorawinifred', 'cutegroot', 'dab'])

    @lol.command(name='events', aliases=['history', 'timeline'])
    async def _events(self, ctx: commands.Context, name: str, index: int, region: str=None, *, args: str=None) \
            -> None:
        """
        Events Command: Displays the events of a match of a player. This includes kills, objectives, and items.
        :param ctx: Context of the message.
        :param name: Name of the player.
        :param index: Index of the match, in relation to the player's most recent matches.
        :param region: Region of the player. Default is NA.
        :param args: Extra arguments.
            Items: Enables item events.
            Items Only: Only shows item events.
            Single: Only shows events that the player is involved in.
        :return: None.
        """
        utils.print_command(ctx.command, [name, index, region], args)
        region = self.retrieve_region(region)
        args = self.parse_args(args)
        use_items, _ = self.parse_single_arg(args, ['items', 'i'])
        use_single, _ = self.parse_single_arg(args, ['single', 's'])
        use_items_only, _ = self.parse_single_arg(args, ['itemsonly', 'io'])
        summoner, match = self.retrieve_events(name, index, region)
        await self.display_embed(ctx, ctx.author.mention, self.create_events(ctx.author, match, summoner, use_items,
                                                                             use_single, use_items_only))

    @lol.command(name='live', aliases=['current', 'spectate'])
    async def _live(self, ctx: commands.Context, name: str, region: str=None, *, args: str=None) \
            -> None:
        utils.print_command(ctx.command, [name, region], args)
        region = self.retrieve_region(region)
        summoner, match = self.retrieve_live(name, region)
        await self.display_embed(ctx, ctx.author.mention, self.create_live(ctx.author, match, summoner))

    @lol.command(name='mastery', aliases=['masteries'])
    async def _mastery(self, ctx: commands.Context, name: str, region: str=None, *, args: str=None) \
            -> None:
        utils.print_command(ctx.command, [name, region], args)
        region = self.retrieve_region(region)
        args = self.parse_args(args)
        _, amount = self.parse_single_arg(args, ['amount', 'a'], True)
        amount = self.retrieve_amount(amount, 1, 140, Constant.DEFAULT_MASTERIES)
        _, champion = self.parse_single_arg(args, ['champion', 'c'], True)
        use_reverse, _ = self.parse_single_arg(args, ['reverse', 'r'])
        summoner, mastery = self.retrieve_mastery(name, region, champion)
        await self.display_embed(ctx, ctx.author.mention, self.create_mastery(ctx.author, mastery, summoner, amount,
                                                                              use_reverse))

    @lol.command(name='match', aliases=['game'])
    async def _match(self, ctx: commands.Context, name: str, index: int, region: str=None, *, args: str=None) \
            -> None:
        utils.print_command(ctx.command, [name, index, region], args)
        region = self.retrieve_region(region)
        args = self.parse_args(args)
        use_overview, _ = self.parse_single_arg(args, ['overview', 'o'])
        match = self.retrieve_match(name, index, region)
        await self.display_embed(ctx, ctx.author.mention, self.create_match(ctx.author, match, use_overview))

    @lol.command(name='matches', aliases=['matchlist', 'recent'])
    async def _matches(self, ctx: commands.Context, name: str, region: str=None, *, args: str=None) \
            -> None:
        utils.print_command(ctx.command, [name, region], args)
        region = self.retrieve_region(region)
        args = self.parse_args(args)
        _, amount = self.parse_single_arg(args, ['amount', 'a'], True)
        amount = self.retrieve_amount(amount, 1, 50, 20)
        summoner, matches = self.retrieve_matches(name, region, amount)
        await self.display_embed(ctx, ctx.author.mention, self.create_matches(ctx.author, matches, summoner))

    @lol.command(name='player', aliases=['profile', 'summoner'])
    async def _player(self, ctx: commands.Context, name: str, region: str=None, *, args: str=None) \
            -> None:
        utils.print_command(ctx.command, [name, region], args)
        region = self.retrieve_region(region)
        summoner, matches, masteries, leagues, live = self.retrieve_player(name, region)
        await self.display_embed(ctx, ctx.author.mention,
                                 self.create_player(ctx.author, live, leagues, masteries, matches, summoner))
    # endregion

    # region HELP
    @staticmethod
    def create_help() \
            -> discord.Embed:
        """
        Create Help Embed: Stub for now.
        :return:
        """
        return discord.Embed(title='Helps')

    # endregion

    # region EVENTS
    def retrieve_events(self, name: str, index: int, region: str) \
            -> Tuple[cassiopeia.Summoner, cassiopeia.Match]:
        """
        Retrieve Events Data: Retrieves the summoner and the match.
        :param name: Name of the player.
        :param index: Index in the recent matches.
        :param region: Region of the player.
        :return: Summoner, Match
        """
        try:
            summoner = cassiopeia.get_summoner(name=name, region=region.upper())
            matches = cassiopeia.get_match_history(summoner=summoner, begin_index=index - 1, end_index=index)
            return summoner, matches[summoner.name]
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.NF_PLAYER, name, region))

    def create_events(self, author: str, match: cassiopeia.Match, summoner: cassiopeia.Summoner, use_items: bool,
                      use_single: bool, use_items_only: bool) \
            -> List[discord.Embed]:
        """
        Create Events Embed: Notably a list of timestamps and events.
        :param ctx: Context of the message.
        :param match: Match data.
        :param summoner: Summoner data.
        :param use_items: Optional flag.
        :param use_single: Optional flag.
        :param use_items_only: Optional flag.
        :return: Embed list.
        """
        embeds = []
        # Preliminary stuff
        participants = match.blue_team.participants + match.red_team.participants
        pid = None
        cid = None
        for p in participants:
            if p.summoner.name == summoner.name:
                pid = p.id
                cid = p.champion.key
                break
        champion = self.get_champion_name_in_english(cid)
        types = ['CHAMPION_KILL', 'BUILDING_KILL', 'ELITE_MONSTER_KILL']
        items = ['ITEM_PURCHASED', 'ITEM_SOLD', 'ITEM_UNDO']
        if use_items:
            types += items
        if use_items_only:
            types = items
        # Embed
        embed = self.build_events_embed(author, match, summoner, champion)
        events = self.build_events_event_list(match, types, items, use_single, pid)

        # Parse events
        def name_gen(i, o): return f'**{self.get_time_stamp_string(o[0].timestamp)}.**\n'

        def value_gen(i, o): return self.build_events_events(o[0], participants, o[1], use_single, pid)

        def inline_gen(i, o): return False

        def embed_gen(): return self.build_events_embed(author, match, summoner, champion)
        return utils.add_to_embed(current_embed=embed, split=Constant.SPLIT, embeds_list=embeds, item_list=events,
                                  field_name_gen=name_gen, field_value_gen=value_gen, field_inline_gen=inline_gen,
                                  embed_gen=embed_gen)
    
    def build_events_embed(self, author: str, match: cassiopeia.Match, summoner: cassiopeia.Summoner, champion: str) \
            -> discord.Embed:
        return utils.create_embed_template(
            description=f'Timeline | Match __**{match.id}**__ in __**{match.region.value}**__.\n'
                        f'__**{summoner.name}**__ played __**{champion}**__.',
            color=Constant.DEFAULT_COLOR, requester=author, author=f'Match History: {match.id}',
            author_url=self.get_match_history_url(match.region.value, match.platform.value, match.id)
        )

    def build_events_event_list(self, match: cassiopeia.Match, types: List[str], items: List[str], use_single: bool,
                                pid: int) \
            -> List[Tuple[core.match.Event, Optional[str]]]:
        events = []
        for f in match.timeline.frames:
            for e in f.events:
                if e.type in types:
                    if use_single:
                        if e.type == 'CHAMPION_KILL':
                            # Can be the killer, assist, or victim
                            if pid == e.killer_id:
                                events.append([e, 'KILLER'])
                            elif pid == e.victim_id:
                                events.append([e, 'VICTIM'])
                            elif pid in e.assisting_participants:
                                events.append([e, 'ASSIST'])
                        elif e.type == 'BUILDING_KILL':
                            # Can be the killer or assist
                            if pid == e.killer_id:
                                events.append([e, 'KILLER'])
                            elif pid in e.assisting_participants:
                                events.append([e, 'ASSIST'])
                        elif e.type == 'ELITE_MONSTER_KILL':
                            # Can be the killer
                            if pid == e.killer_id:
                                events.append([e, 'KILLER'])
                        elif e.type in items:
                            if pid == e.participant_id:
                                events.append([e, None])
                        else:
                            events.append([e, None])
                    else:
                        events.append([e, None])
        return events

    def build_events_events(self, event: core.match.Event, participants: List[core.match.Participant], how: str,
                            use_single: bool, pid: int) \
            -> str:
        # TODO: Add events for Ascension, Poro King
        if event.type == 'CHAMPION_KILL':
            return self.build_events_champion_kill(event, participants, how, use_single, pid)
        elif event.type == 'BUILDING_KILL':
            return self.build_events_building_kill(event, participants, how, use_single, pid)
        elif event.type == 'ELITE_MONSTER_KILL':
            return self.build_events_elite_monster_kill(event, participants, use_single)
        elif event.type == 'ITEM_PURCHASED':
            return self.build_events_item_purchased(event, participants, use_single)
        elif event.type == 'ITEM_SOLD':
            return self.build_events_item_sold(event, participants, use_single)
        elif event.type == 'ITEM_UNDO':
            return self.build_events_item_undo(event, participants, use_single)
        else:
            return ''

    def build_events_champion_kill(self, event: core.match.Event, participants: List[core.match.Participant], how: str,
                                   use_single: bool, pid: int) \
            -> str:
        # Killer
        killer = participants[event.killer_id - 1]
        team = killer.side.value // 100
        killer = f'{self.get_champion_name_in_english(killer.champion.key)} ({killer.summoner.name})'
        # Victim
        victim = participants[event.victim_id - 1]
        victim = f'{self.get_champion_name_in_english(victim.champion.key)} ({victim.summoner.name})'
        if use_single:
            if how == 'KILLER':
                string = f'Slayed **{victim}**.\n'
            elif how == 'VICTIM':
                string = f'Slain by **{killer}**.\n'
            else:
                string = f'Helped **{killer}** slay **{victim}**.\n'
            if event.assisting_participants:
                if how == 'ASSIST' and len(event.assisting_participants) > 1:
                    string += '\tAlso assisted by:\n'
                elif how != 'ASSIST':
                    string += '\tAssisted by:\n'
            for a in event.assisting_participants:
                if how == 'ASSIST' and a == pid:
                    continue
                assist = participants[a - 1]
                string += f'\t\t**{self.get_champion_name_in_english(assist.champion.key)} ({assist.summoner.name})**\n'
        else:
            string = f'**Team {team} - {killer}** has slain **{victim}**.\n'
            if event.assisting_participants:
                string += '\tAssisted by:\n'
            for a in event.assisting_participants:
                assist = participants[a - 1]
                string += f'\t\t**{self.get_champion_name_in_english(assist.champion.key)} ({assist.summoner.name})**\n'
        return string

    def build_events_building_kill(self, event: core.match.Event, participants: List[core.match.Participant], how: str,
                                   use_single: bool, pid: int) \
            -> str:
        # Killer
        killer = participants[event.killer_id - 1]
        team = killer.side.value // 100
        killer = f'{self.get_champion_name_in_english(killer.champion.key)} ({killer.summoner.name})'
        # Until timeline's event.lane_type is fixed
        # if event.lane_type == 'MID_LANE':
        #     lane = 'Middle'
        # elif event.lane_type == 'BOT_LANE':
        #     lane = 'Bottom'
        # elif event.lane_type == 'TOP_LANE':
        #     lane = 'Top'
        # else:
        #     lane = None
        # print(lane)
        # Victim
        if event.tower_type == 'NEXUS_TURRET':
            victim = 'Nexus Tower'
        elif event.building_type == 'INHIBITOR_BUILDING':
            victim = 'Inhibitor'
        elif event.tower_type == 'INNER_TURRET':
            victim = 'Inner Tower'
        elif event.tower_type == 'OUTER_TURRET':
            victim = 'Outer Tower'
        elif event.tower_type == 'BASE_TURRET':
            victim = 'Base Tower'

        if use_single:
            if how == 'KILLER':
                string = f'Destroyed the **{victim}**.\n'
            else:
                string = f'Helped **{killer}** destroy the **{victim}**.\n'
            if event.assisting_participants:
                if how == 'ASSIST' and len(event.assisting_participants) > 1:
                    string += '\tAlso assisted by:\n'
                elif how != 'ASSIST':
                    string += '\tAssisted by:\n'
            for a in event.assisting_participants:
                if how == 'ASSIST' and a == pid:
                    continue
                assist = participants[a - 1]
                string += f'\t\t**{self.get_champion_name_in_english(assist.champion.key)} ({assist.summoner.name})**\n'
        else:
            string = f'**Team {team} - {killer}** has destroyed the **{victim}**.\n'
            if event.assisting_participants:
                string += '\tAssisted by:\n'
            for a in event.assisting_participants:
                assist = participants[a - 1]
                string += f'\t\t**{self.get_champion_name_in_english(assist.champion.key)} ({assist.summoner.name})**\n'
        return string

    def build_events_elite_monster_kill(self, event: core.match.Event, participants: List[core.match.Participant],
                                        use_single: bool) \
            -> str:
        # Killer
        killer = participants[event.killer_id - 1]
        team = killer.side.value // 100
        killer = f'{self.get_champion_name_in_english(killer.champion.key)} ({killer.summoner.name})'
        # Victim
        if event.monster_type == 'BARON_NASHOR':
            victim = 'Baron'
        elif event.monster_type == 'RIFTHERALD':
            victim = 'Rift Herald'
        elif event.monster_type == 'VILE_MAW':
            victim = 'Vile\'Maw'
        elif event.monster_type == 'DRAGON':
            victim = 'Dragon'
            # Monster Sub Type is bugged
            # if event.monster_sub_type == 'WATER_DRAGON':
            #     victim = 'Ocean Dragon'
            # elif event.monster_sub_type == 'AIR_DRAGON':
            #     victim = 'Cloud Dragon'
            # elif event.monster_sub_type == 'EARTH_DRAGON':
            #     victim = 'Mountain Dragon'
            # elif event.monster_sub_type == 'FIRE_DRAGON':
            #     victim = 'Infernal Dragon'
            # elif event.monster_sub_type == 'ELDER_DRAGON':
            #     victim = 'Elder Dragon'
        if use_single:
            return f'Slayed the **{victim}**.\n'
        else:
            return f'**Team {team} - {killer}** has slain the **{victim}**.\n'

    def build_events_item_purchased(self, event: core.match.Event, participants: List[core.match.Participant],
                                    use_single: bool) \
            -> str:
        if use_single:
            return f'Bought **{self.get_item_name(event.item_id)}**.'
        # Buyer
        buyer = participants[event.participant_id - 1]
        buyer = f'{self.get_champion_name_in_english(buyer.champion.key)} ({buyer.summoner.name})'
        return f'**{buyer}** has bought **{self.get_item_name(event.item_id)}**.'

    def build_events_item_sold(self, event: core.match.Event, participants: List[core.match.Participant],
                                    use_single: bool) \
            -> str:
        if use_single:
            return f'Sold **{self.get_item_name(event.item_id)}**.'
        # Buyer
        buyer = participants[event.participant_id - 1]
        buyer = f'{self.get_champion_name_in_english(buyer.champion.key)} ({buyer.summoner.name})'
        return f'**{buyer}** has sold **{self.get_item_name(event.item_id)}**.'

    def build_events_item_undo(self, event: core.match.Event, participants: List[core.match.Participant],
                                    use_single: bool) \
            -> str:
        if use_single:
            return f'Undid **{self.get_item_name(event.before_id)}**.'
        # Buyer
        buyer = participants[event.participant_id - 1]
        buyer = f'{self.get_champion_name_in_english(buyer.champion.key)} ({buyer.summoner.name})'
        return f'**{buyer}** has undone **{self.get_item_name(event.before_id)}**.'
    # endregion

    # region LIVE
    def retrieve_live(self, name: str, region: str) \
            -> Tuple[cassiopeia.Summoner, cassiopeia.CurrentMatch]:
        # Get Summoner
        try:
            summoner = cassiopeia.get_summoner(name=name, region=region.upper())
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.NF_PLAYER, name, region))
        # Get Live Match
        try:
            match = cassiopeia.get_current_match(summoner=summoner, region=region.upper())
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.NF_LIVE, name, region))
        return summoner, match

    def create_live(self, author: str, match: cassiopeia.CurrentMatch, summoner: cassiopeia.Summoner) \
            -> List[discord.Embed]:
        embeds = []
        embed = self.build_live_embed(author, match, summoner)
        for t in [match.blue_team, match.red_team]:
            for p in t.participants:
                team = 'Blue' if p.side.value == 100 else 'Red'
                embed.add_field(name=f' {team} Team: {p.summoner.name}', value=self.build_live_players(p), inline=False)
        embeds.append(embed)
        return embeds

    def build_live_embed(self, author: str, match: cassiopeia.CurrentMatch, summoner: cassiopeia.Summoner) \
            -> discord.Embed:
        return utils.create_embed_template(
            description=f'**{Constant.FROM_QUEUE_TO_STRING[match.queue]}** | {match.duration}',
            color=Constant.DEFAULT_COLOR, requester=author, author=f'Live Match | {summoner.name}',
            author_url=self.get_live_match_url(match.region.value, summoner.name)
        )

    def build_live_players(self, participant: core.spectator.Participant) \
            -> str:
        string = f'**Is Playing ** {self.get_champion_name_in_english(participant.champion.key)}\n'
        # string += f'**Previously:** {p.rank_last_season.value}\n'
        string += f'**Has ** {participant.summoner_spell_d.name} {participant.summoner_spell_f.name}\n'
        for i, r in enumerate(list(participant.runes)):
            rune = cassiopeia.get_runes('NA')[r.id]
            if i == 0:
                string += f'**Primary** {rune.path.value.capitalize()}\n'
            elif i == 4:
                string += f'**Secondary** {rune.path.value.capitalize()}\n'
            keystone = '**' if rune.is_keystone else ''
            string += f'\t{keystone}{rune.name}{keystone}\n'
        return string
    # endregion

    # region MASTERY
    def retrieve_mastery(self, name: str, region: str, champion: str=None) \
            -> Tuple[cassiopeia.Summoner, Union[cassiopeia.ChampionMastery, cassiopeia.ChampionMasteries]]:
        try:
            summoner = cassiopeia.get_summoner(name=name, region=region.upper())
            if champion is None:
                return summoner, cassiopeia.get_champion_masteries(summoner=summoner, region=summoner.region)
            else:
                return summoner, cassiopeia.get_champion_mastery(summoner=summoner, champion=champion.capitalize(),
                                                                 region=summoner.region)
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.NF_PLAYER, name, region))

    def create_mastery(self, author: str,  mastery: Union[cassiopeia.ChampionMastery, cassiopeia.ChampionMasteries],
                       summoner: cassiopeia.Summoner, amount: int, use_reverse: bool) \
            -> List[discord.Embed]:
        masteries = [mastery] if isinstance(mastery, cassiopeia.ChampionMastery) else list(mastery)
        if use_reverse:
            masteries.reverse()
        embeds = []
        embed = self.build_masteries_embed(author, masteries, summoner)

        # Add masteries
        def name_gen(i, o): return f'{o.champion.name}'

        def value_gen(i, o): return self.build_masteries_champion(o)

        def inline_gen(i, o): return False

        def embed_gen(): return self.build_masteries_embed(author, masteries, summoner)
        return utils.add_to_embed(current_embed=embed, split=Constant.SPLIT, embeds_list=embeds, item_list=masteries[:amount],
                                  field_name_gen=name_gen, field_value_gen=value_gen, field_inline_gen=inline_gen,
                                  embed_gen=embed_gen)

    def build_masteries_embed(self, author: str, masteries: List[cassiopeia.ChampionMastery],
                              summoner: cassiopeia.Summoner) \
            -> discord.Embed:
        return utils.create_embed_template(
            description=f'Masteries | __**{summoner.name}**__ in __**{summoner.region.value}**__.',
            color=Constant.DEFAULT_COLOR, requester=author, author=f'Match History: {summoner.name}',
            author_url=self.get_op_gg_url(summoner.region.value, summoner.name), thumbnail=summoner.profile_icon.url,
            image=(masteries[0].champion.image.url if len(masteries) == 1 else None)
        )

    def build_masteries_champion(self, mastery: cassiopeia.ChampionMastery) \
            -> str:
        string = f'**Level** {mastery.level}\n' \
                 f'**Points** {mastery.points}\n' \
                 f'\t**Since Last Level** {mastery.points_since_last_level}\n' \
                 f'\t**Until Next Level** {mastery.points_until_next_level}\n'
        if mastery.level > 4:
            string += f'**Tokens** {mastery.tokens}\n'
        if mastery.chest_granted:
            string +='**Got Chest.**\n'
        return string
    # endregion

    # region MATCH
    def retrieve_match(self, name: str, index: int, region: str) \
            -> cassiopeia.Match:
        try:
            summoner = cassiopeia.get_summoner(name=name, region=region.upper())
            matches = cassiopeia.get_match_history(summoner=summoner, begin_index=index - 1, end_index=index)
            return list(matches)[0]
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.NF_PLAYER, name, region))

    def create_match(self, author: str, match: cassiopeia.Match, use_overview: bool) \
            -> List[discord.Embed]:
        embeds = []
        embed = self.build_match_embed(author, match)
        queue = Constant.QUEUE_INFO[match.queue]
        # Add core
        embed.add_field(name='__Core Info:__',
                        value=f'**{Constant.FROM_SEASON_TO_STRING[match.season]}**\n'
                              f'**{Constant.FROM_QUEUE_TO_STRING[match.queue]}**\n'
                              f'**Duration:** {match.duration}\n',
                        inline=False)
        # Add teams
        for t in [match.blue_team, match.red_team]:
            embed.add_field(name=f'__TEAM {t.side.value // 100}__',
                            value=self.build_match_team(queue, t),
                            inline=True)
        embeds.append(embed)
        # Add players
        for t in [match.blue_team, match.red_team]:
            for p in t.participants:
                embed = self.build_match_team_embed(author, p, t)
                stats = p.stats
                # Add overview + items
                embed.add_field(name='__OVERVIEW:__', value=self.build_match_player_overview(queue, p))
                # Add core stats
                embed.add_field(name='__BASIC:__', value=self.build_match_player_core(queue, stats))
                # Add advanced stats
                if not use_overview:
                    embed.add_field(name='__ADVANCED:__', value=self.build_match_player_advanced(queue, stats))
                # Add runes
                embed.add_field(name='__RUNES:__', value=self.build_match_player_runes(p))
                embeds.append(embed)
        return embeds

    def build_match_embed(self, author: str, match: cassiopeia.Match) \
            -> discord.Embed:
        return utils.create_embed_template(
            description=f'Overview | Match __**{match.id}**__ in __**{match.region.value}**__.',
            color=Constant.DEFAULT_COLOR, requester=author, author=f'Match History: {match.id}',
            author_url=self.get_match_history_url(match.region.value, match.platform.value, match.id)
        )

    def build_match_team_embed(self, author: str, participant: core.match.Participant, team: core.match.Team) \
            -> discord.Embed:
        return utils.create_embed_template(
                    description=f'__**Team {team.side.value // 100}**__ |  __**{participant.summoner.name}**__.',
                    color=Constant.DEFAULT_COLOR, requester=author, author=f'OP.GG: {participant.summoner.name}',
                    author_url = self.get_op_gg_url(participant.summoner.region.value, participant.summoner.name),
                    icon_url = Constant.OP_GG_ICON_URL, thumbnail=participant.summoner.profile_icon.url
                )
    
    def build_match_team(self, queue: QueueInfo, team: core.match.Team) \
            -> str:
        result = 'VICTORY' if team.win else 'DEFEAT'
        string = f'**{result}**\n'
        if queue.has_towers:
            string += f'**Towers:** {team.tower_kills}'
            if team.first_tower:
                string += '  Got **First Tower.**'
            string += f'\n**Inhibitors:** {team.inhibitor_kills}'
            if team.first_inhibitor:
                string += '  Got **First Inhibitor.**'
            string += '\n'
        if queue.has_dragons:
            string += f'**Dragons:** {team.dragon_kills}'
            if team.first_dragon:
                string += '  Got **First Dragon.**'
            string += '\n'
        if queue.has_barons:
            string += f'**Barons:** {team.baron_kills}'
            if team.first_baron:
                string += '  Got **First Baron.**'
            string += '\n'
        if queue.has_heralds:
            string += f'**Herald:** {team.rift_herald_kills}'
            if team.first_rift_herald:
                string += '  Got **First Herald.**'
            string += '\n'
        if queue.has_vilemaws:
            string += f'**Vile\'Maws:** {team.vilemaw_kills}\n'
        if team.first_blood:
            string += 'Got **First Blood.**\n'
        # Bans are bugged
        # if team.bans:
        #     string += '**BANS:**\n'
        #     for i, b in enumerate(team.bans):
        #         champion = cassiopeia.get_champion(b.key, 'NA')
        #         champion = champion.name if champion is not None else 'None'
        #         string += f'{i + 1}. {champion}\n'
        return string

    def build_match_player_overview(self, queue: QueueInfo, participant: core.match.Participant) \
            -> str:
        stats = participant.stats
        string = f'**Played** {self.get_champion_name_in_english(participant.champion.key)} '
        if queue.has_lanes:
            string += self.get_role_string(participant.lane, participant.role)
        string += f'\n**Previously** {participant.rank_last_season.value}\n' \
                  f'**Had** {participant.summoner_spell_d.name} {participant.summoner_spell_f.name}\n' \
                  f'**Final Build:**\n'
        for i, j in enumerate(stats.items):
            item = cassiopeia.get_items('NA')[j.id].name if j is not None else 'None'
            string += f'{i + 1}. {item}\n'
        return string

    def build_match_player_core(self, queue: QueueInfo, stats: core.match.ParticipantStats) \
            -> str:
        string = f'**KDA:** {stats.kills} / {stats.deaths} / {stats.assists}  ' \
                 f'**Level:** {stats.level}\n'
        if queue.has_score:
            string += f'**Score:** {stats.total_player_score}\n' \
                      f'\t**Combat:** {stats.combat_player_score}\n' \
                      f'\t**Objective:** {stats.objective_player_score}\n'
        string += f'**CS:** {self.get_total_cs(queue, stats.total_minions_killed, stats.neutral_minions_killed)}'
        if queue.has_monsters:
            string += f'  **Monsters:** {stats.neutral_minions_killed}\n' \
                      f'\t**In Team Jungle:** {stats.neutral_minions_killed_team_jungle}\n' \
                      f'\t**In Enemy Jungle:** {stats.neutral_minions_killed_enemy_jungle}\n'
        else:
            string += '\n'
        if queue.has_vision:
            string += f'**Vision Score:** {stats.vision_score}\n' \
                      f'\t**Control Wards:** {stats.vision_wards_bought_in_game}\n' \
                      f'\t**Wards Placed:** {stats.wards_placed}\n' \
                      f'\t**Wards Killed:** {stats.wards_killed}\n'
        string += f'**Crowd Control:** {stats.total_time_crowd_control_dealt}\n' \
                  f'**Gold Spent / Earned:** {stats.gold_spent} / {stats.gold_earned}\n'
        return string

    def build_match_player_advanced(self, queue: QueueInfo, stats: core.match.ParticipantStats) \
            -> str:
        string = f'**Killing Sprees:** {stats.killing_sprees}  **Largest:** {stats.largest_killing_spree}\n' \
                 f'**Largest Multi Kill:** {stats.largest_multi_kill}\n' \
                 f'\t**Double Kills:** {stats.double_kills}\n' \
                 f'\t**Triple Kills:** {stats.triple_kills}\n' \
                 f'\t**Quadra Kills:** {stats.quadra_kills}\n' \
                 f'\t**Penta Kills:** {stats.penta_kills}\n' \
                 f'\t**Unreal Kills:** {stats.unreal_kills}\n'
        if stats.first_blood_kill or stats.first_blood_assist:
            string += '\tGot **First Blood**.\n'
        string += f'**Total Damage Dealt:** {stats.total_damage_dealt}\n' \
                  f'\t**Magical:** {stats.magic_damage_dealt}\n' \
                  f'\t**Physical:** {stats.physical_damage_dealt}\n' \
                  f'\t**True:** {stats.true_damage_dealt}\n' \
                  f'**Total To Champions:** {stats.total_damage_dealt_to_champions}\n' \
                  f'\t**Magical:** {stats.magic_damage_dealt_to_champions}\n' \
                  f'\t**Physical:** {stats.physical_damage_dealt_to_champions}\n' \
                  f'\t**True:** {stats.true_damage_dealt_to_champions}\n' \
                  f'**Total Damage Taken:** {stats.total_damage_taken}\n' \
                  f'\t**Magical:** {stats.magical_damage_taken}\n' \
                  f'\t**Physical:** {stats.physical_damage_taken}\n' \
                  f'\t**True:** {stats.true_damage_taken}\n' \
                  f'**Damage Self Mitigated:** {stats.damage_self_mitigated}\n' \
                  f'**Total Healing:** {stats.total_heal}\n' \
                  f'**Largest Critical Strike:** {stats.largest_critical_strike}\n' \
                  f'**Damage to Objectives:** {stats.damage_dealt_to_objectives}\n'
        if queue.has_towers:
            string += f'\t**Damage to Towers:** {stats.damage_dealt_to_turrets}\n' \
                      f'\t**Tower Kills:** {stats.turret_kills}'
            if stats.first_tower_kill or stats.first_tower_assist:
                string += '  Got **First Tower**.'
            string += f'\n\t**Inhibitor Kills:** {stats.inhibitor_kills}'
            if stats.first_inhibitor_kill or stats.first_inhibitor_assist:
                string += '  Got **First Inhibitor**.'
            string += '\n'
        return string

    def build_match_player_runes(self, participant: core.match.Participant) \
            -> str:
        runes = list(participant.runes)
        string = f'**Primary** {runes[0].path.value}\n'
        for r in runes[:4]:
            if r.is_keystone:
                rune = f'**{r.name}**'
            else:
                rune = f'{r.name}'
            string += f'\t{rune}\n'
        string += f'**Secondary** {runes[4].path.value}\n'
        for r in runes[4:]:
            string += f'\t{r.name}\n'
        return string
    # endregion

    # region MATCHES
    def retrieve_matches(self, name: str, region: str, amount: int) \
            -> Tuple[cassiopeia.Summoner, cassiopeia.MatchHistory]:
        try:
            summoner = cassiopeia.get_summoner(name=name, region=region.upper())
            matches = cassiopeia.get_match_history(summoner=summoner, end_index=amount)
            return summoner, matches
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.NF_PLAYER, name, region))

    def create_matches(self, author: str, matches: cassiopeia.MatchHistory, summoner: cassiopeia.Summoner) \
            -> List[discord.Embed]:
        embeds = []
        embed = self.build_matches_embed(author, matches, summoner)

        # Add basics
        def name_gen(i, o): return f'{i + 1}. __**{o.id}:**__'

        def value_gen(i, o): return self.build_matches_stats(o, summoner)

        def inline_gen(i, o): return False

        def embed_gen(): return self.build_matches_embed(author, matches, summoner)
        return utils.add_to_embed(current_embed=embed, split=Constant.SPLIT, embeds_list=embeds, item_list=matches,
                                  field_name_gen=name_gen, field_value_gen=value_gen, field_inline_gen=inline_gen,
                                  embed_gen=embed_gen)

    def build_matches_embed(self, author: str, matches: cassiopeia.MatchHistory, summoner: cassiopeia.Summoner) \
            -> discord.Embed:
        return utils.create_embed_template(
            description=f'{len(matches)} Recent Matches | '
                        f'__**{summoner.name}**__ in __**{summoner.region.value}**__.',
            color=Constant.DEFAULT_COLOR, requester=author, thumbnail=summoner.profile_icon.url,
            author=f'OP.GG: {summoner.name}', author_url=self.get_op_gg_url(summoner.region.value, summoner.name),
            icon_url=Constant.OP_GG_ICON_URL
        )

    def build_matches_stats(self, match: cassiopeia.Match, summoner: cassiopeia.Summoner) \
            -> str:
        player = match.participants[summoner]
        stats = player.stats
        return f'\t**{self.get_result_string(player.team.win)}**\n' \
               f'\t**{Constant.FROM_SEASON_TO_STRING[match.season]}**\n' \
               f'\t**{Constant.FROM_QUEUE_TO_STRING[match.queue]}**\n\t**Duration:** {match.duration}\n' \
               f'\t**Played** {self.get_champion_name_in_english(player.champion.key)}\n' \
               f'\t**KDA:** {stats.kills} / {stats.deaths} / {stats.assists}\n' \
               f'\t**CS:** {self.get_total_cs(match.queue, stats.total_minions_killed, stats.neutral_minions_killed)}' \
               f'  {self.get_vs_string(match.queue, stats)}'

    # endregion

    # region PLAYER
    def retrieve_player(self, name: str, region: str) \
            -> Tuple[cassiopeia.Summoner, cassiopeia.MatchHistory, cassiopeia.ChampionMasteries,
                     cassiopeia.LeagueEntries, cassiopeia.CurrentMatch]:
        # Get summoner
        try:
            summoner = cassiopeia.get_summoner(name=name, region=region.upper())
            matches = cassiopeia.get_match_history(summoner=summoner, region=summoner.region,
                                                   end_index=Constant.DEFAULT_MATCHES)
            masteries = cassiopeia.get_champion_masteries(summoner=summoner, region=summoner.region)
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.NF_PLAYER, name, region))
        try:
            live = cassiopeia.get_current_match(summoner=summoner, region=summoner.region)
        except datapipelines.NotFoundError:
            live = None
        try:
            leagues = cassiopeia.get_league_positions(summoner=summoner, region=summoner.region)
            return summoner, matches, masteries, leagues, live
        except datapipelines.NotFoundError:
            raise commands.UserInputError(self.get_error_message(Error.NF_LEAGUES, name, region))

    def create_player(self, author: str, live: cassiopeia.CurrentMatch, leagues: cassiopeia.LeagueEntries,
                      masteries: cassiopeia.ChampionMasteries, matches: cassiopeia.MatchHistory,
                      summoner: cassiopeia.Summoner) \
            -> List[discord.Embed]:
        embed = self.build_player_embed(author, summoner)
        # Add basic
        embed.add_field(name='__Core:__', value=f'**Level:** {summoner.level}', inline=False)
        # Add recent games
        embed.add_field(name=f'__Recent {len(matches)} Games:__', value=self.build_player_stats(matches, summoner))
        # Add masteries
        embed.add_field(name=f'__Top {len(list(masteries)[:5])} Champions:__',
                        value=self.build_player_masteries_string(masteries))
        # Add leagues
        for l in leagues:
            embed.add_field(name=f'__{utils.get_sanitized_value(l.queue.value)}:__', value=self.build_player_ranks(l))
        # Add live
        embed.add_field(name='__**Live Match**__', value=self.build_player_live(live, summoner), inline=False)
        return [embed]

    def build_player_embed(self, author: str, summoner: cassiopeia.Summoner) \
            -> discord.Embed:
        return utils.create_embed_template(
            description=f'Overview | __**{summoner.name}**__ in __**{summoner.region.value}**__.',
            color=Constant.DEFAULT_COLOR, requester=author, thumbnail=summoner.profile_icon.url,
            author=f'OP.GG: {summoner.name}', author_url=self.get_op_gg_url(summoner.region.value, summoner.name),
            icon_url=Constant.OP_GG_ICON_URL
        )

    def build_player_stats(self, matches: cassiopeia.MatchHistory, summoner: cassiopeia.Summoner) \
            -> str:
        games, wins, kills, deaths, assists, vision, cs = len(matches), 0, 0, 0, 0, 0, 0
        for m in matches:
            player = m.participants[summoner]
            stats = player.stats
            if player.team.win:
                wins += 1
            kills += stats.kills
            deaths += stats.deaths
            assists += stats.assists
            vision += stats.vision_score
            cs += self.get_total_cs(m.queue, stats.total_minions_killed, stats.neutral_minions_killed)
        losses = games - wins
        if games > 0:
            kills /= games
            deaths /= games
            assists /= games
            vision /= games
            cs /= games
        return f'**W/L:** {wins}W / {losses}L\n**Win Rate:** {self.get_win_rate(wins, losses):.2f}%\n' \
               f'**KDA:** {kills:.2f} / {deaths:.2f} / {assists: .2f}  ' \
               f'**R:** {self.get_kda(kills, deaths, assists):.2f}\n' \
               f'**CS:** {cs:.2f}  **VS:** {vision:.2f}' \

    def build_player_masteries_string(self, masteries: cassiopeia.ChampionMasteries) \
            -> str:
        top_5 = list(masteries)[:5]
        if len(top_5) < 1:
            return 'No champions mastered.'
        string = ''
        for i, m in enumerate(top_5):
            string += f'{i + 1}. **{self.get_champion_name_in_english(m.champion.key)}** ' \
                      f'(**{m.level}**) {m.points} pts.\n'
        return string

    def build_player_ranks(self, league: core.league.LeagueEntry) \
            -> str:
        win_rate = self.get_win_rate(league.wins, league.losses)
        ranked_string = f'**Name:** {league.name}\n**Rank:** {league.tier.value} {league.division.value}\n' \
                        f'**W/L:** {league.wins}W / {league.losses}L' \
                        f'  **Win Rate:** {win_rate:.2f}%\n**LP:** {league.league_points}\n'
        if league.fresh_blood:
            ranked_string += 'Fresh Blood. '
        if league.hot_streak:
            ranked_string += 'Hot Streak. '
        if league.veteran:
            ranked_string += 'Veteran. '
        return ranked_string

    def build_player_live(self, live: cassiopeia.CurrentMatch, summoner: cassiopeia.Summoner) \
            -> str:
        if live is None:
            return f'Not currently playing.'
        else:
            player = None
            for p in live.participants:
                if p.summoner.name == summoner.name:
                    player = p
                    break
            return f'Playing **{self.get_champion_name_in_english(player.champion.key)}** in ' \
                   f'**{Constant.FROM_QUEUE_TO_STRING[live.queue]}** | **{live.duration}**'
    # endregion

    # region DISPLAYS
    @staticmethod
    async def display_embed(ctx: commands.Context, content: str=None, embeds: list=None) \
            -> None:
        for i, e in enumerate(embeds):
            if i == 0:
                await ctx.send(content=content, embed=e)
            else:
                await ctx.send(embed=e)

    # endregion

    # region ERROR
    @staticmethod
    async def on_command_error(ctx: commands.Context, error: commands.CommandError) \
            -> None:
        if isinstance(error, commands.MissingRequiredArgument):
            splits = re.split(' ', error.__str__())
            string = f'**{splits[0]}**'
            await ctx.send(' '.join([string] + splits[1:]))
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error)
        elif isinstance(error, commands.UserInputError):
            await ctx.send(error)
        # elif isinstance(error, commands.CommandInvokeError):
        #     await ctx.send('403: Forbidden.')
        else:
            raise error
    # endregion

    # region GETTERS
    @staticmethod
    def get_error_message(error_type: Error, *args) \
            -> str:
        if error_type == Error.NF_REGION:
            return f'**{args[0]}** not found.'
        elif error_type == Error.NF_PLAYER:
            return f'**{args[0]}** not found in **{args[1]}**.'
        elif error_type == Error.NF_LEAGUES:
            return f'Ranks not found for **{args[0]}** in **{args[1]}**.'
        elif error_type == Error.INV_AMOUNT:
            return f'Amount must be an integer between **{args[0]}** and **{args[1]}**.'
        elif error_type == Error.NF_LIVE:
            return f'**{args[0]}** in **{args[1]}** not in game.'
        else:
            return ''
        
    @staticmethod
    def get_champion_name_in_english(key: Union[str, int]) \
            -> str:
        return cassiopeia.get_champion(key, 'NA').name

    @staticmethod
    def get_item_name(id: int) \
        -> str:
        return cassiopeia.get_items('NA')[id].name

    @staticmethod
    def get_rune(id: int) \
            -> cassiopeia.Rune:
        return cassiopeia.get_runes('NA')[id]

    @staticmethod
    def get_role_name(queue: cassiopeia.Queue, role: data.Role) \
            -> str:
        # if Constant.QUEUE_INFO[queue].has_lanes:
        #     if role is None:
        #         return 'Jungle'
        #     elif role is data.Role.
        return Constant.FROM_ROLE_TO_STRING[role] if role is not None and Constant.QUEUE_INFO[queue].has_lanes else ' '

    @staticmethod
    def get_role_string(lane: data.Lane, role: data.Role):
        role = Constant.FROM_ROLE_TO_STRING[role] if role is not None else ' '
        if role == 'Solo' or role == 'Duo' or role == ' ':
            return f'{Constant.FROM_LANE_TO_STRING[lane]}'
        else:
            return f'{role}'

    @staticmethod
    def get_result_string(win: bool) \
            -> str:
        return 'VICTORY' if win else 'DEFEAT'

    @staticmethod
    def get_vs_string(queue: cassiopeia.Queue, stats: core.match.ParticipantStats) \
            -> str:
        return f'**VS:** {stats.vision_score}' if Constant.QUEUE_INFO[queue].has_vision else ''

    def get_time_stamp_string(self, time):
        timestamp = self.get_time_stamp(time)
        return f'{timestamp[0]}:{timestamp[1]:02d}'

    @staticmethod
    def get_total_cs(queue: Union[cassiopeia.Queue, QueueInfo], cs: int, monsters: int=None) \
            -> int:
        if isinstance(queue, cassiopeia.Queue):
            return cs + (monsters if Constant.QUEUE_INFO[queue].has_monsters else 0)
        else:
            return cs + (monsters if queue.has_monsters else 0)

    @staticmethod
    def get_kda(kills: int, deaths: int, assists: int) \
            -> float:
        return (kills + assists) / (deaths + 1)

    @staticmethod
    def get_win_rate(wins: int, losses: int) \
            -> float:
        return (wins / (wins + losses) * 100) if wins + losses > 0 else 0

    @staticmethod
    def get_live_match_url(region: str, name: str) \
            -> str:
        name = name.replace(' ', '')
        return f'https://lolspectator.tv/spectate/?summoner={name.lower()}&server={region.lower()}'

    @staticmethod
    def get_match_history_url(region: str, platform: str, match_id: int, player_id: int=None) \
            -> str:
        if region == 'kr':
            url = f'https://matchhistory.leagueoflegends.co.kr/ko/#match-details/KR/{match_id}'
        else:
            url = f'https://matchhistory.{region}.leagueoflegends.com/en/#match-details/{platform}/{match_id}'
        if player_id is not None:
            url += f'/{player_id}'
        url += '?tab=overview'
        return url

    @staticmethod
    def get_op_gg_url(region: str, name: str) \
            -> str:
        name = name.replace(' ', '+')
        return f'http://{region}.op.gg/summoner/userName={name}'

    @staticmethod
    def get_time_stamp(time) \
            -> Tuple[int, int]:
        time = time / 1000 / 60
        return int(time), int(time % 1 * 60)

    @staticmethod
    def get_within_bounds(value: Union[int, None], min_value: int, max_value: int, default: int) \
            -> Optional[int]:
        if value is None:
            return default
        else:
            value = int(value)
        if 0 < max_value < value:
            return None
        if value < min_value:
            return None
        return value

    def get_amount(self, amount: Union[int, None], min: int, max: int, default: int) \
            -> Optional[int]:
        try:
            return self.get_within_bounds(amount, min, max, default)
        except ValueError:
            return None

    @staticmethod
    def get_region(region: str=None) \
            -> str:
        if region is None:
            return 'NA'
        return region if region.upper() in Constant.REGIONS_LIST else None
    # endregion

    # region PARSERS
    def parse_args(self, args: str) \
            -> Optional[List[str]]:
        try:
            return re.split(' ?{}'.format(self.arg_prefix), args)
        except TypeError:
            return None
        except ValueError:
            return None

    def parse_single_arg(self, args: list, arg: List[str], has_value: bool=False) \
            -> Optional[Tuple[bool, Optional[str]]]:
        if args is None:
            return False, None
        value = None
        found = False
        for a in args:
            try:
                split = re.split(self.val_prefix, a)
            except ValueError:
                return None
            if split[0] in arg:
                found = True
                if has_value and len(split) > 1:
                    value = split[1]
                break
        return found, value
    # endregion

    # region RETRIEVAL
    def retrieve_amount(self, amount: Union[int, None], min: int, max: int, default: int) \
            -> int:
        amount = self.get_amount(amount, min, max, default)
        if amount is None:
            raise commands.BadArgument(self.get_error_message(Error.INV_AMOUNT, min, max))
        return amount

    def retrieve_region(self, region: Union[str, None]) \
            -> str:
        region_temp = self.get_region(region)
        if region_temp is None:
            raise commands.UserInputError(self.get_error_message(Error.NF_REGION, region))
        return region_temp
    # endregion

    async def react_to(self, msg: discord.Message, emojis: list) \
            -> None:
        for e in self.bot.emojis:
            if e.name in emojis:
                await msg.add_reaction(e)
