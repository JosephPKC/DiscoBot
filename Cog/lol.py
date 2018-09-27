import re
from enum import Enum
from typing import Callable, List, Optional, Tuple, Union

import cassiopeia
import datapipelines
import discord
from cassiopeia import *
from cassiopeia.core.common import CassiopeiaLazyList, CassiopeiaGhost
from cassiopeia.core.staticdata.champion import ChampionSpell, Stats

from discord.ext import commands

from Data import utils


class LoLError(Enum):
    NO_ERROR = 0
    REGION_NOT_FOUND = 1
    PLAYER_NOT_FOUND = 2
    LEAGUE_NOT_FOUND = 3
    CHAMPION_NOT_FOUND = 4
    ITEM_NOT_FOUND = 5


class LoLConstants(object):
    DEFAULT_COLOR = 0x18719
    DEFAULT_MATCH_AMOUNT = 20
    DEFAUL_REGION = 'NA'

    SPLIT_CHAMPIONS = 25
    SPLIT_LORE = 500

    OP_GG_ICON_URL = 'http://opgg-static.akamaized.net/images/logo/l_logo.png'

    REGIONS_LIST = [
        'NA',
        'KR'
    ]
    TAGS_LIST = [
        'ASSASSIN',
        'FIGHTER',
        'MAGE',
        'MARKSMAN',
        'SUPPORT',
        'TANK'
    ]


