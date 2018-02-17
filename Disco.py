import sys
try:
    import discord
    from discord.ext import commands
except ImportError:
    commands, discord = None, None
    print('Discord.py not found.')
    print('pip install discord.py[voice].')
    sys.exit(2)
from cog import DiscoLoLCog
from manager import LoLDatabase, LoLDataDragon
from value import GeneralValues as Gv

# Get keys from file
with open(Gv.config_path, 'r') as file:
    discord_key = file.readline().rstrip('\n')
    riot_api_key = file.readline().rstrip('\n')
    champion_gg_key = file.readline().rstrip('\n')
# Create the bot
bot = commands.Bot(command_prefix=Gv.bot_prefix, description=Gv.bot_blurb)


# Wait for ready
@bot.event
async def on_ready():
    print('Disco Bot is ready to Shurima.')
    await bot.change_presence(game=discord.Game(name=Gv.bot_game))
# Prepare the cogs
cogs = [
    DiscoLoLCog.DiscoLoLCog(bot, riot_api_key, champion_gg_key)
]
# Add cogs and run
try:
    for c in cogs:
        bot.add_cog(c)
    LoLDatabase.init()
    LoLDataDragon.init()
    bot.run(discord_key)
finally:
    LoLDatabase.end()
    bot.close()

# Name Prefixes
# Get - Non-API Retrieval/Calculation/Conversion
# Find - API Retrieval
# Print - Print to console
# Display - Print to discord
# Create - Core Factory
# Build - Package Factory
# Command - Commands
# Parse - Parse
# Name Suffixes
# Map - Mappings
# Url - Url base
# Part - Url part
# File - File name
# Path - File path
# Default - Default
# range - range
