# region Imports
import sys

try:
    import discord
    from discord.ext import commands
except ImportError:
    print('Discord.py not found.')
    print('pip install discord.py[voice].')
    sys.exit(2)

from cog import DiscoLoLCog
from manager import CacheManager, DatabaseManager, FileManager
from value import GeneralValues as Gv
# endregion

# region Global Constants
path = 'config.txt'
blurb = 'Shurima'
game = 'Ascension'
prefix = '\\'
# endregion

# region Start Script
# Get keys from file
with open(path, 'r') as file:
    discord_key = file.readline().rstrip('\n')
    riot_api_key = file.readline().rstrip('\n')
    champion_gg_key = file.readline().rstrip('\n')

# Create the bot
bot = commands.Bot(command_prefix=prefix, description=blurb)

# Create the managers
cache = CacheManager.CacheManager(Gv.db_freshness, Gv.api_freshness, Gv.str_freshness)
database = DatabaseManager.DatabaseManager(Gv.lol_db_path, cache)
file = FileManager.FileManager()

# Prepare the cogs
cogs = [
    DiscoLoLCog.DiscoLoLCog(bot, riot_api_key, champion_gg_key, cache, database, file)
]


# Wait for ready
@bot.event
async def on_ready():
    print('Disco Bot is ready to Shurima.')
    await bot.change_presence(game=discord.Game(name=game))

# Add cogs and run
try:
    for c in cogs:
        bot.add_cog(c)
    bot.run(discord_key)
finally:
    bot.close()
# endregion