class LoLFactory(object):
    @staticmethod
    def create_help() \
            -> discord.Embed:
        return discord.Embed(title='Help')

    @staticmethod
    def create_all_champions(author: str, champions: cassiopeia.Champions,
                             free_to_play: bool, tags: Optional[List[str]]) \
            -> List[discord.Embed]:
        # For each champion (blocks up to 25)
            # State name, roles
        embeds = list()
        champions = utils.generate_blocks(list(champions), LoLConstants.SPLIT_CHAMPIONS)
        number = 1
        for block in champions:
            embeds .append(LoLFactory.build_all_champions_embed(author, block, free_to_play, tags, number))
            number += len(block)
        return embeds

    @staticmethod
    def create_champion(author: str, champion: cassiopeia.Champion, use_lore: bool, use_tips: bool) \
            -> List[discord.Embed]:
        embeds = list()
        embeds.append(LoLFactory.build_champion_embed(author, champion))
        if use_tips:
            embeds.append(LoLFactory.build_champion_tips_embed(author, champion))
        if use_lore:
            embeds.extend(LoLFactory.build_champion_lore_embed(author, champion))
        return embeds

    @staticmethod
    def create_skills(author: str, champion: cassiopeia.Champion) \
            -> List[discord.Embed]:
        return LoLFactory.build_skills_embed(author, champion)

    @staticmethod
    def create_lore(author: str, champion: cassiopeia.Champion) \
            -> List[discord.Embed]:
        return LoLFactory.build_champion_lore_embed(author, champion)

    @staticmethod
    def create_item(author: str, item: cassiopeia.Item, region: str) \
            -> List[discord.Embed]:
        print(item.to_dict())
        return [LoLFactory.build_items_embed(author, item, region)]

    # region Builders
    @staticmethod
    def build_lol_embed(description: str, requester: Optional[str]=None, thumbnail: Optional[str]=None,
                        image: Optional[str]=None, author: Optional[str]=None, author_url: Optional[str]=None,
                        icon_url: Optional[str]=None) \
            -> discord.Embed:
        return utils.create_embed_template(description, LoLConstants.DEFAULT_COLOR, requester,
                                           thumbnail, image, author, author_url, icon_url)

    @staticmethod
    def build_all_champions_embed(author: str, champions: List[cassiopeia.Champion],
                                  free_to_play: bool, tags: List[str], starting_number: int) \
            -> discord.Embed:
        tag_description = ', '.join([t.capitalize() for t in tags]) if tags is not None else ''
        free_to_play_description = 'Free to Play' if free_to_play else ''
        description = f'All {free_to_play_description} {tag_description} Champions'
        embed = LoLFactory.build_lol_embed(description=description, requester=author)
        for c in champions:
            embed.add_field(name=f'{starting_number}. __**{c.name}**__, {c.title}',
                            value=f'\n{", ".join(c.tags)}', inline=False)
            starting_number += 1
        return embed

    @staticmethod
    def build_champion_embed(author: str, champion: cassiopeia.Champion) \
            -> discord.Embed:
        description = f'__**{champion.name}**__ {champion.title}'
        default_art = champion.skins[0]
        embed = LoLFactory.build_lol_embed(description=description, requester=author,
                                           thumbnail=default_art.loading_image_url, image=default_art.splash_url)
        info = f'**Attack:** {champion.info.attack}\n' \
               f'**Defense:** {champion.info.defense}\n' \
               f'**Magic:** {champion.info.magic}\n' \
               f'**Difficulty:** {champion.info.difficulty}\n'
        embed.add_field(name=f'*{", ".join(champion.tags)}*', value=info, inline=False)
        stats = LoLUtils.get_stat_string('Health', champion.stats.health, champion.stats.health_per_level) + \
            LoLUtils.get_stat_string('Health Regen', champion.stats.health_regen,
                                     LoLWorkArounds.get_health_regen_per_level_stat(champion.stats)) + \
            LoLUtils.get_stat_string('Mana', champion.stats.mana, champion.stats.mana_per_level) + \
            LoLUtils.get_stat_string('Mana Regen', champion.stats.mana_regen,
                                     champion.stats.mana_regen_per_level) + \
            LoLUtils.get_stat_string('Armor', champion.stats.armor, champion.stats.armor_per_level) + \
            LoLUtils.get_stat_string('Magic Resist', champion.stats.magic_resist,
                                     champion.stats.magic_resist_per_level) + \
            LoLUtils.get_stat_string('Movement Speed', champion.stats.movespeed) + \
            LoLUtils.get_stat_string('Attack Range', champion.stats.attack_range) + \
            LoLUtils.get_stat_string('Attack Damage', champion.stats.attack_damage,
                                     champion.stats.attack_damage_per_level) + \
            LoLUtils.get_as_stat_string(champion.stats.attack_speed, champion.stats.percent_attack_speed_per_level)
        embed.add_field(name='__**Stats**__', value=stats, inline=False)

        embed = LoLFactory.add_skills_embed(embed, [champion.passive], True)
        return LoLFactory.add_skills_embed(embed, list(champion.spells))

    @staticmethod
    def build_champion_tips_embed(author: str, champion: cassiopeia.Champion) \
            -> discord.Embed:
        description = f'__**{champion.name}**__ Tips'
        embed = LoLFactory.build_lol_embed(description=description, requester=author)
        tips = ''
        for t in champion.ally_tips:
            tips += f'• {t}\n'
        embed.add_field(name='__**Ally Tips**__', value=tips, inline=True)
        tips = ''
        for t in champion.enemy_tips:
            tips += f'• {t}\n'
        embed.add_field(name='__**Eenemy Tips**__', value=tips, inline=True)
        return embed

    @staticmethod
    def build_champion_lore_embed(author: str, champion: cassiopeia.Champion) \
            -> List[discord.Embed]:
        embeds = list()
        description = f'__**{champion.name}**__ Lore'
        lore_blocks = utils.generate_blocks(champion.lore, LoLConstants.SPLIT_LORE)
        for i, l in enumerate(lore_blocks):
            embed = LoLFactory.build_lol_embed(description=description, requester=author)
            embed.add_field(name=f'Lore part {i + 1}', value=f'{l}')
            embeds.append(embed)
        return embeds

    @staticmethod
    def build_skills_embed(author: str, champion: cassiopeia.Champion) \
            -> List[discord.Embed]:
        embeds = list()
        description = f'__**{champion.name}**__ {champion.title}'
        embed = LoLFactory.build_lol_embed(description=description, requester=author,
                                           thumbnail=LoLUtils.get_spell_icon_url(champion.passive))
        embeds.append(LoLFactory.add_skills_embed(embed, [champion.passive], True))
        for s in champion.spells:
            embed = LoLFactory.build_lol_embed(description=description, requester=author,
                                               thumbnail=LoLUtils.get_spell_icon_url(s))
            embeds.append(LoLFactory.add_skills_embed(embed, [s]))
        return embeds

    @staticmethod
    def build_items_embed(author: str, item: cassiopeia.Item, region: str) \
            -> discord.Embed:
        description = f'__**{item.name}**__'
        embed = LoLFactory.build_lol_embed(description=description, requester=author,
                                           thumbnail=item.image.url)
        gold = f'**Base:** {item.gold.base}\n' \
               f'**Total:** {item.gold.total}\n' \
               f'**Sell:** {item.gold.sell}\n'
        if not item.gold.purchasable:
            gold += '**Not Purchasable**'
        embed.add_field(name='**Cost**', value=gold, inline=False)
        embed.add_field(name=f'**{item.plaintext}**', value=f'{utils.clean_html(item.description)}', inline=False)
        builds_from = LoLWorkArounds.get_item_build_from(item, region)
        if len(builds_from) > 0:
            items_from = ', '.join([i.name for i in builds_from])
            embed.add_field(name='**Builds From**', value=f'{items_from}', inline=False)
        if len(item.builds_into) > 0:
            items_into = ', '.join([i.name for i in item.builds_into])
            embed.add_field(name='**Builds Into**', value=f'{items_into}', inline=False)
        maps = ', '.join([m.name for m in item.maps])
        embed.add_field(name='**Available in**', value=f'{maps}', inline=False)
        return embed
    # endregion

    # region Helpers
    @staticmethod
    def add_skills_embed(embed: discord.Embed, spells: List[ChampionSpell], passive: bool=False) \
            -> discord.Embed:
        for i, s in enumerate(spells):
            key = 'P' if passive else s.keyboard_key.value
            value = ''
            if not passive:
                value += f'**Max Rank:** {LoLWorkArounds.get_skill_max_rank(s)}\n' \
                         f'**Cost:** {s.to_dict()["costBurn"]}\n' \
                         f'**Cooldown:** {s.to_dict()["cooldownBurn"]}\n'
            value += utils.clean_html(s.description)
            embed.add_field(name=f'**{key}:** {s.name}',
                            value=value,
                            inline=False)
        return embed
    # endregion


