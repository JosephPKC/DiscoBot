import discord
# region Constants
# Discord Bot Constants
bot_blurb = 'Shurima'
bot_game = 'Ascension'
bot_prefix = '\\'
bot_arg_prefix = '-'
bot_arg_value_prefix = ':'
# Paths
config_path = 'config.txt'
lol_db_path = 'data\\LoLStaticData.db'
# Cache Constants
api_freshness = 15
db_freshness = 20
str_freshness = 15
# endregion


# region Enumerations

# endregion


# region Mappings

# endregion


# region Methods
# Calculation, Retrieval (Get)
def get_minutes_seconds(time_in_s):
    return time_in_s // 60, time_in_s % 60


# Display (Print)
def print_command(cmd, inp):
    print('Command: {}\nInput: {}\n'.format(cmd, inp))


# Factory
def create_embed(color, description, requester, thumbnail=None):
    embed = discord.Embed(colour=color, description=description)
    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text='Requested by @{}.'.format(requester))
    return embed
# endregion
