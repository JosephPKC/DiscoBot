import os
import sys
from typing import Dict, List, Tuple

from Cog import lol

try:
    imported_module = ['Discord.py', 'Cassiopeia', 'Pokebase', 'Wikipedia API']
    module = 0
    import discord
    from discord.ext import commands

    print(f'Loaded {imported_module[module]} Version: {discord.version_info}.')
    module += 1
    import cassiopeia

    print(f'Loaded {imported_module[module]}.')
    module += 1
    import pokebase

    print(f'Loaded {imported_module[module]}.')
    module += 1
    import wikipediaapi as wiki

    print(f'Loaded {imported_module[module]}.')
except ImportError:
    discord, commands, cassiopeia, pokebase, wiki = None, None, None, None, None
    print(f'{imported_module[module]} not found.')
    sys.exit(2)


def load_constants() \
        -> Tuple[str, str, str]:
    return '\\', '-', '='


def load_data_store() \
        -> str:
    return os.path.abspath('Data/lolStaticData.db')


def load_keys() \
        -> Tuple[str, str, str]:
    with open('Data/config.txt', 'r') as f:
        discord_key = f.readline().rstrip('\n')
        riot_key = f.readline().rstrip('\n')
        ch_gg_key = f.readline().rstrip('\n')
    return discord_key, riot_key, ch_gg_key


def load_settings(data_store_path: str, riot_key: str, ch_gg_key: str) \
        -> Dict:
    return {
        'global': {
            'version_from_match': 'patch',
            'enable_ghost_loading': True
        },
        'plugins': {},
        'pipeline': {
            'Cache': {},
            'SimpleKVDiskStore': {
                'package': 'cassiopeia_diskstore',
                'path': data_store_path
            },
            'DDragon': {},
            'RiotAPI': {
                'api_key': riot_key,
                'request_by_id': True
            },
            'ChampionGG': {
                'package': 'cassiopeia_championgg',
                'api_key': ch_gg_key
            }
        },
        'logging': {
            'print_calls': True,
            'print_riot_api_key': False,
            'default': 'WARNING',
            'core': 'WARNING'
        }
    }


def load_cogs(bot: commands.Bot, prefix: str, arg_prefix: str, val_prefix: str) \
        -> List[object]:
    return [
        lol.LoLCog(bot, prefix, arg_prefix, val_prefix)
    ]


def run_bot(bot: commands.Bot, cogs: List[object], discord_key: str) \
        -> None:
    try:
        for c in cogs:
            bot.add_cog(c)
        bot.run(discord_key)
    finally:
        bot.close()


def main() \
        -> None:
    prefix, arg_prefix, val_prefix = load_constants()
    discord_key, riot_key, ch_gg_key = load_keys()
    cassiopeia.apply_settings(load_settings(load_data_store(), riot_key, ch_gg_key))

    bot = commands.Bot(command_prefix=prefix)

    @bot.event
    async def on_ready():
        print(f'Ready to Shurima.')
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name='Ascension'
            )
        )

    run_bot(bot, load_cogs(bot, prefix, arg_prefix, val_prefix), discord_key)


if __name__ == "__main__":
    main()
