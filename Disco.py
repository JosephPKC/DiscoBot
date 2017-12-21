import sys

try:
    import discord
    from discord.ext import commands
except ImportError:
    print('Discord.py is not installed\n. Do pip install discord.py[voice]\n.')
    sys.exit(2)


from Cogs import DiscoLoL

'''
The main file for Disco Bot.
Starts up the bot, and queues up any enabled cogs.
'''

# Get keys
with open('config.txt', 'r') as file:
    token = file.readline().rstrip('\n')
    riot = file.readline().rstrip('\n')
    key = file.readline().rstrip('\n')
    prefix = file.readline().rstrip('\n')

# Create the bot
bot = commands.Bot(command_prefix=prefix, descriptio='Shurima')
cogs = [
    DiscoLoL.LoL(bot, riot)
]

@bot.event
async def on_ready():
    print(prefix)
    print('Logged in and ready to go...')
    await bot.change_presence(game=discord.Game(name='Ascension'))

try:
    for c in cogs:
        bot.add_cog(c)
    bot.run(token)
finally:
    bot.close()