class LoLUtils(object):
    @staticmethod
    def get_error_message(error_type: LoLError, *args) \
            -> str:
        if error_type == LoLError.REGION_NOT_FOUND:
            if len(args) > 0:
                return f'Region **{args[0]}** not found.'
        elif error_type == LoLError.PLAYER_NOT_FOUND:
            if len(args) > 1:
                return f'Player **{args[0]}** not found in **{args[1]}**.'
        elif error_type == LoLError.LEAGUE_NOT_FOUND:
            if len(args) > 1:
                return f'Ranks not found for **{args[0]}** in **{args[1]}**.'
        return ''

    @staticmethod
    def get_op_gg_url(region: str, name: str) \
            -> str:
        name = name.replace(' ', '+')
        return f'http://{region}.op.gg/summoner/userName={name}'

    @staticmethod
    def get_region(region: Optional[str]=None) \
            -> str:
        if region is None:
            return LoLConstants.DEFAUL_REGION
        if utils.clean_string(region) in LoLConstants.REGIONS_LIST:
            return region
        raise commands.UserInputError(LoLUtils.get_error_message(LoLError.REGION_NOT_FOUND, region))

    @staticmethod
    def get_stat_string(stat_name: str, stat: float, stat_level: Optional[float]=None) \
            -> str:
        if stat_level is None:
            return f'**{stat_name}:** __{stat}__\n'
        at_18 = LoLUtils.calculate_stat_at_level(stat, stat_level)
        return f'**{stat_name}:** __{stat}__ + __{stat_level}__ / lvl (__{at_18}__ @ 18)\n'

    @staticmethod
    def get_as_stat_string(base: float, per_level: float) \
            -> str:
        at_18 = LoLUtils.calculate_stat_at_level(base, per_level)
        return f'**Attack Speed:** __{base}__ + __{per_level}__ % / lvl (__{at_18}__ @ 18)\n'

    @staticmethod
    def calculate_stat_at_level(base: float, growth: float, level: int=18) \
            -> float:
        if level == 0:
            return 0
        return float(format((base + growth * (level - 1)) * (0.7025 + 0.0175 * (level - 1)), '.3f'))

    @staticmethod
    def get_spell_icon_url(spell: ChampionSpell) \
            -> str:
        image = spell.image_info.to_dict()
        return f'http://ddragon.leagueoflegends.com/cdn/{image["version"]}/img/{image["group"]}/{image["full"]}'


class LoLWorkArounds(object):
    @staticmethod
    def get_health_regen_per_level_stat(stats: Stats) \
            -> float:
        try:
            return stats.health_regen_per_level
        except AttributeError:
            return stats.to_dict()['healthHegenPerLevel']

    @staticmethod
    def get_skill_max_rank(skills: ChampionSpell) \
            -> int:
        try:
            return skills.max_rank
        except AttributeError:
            return skills.to_dict()['maxRank']

    @staticmethod
    def get_item_build_from(item: cassiopeia.Item, region: str) \
            -> List[Item]:
        try:
            return item.builds_from
        except AttributeError:
            return LoLCog.load_items_from_codes(region, item.to_json()['buildsFrom'])


