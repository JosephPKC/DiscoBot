import sys
import concurrent.futures._base

import DiscoUtils
import DiscoMusic

try:
    import discord
    from discord.ext import commands
except ImportError:
    print("discord.py not installed.\n"
          "Try pip install discord.py[voice]\n")
    sys.exit(1)


bot = commands.Bot(command_prefix=DiscoUtils.PREFIX, description='Shurima')
cogs = [DiscoMusic.Music(bot)]

@bot.event
async def on_ready():
    print('Logged in as: {0}, {1}\n-----'.format(bot.user.name, bot.user.id))
    await bot.change_presence(game=discord.Game(name='Ascension'))
    # game = discord.Game(name='Ascension')
    # await bot.change_presence(status=None, game=game)

with open('config.txt', 'r') as file:
    token = file.readline()
    if len(sys.argv) == 2:
        bot.command_prefix = sys.argv[1]
        DiscoUtils.PREFIX = sys.argv[1]
    try:
        for c in cogs:
            bot.add_cog(c)
        bot.run(token)
    except concurrent.futures._base.CancelledError:
        print('Cancelled process')
    except:
        print("Could not initialize bot.")
    finally:
        bot.close()
