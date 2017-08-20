import sys
import concurrent.futures._base
import DiscoUtils
from cogs import DiscoMusic
from cogs import DiscoGeneral
from cogs import DiscoLoL
try:
    import discord
    from discord.ext import commands
except ImportError:
    print("discord.py not installed.\n"
          "Try pip install discord.py[voice]\n")
    sys.exit(1)

__author__ = 'JosephPKC'
__version__ = '0.1'

# Read api keys and tokens
with open('config.txt', 'r') as file:
    token = file.readline().rstrip('\n')
    riot_key = file.readline().rstrip('\n')

# Create the bot
bot = commands.Bot(command_prefix=DiscoUtils.PREFIX, description='Shurima')
cogs = [
    DiscoMusic.Music(bot),
    DiscoGeneral.General(bot),
    DiscoLoL.LoL(bot, riot_key)
]
@bot.event
async def on_ready():
    print('Logged in as: {0}, {1}\n-----'.format(bot.user.name, bot.user.id))
    await bot.change_presence(game=discord.Game(name='Ascension'))

@bot.command(name='toggle')
async def toggle():
    DiscoUtils.DEBUG = not DiscoUtils.DEBUG
    DiscoUtils.VERBOSE = not DiscoUtils.VERBOSE

try:
    for c in cogs:
        bot.add_cog(c)
    bot.run(token)
except concurrent.futures._base.CancelledError:
    print('Cancelled process')
except Exception as e:
    print("Could not initialize bot.\n {}: {}\n".format(type(e).__name__, e))
finally:
    bot.close()


"""TODO List
Features
Music::Playlists - Creating, editing, deleting, renaming, and playing playlists (Nice to Have)
Music::Shuffle - Shuffle the current queue (Nice to Have)
Music::Repeat - Repeat the current or indicated song in queue by X times (Nice to Have)
Music::Remove - Remove the indicated song in queue (Nice to Have)
Music::Loop - Loop the queue (when dequeueing, add it to the end of the queue instead of deleting)
LoL:: - General LoL API features
DnD:: - General DnD and Database features
Trivia:: Storing, creating, and playing trivia games
Administrative Stuff? - Nah, this is a purely entertainment-focused bot. No administrative and management stuff
Dungeon Crawl:: Custom Text based game you can play? - Might be difficult with the multiple people using -> Need to store saves for each user, etc.
CleverBot:: - Maybe something with the Cleverbot API
Wolfram:: - Maybe something with the Wolfram API
Other Games:: - Like poker, blackjack, hangman, etc
Save:: Need a system to save the states( Savable states ) of the bot when it closes, or maybe once every 5 minutes.
OR
Database:: Instead of Save, we can just do read/writes to a database. Store any info that needs to be persistent into database, and then just lookup whenever it is needed and write to it whenever it changes (or just load into memory at start, but will need to be saved at the end - But what about when it closes unexpectedly? - Read/write whenever is safer, but slower)
QOL
Help - Just use the built-in default help instead of creating different helps.
Admin - Have a stored user id for admin modes, allowining debug commands
"""

# Implement a cache manager that will cache data