# Workflow of a typical LoL Command:
# 1. Print the command for logging purposes
# 2. Parse require inputs
# 3. Parse optional inputs/flags
# 4. Retrieve necessary data from cassiopeia
# 5. Scrape the data and format the data into a rich embed
# 6. Display the embeds in a series of messages

class LoLCog(object):
    _dab_emote = '<:dab:390040479951093771>'

    def __init__(self, bot: commands.Bot, prefix: str, arg_prefix: str, val_prefix: str) \
            -> None:
        self._bot = bot
        self._prefix = prefix
        self._arg_prefix = arg_prefix
        self._val_prefix = val_prefix
        self._help = LoLFactory.create_help()

    # region Commands
    @commands.group()
    async def lol(self, ctx: commands.Context) \
            -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Invalid Command: {ctx.subcommand_passed}. {self._dab_emote}')

    @lol.command(aliases=['?', 'commands'])
    async def help(self, ctx: commands.Context) \
            -> None:
        utils.print_command(ctx.command)
        await ctx.send(content=ctx.author.mention, embed=self._help)

    # endregion

    # region Static Data commands
    @lol.command(help='Displays a list of champions.')
    async def champions(self, ctx: commands.Context, *, args: Optional[str]=None) \
            -> None:
        utils.print_command(ctx.command, args=args)
        args = self._parse_args(args)
        free_only_flag, _ = self._parse_single_arg(args, ['f', 'free'])
        _, region = self._parse_single_arg(args, ['r', 'region'], True)
        region = LoLUtils.get_region(region)
        _, tag_filters = self._parse_single_arg(args, ['t', 'tags'], True)
        tag_filters = utils.parse_many_value_argument(tag_filters, LoLConstants.TAGS_LIST, ',')
        champions = self._retrieve_all_champions(region, free_only_flag, tag_filters)
        await utils.display_embed(ctx, ctx.author.mention,
                                  LoLFactory.create_all_champions(ctx.author, champions, free_only_flag, tag_filters))

    @lol.command(help='Displays information on the champion.')
    async def champion(self, ctx: commands.Context, name: str, *, args: Optional[str]=None) \
            -> None:
        utils.print_command(ctx.command, [name], args)
        name = utils.clean_string(name)
        args = self._parse_args(args)
        art_flag, _ = self._parse_single_arg(args, ['a', 'art', 'skins'])
        lore_flag, _ = self._parse_single_arg(args, ['l', 'lore'])
        tips_flag, _ = self._parse_single_arg(args, ['t', 'tips'])
        verbose_flag, _ = self._parse_single_arg(args, ['v', 'verbose', 'all'])
        if verbose_flag:
            art_flag, lore_flag, tips_flag = True, True, True
        _, region = self._parse_single_arg(args, ['r', 'region'], True)
        region = LoLUtils.get_region(region)
        champion = self._retrieve_champion(name, region)
        await utils.display_embed(ctx, ctx.author.mention,
                                  LoLFactory.create_champion(ctx.author, champion, lore_flag, tips_flag))
        if art_flag:
            for s in champion.skins[1:]:
                await ctx.send(f'**{s.name}: ** {s.splash_url}')

    @lol.command(help='Displays the skills of the champion.')
    async def skills(self, ctx: commands.Context, name: str, *, args: Optional[str]=None) \
            -> None:
        utils.print_command(ctx.command, [name], args)
        name = utils.clean_string(name)
        args = self._parse_args(args)
        _, region = self._parse_single_arg(args, ['r', 'region'], True)
        region = LoLUtils.get_region(region)
        champion = self._retrieve_champion(name, region)
        await utils.display_embed(ctx, ctx.author.mention,
                                  LoLFactory.create_skills(ctx.author, champion))

    @lol.command(help='Displays the lore of the champion.')
    async def lore(self, ctx: commands.Context, name: str, *, args: Optional[str]=None) \
            -> None:
        utils.print_command(ctx.command, [name], args)
        name = utils.clean_string(name)
        args = self._parse_args(args)
        _, region = self._parse_single_arg(args, ['r', 'region'], True)
        region = LoLUtils.get_region(region)
        champion = self._retrieve_champion(name, region)
        await utils.display_embed(ctx, ctx.author.mention,
                                  LoLFactory.create_lore(ctx.author, champion))

    @lol.command(help='Displays the splash arts of the champion.')
    async def skins(self, ctx: commands.Context, name: str, *, args: Optional[str]=None) \
            -> None:
        utils.print_command(ctx.command, [name], args)
        name = utils.clean_string(name)
        args = self._parse_args(args)
        _, region = self._parse_single_arg(args, ['r', 'region'], True)
        region = LoLUtils.get_region(region)
        champion = self._retrieve_champion(name, region)

        for s in champion.skins:
            await ctx.send(f'**{s.name}: ** {s.splash_url}')

    @lol.command(help='Displays the information of the item.')
    async def item(self, ctx: commands.Context, name: str, *, args: Optional[str]=None) \
            -> None:
        utils.print_command(ctx.command, [name], args)
        name = utils.clean_string(name)
        args = self._parse_args(args)
        _, region = self._parse_single_arg(args, ['r', 'region'], True)
        region = LoLUtils.get_region(region)
        item = self._retrieve_item(name, region)
        await utils.display_embed(ctx, ctx.author.mention,
                                  LoLFactory.create_item(ctx.author, item, region))
    # endregion

    # region Retrieval
    @staticmethod
    def _retrieve_all_champions(region: str, free_to_play: bool, tag_filters: Optional[List[str]]) \
            -> cassiopeia.Champions:
        champions = cassiopeia.get_champions(region=region)
        if free_to_play:
            champions = champions.filter(lambda champion: champion.free_to_play)
        if tag_filters is None:
            return champions
        for t in tag_filters:
            champions = champions.filter(lambda champion: t in [tag.upper() for tag in champion.tags])
        return champions

    @staticmethod
    def _retrieve_champion(name: str, region: str) \
            -> cassiopeia.Champion:
        champions = LoLCog._retrieve_all_champions(region, False, None)
        filtered_champions = champions.filter(lambda c: utils.clean_string(c.name) == name)
        if len(filtered_champions) != 1:
            return LoLCog._retrieve_na_champion(name, region, champions)
        return filtered_champions[0]

    @staticmethod
    def _retrieve_na_champion(name: str, region: str, champions: cassiopeia.Champions) \
            -> cassiopeia.Champion:
        return LoLCog._retrieve_na_thing(name, region, champions, LoLCog._retrieve_all_champions,
                                         LoLError.CHAMPION_NOT_FOUND)

    @staticmethod
    def _retrieve_all_items(region: str) \
            -> cassiopeia.Items:
        items = cassiopeia.get_items(region)
        return items

    @staticmethod
    def _retrieve_item(name: str, region: str) \
            -> cassiopeia.Item:
        items = LoLCog._retrieve_all_items(region)
        filtered_items = items.filter(lambda i: utils.clean_string(i.name) == name)
        if len(filtered_items) != 1:
            return LoLCog._retrieve_na_item(name, region, items)
        return filtered_items[0]

    @staticmethod
    def _retrieve_na_item(name:  str, region: str, items: cassiopeia.Items) \
            -> cassiopeia.Item:
        return LoLCog._retrieve_na_thing(name, region, items, LoLCog._retrieve_all_items, LoLError.ITEM_NOT_FOUND)

    @staticmethod
    def _retrieve_na_thing(name: str, region: str, item_list: CassiopeiaLazyList,
                           retrieval: Callable[[str], CassiopeiaLazyList], error: LoLError) \
            -> CassiopeiaGhost:
        if region != 'NA':
            na_things = retrieval('NA')
            na_things = na_things.filter(lambda x: utils.clean_string(x.name) == name)
            if len(na_things) == 1:
                thing = na_things[0]
                na_things = item_list.filter(lambda x: x.key == thing.key)
                if len(na_things) == 1:
                    return na_things[0]
        raise commands.UserInputError(LoLUtils.get_error_message(error, name))

    # endregion

    # @staticmethod
    # async def on_command_error(ctx: commands.Context, error: commands.CommandError) \
    #         -> None:
    #     await ctx.send(error)

    def _parse_args(self, args: str) \
            -> List[str]:
        return utils.parse_arguments(utils.clean_string(args), self._arg_prefix)

    def _parse_single_arg(self, args: List[str], valid_args: List[str], has_value: bool=False) \
            -> Tuple[bool, Optional[str]]:
        return utils.parse_single_argument(args, valid_args, self._arg_prefix, self._val_prefix, has_value)

    @classmethod
    def load_items_from_codes(cls, region: str, items: List[int]) \
            -> List[Item]:
        all_items = cls._retrieve_all_items(region)
        new_items = list()
        for i in items:
            item = all_items.filter(lambda x: x.id == i)
            if len(item) != 1:
                print(f'Item with id {i} not found.')
                continue
            new_items.append(item[0])
        return new_items
