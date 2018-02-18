import discord
from manager import FileManager as File


rank_emojis_list = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'master', 'challenger']
tier_emojis_list = ['i', 'ii', 'iii', 'iv', 'v']
rank_emoji_path = 'data\\img\\emojis\\ranks\\'

emoji_id_map = {}


async def __create_emoji(bot, name, path):
    with open(path, 'rb') as image:
        server = list(bot.servers)[0]
        emoji = await bot.create_custom_emoji(server, name=name, image=image.read())
    return emoji


async def init(bot):
    # Create rank emojis
    for r in rank_emojis_list:
        path = '{}{}.png'.format(rank_emoji_path, r)
        emoji = await __create_emoji(bot, r, path)
        emoji_id_map[r] = emoji.id
        for t in tier_emojis_list:
            tiered_path = '{}{}_{}.png'.format(rank_emoji_path, r, t)
            emoji = await __create_emoji(bot, '{}_{}'.format(r, t), tiered_path)
            emoji_id_map['{}_{}'.format(r, t)] = emoji.id