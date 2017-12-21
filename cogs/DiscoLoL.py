import json
import re
import requests
import sys

from discord.ext import commands

from Data.values import Generalvals as gv
from Data.values import LoLvals

from Containers import Summoner
from Containers import SummonerRank

from Managers import DownloadManager

try:
    import riotwatcher
except ImportError:
    print('Do pip install riotwatcher')

try:
    import py_gg
except ImportError:
    print('Do pip install py_gg')

class LoL:



    def __init__(self, bot, key):
        self.bot = bot
        self.downloader = DownloadManager.DownloadManager()
        self.watcher = riotwatcher.RiotWatcher(key)
        self.items = None
        self.current_patch = self.__get_latest_patch()
        print(self.current_patch)

    @commands.command(name='summoner', aliases=['player'], pass_context=True,
                      help='Get player info.')
    async def summoner(self, ctx, *, input: str = None):
        msg = await self.bot.say('Not yet implemented')
        for e in self.bot.get_all_emojis():
            if e.name == 'dab':
                await self.bot.add_reaction(msg, e)


        # Check inputs on name and region
        if input is None:
            await self.bot.say('**Usage**: \summoner *name* -[*region*]')
        name, region = await self.__parse_to_summoner(input)
        if name is None:
            return
        # Search for name in region
        summoner = await self.__find_summoner(name, region)
        if summoner is None:
            return
        # Get profile icon
        # Get ranks
        ranks = self.watcher.league.positions_by_summoner(region, summoner['id'])
        p_ranks = []
        for r in ranks:
            rank = SummonerRank.SummonerRank(r['queueType'], r['leagueName'], r['tier'], r['rank'], r['leaguePoints'], r['wins'], r['losses'], r['veteran'], r['inactive'], r['freshBlood'], r['hotStreak'])
            p_ranks.append(rank)
        # Download profile icon
        data_url = 'http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png'.format(self.current_patch, summoner['profileIconId'])

        self.downloader.download_file(gv.DataType.IMG, '{}.png'.format(summoner['profileIconId']), data_url)

        with open('Data\\img\\{}.png'.format(summoner['profileIconId']), 'rb') as f:
            await self.bot.send_file(ctx.message.channel, f)

        # Cache data
        player = Summoner.Summoner(summoner['name'], region, summoner['id'], summoner['summonerLevel'], summoner['profileIconId'], p_ranks)
        # Display
        await self.bot.say('```' + str(player) + '```')
        return None


    #region Parsing and Input Sanity Checks
    async def __parse_to_summoner(self, input):
        print(input)
        split_input = re.split(' ?-', input)
        name, region = split_input[0], (split_input[1] if len(split_input) > 1 else None)
        if name is None:
            await self.bot.say('Unknown summoner name.')
            name = None
        if region is None:
            region = LoLvals.default_region
        elif region not in LoLvals.regions_list:
            if region + '1' not in LoLvals.regions_list:
                await self.bot.say('Unknown region.')
                region = None
            else:
                region += '1'
        return name, region

    async def __find_summoner(self, name, region):
        try:
            summoner = self.watcher.summoner.by_name(region, name)
            return summoner
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                await self.bot.say('**{}** was not found in **{}**.'.format(name, region))
            elif e.response.status_code == 429:
                print('Retrying...')
            else:
                await self.bot.say('Unknown error occured. Status code {}.'.format(e.response.status_code))
            return None

    #endregion

    def __get_latest_patch(self):
        versions_path = 'Data\\json\\versions.json'
        self.downloader.download_file(gv.DataType.JSON, 'versions.json', 'https://ddragon.leagueoflegends.com/api/versions.json')
        # Get the first entry.
        with open(versions_path, 'r', encoding='utf-8') as f:
            j_file = json.loads(f.read())
        return j_file[0]
