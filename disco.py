from cogs import lol
import os
import sys
try:
    import discord
    from discord.ext import commands
    print(f'Discord.py Version: {discord.version_info}.\n')
except ImportError:
    discord, commands = None, None
    print('Discord.py not found.')
    sys.exit(2)
try:
    import cassiopeia
except ImportError:
    cassiopeia = None
    print('Cassiopeia not found.')
    sys.exit(2)
# CONSTANTS
prefix = '\\'
arg_prefix = '-'
val_prefix = '='
# Get data store paths and keys
data_store_path = os.path.abspath('data/lolstaticdata.db')
with open('config.txt', 'r') as f:
    discord_key = f.readline().rstrip('\n')
    riot_key = f.readline().rstrip('\n')
    chgg_key = f.readline().rstrip('\n')
# Create the settings and apply them.
settings = {
    'global': {
        'version_from_match': 'patch',
        'enable_ghost_loading': True
    },
    'plugins': {

    },
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
            'api_key': chgg_key
        }
    },
    'logging': {
        'print_calls': True,
        'print_riot_api_key': False,
        'default': 'WARNING',
        'core': 'WARNING'
    }
}
cassiopeia.apply_settings(settings)
# Create and set bot
bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_ready():
    print('Ready to Shurima.')
    await bot.change_presence(game=discord.Game(name='Ascension'))

cogs = [
    lol.LoL(bot, prefix, arg_prefix, val_prefix)
]
try:
    for c in cogs:
        bot.add_cog(c)
    bot.run(discord_key)
finally:
    bot.close()
