import json
import re
import requests
import sys

from discord.ext import commands

from Data.values import Generalvals as gv
from Data.values import LoLvals

from Containers import Summoner, SummonerRank
from Containers import PlayerMatchList, PlayerMatch

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



    def __init__(self, bot, key, downloader, cacher):
        self.bot = bot
        self.downloader = downloader
        self.cacher = cacher
        self.watcher = riotwatcher.RiotWatcher(key)
        self.items = None
        self.current_patch = self.__get_latest_patch()
        print(self.current_patch)

    #region Commands
    @commands.command(name='summoner', aliases=['player'], pass_context=True,
                      help='Get player info.')
    async def summoner(self, ctx, *, input: str = None):
        # Check inputs on name and region
        if input is None:
            await self.bot.say('**Usage**: summoner *name* -[r=*region*]')
            return
        name, region = await self.__parse_to_summoner(input)
        if name is None:
            return

        cached = self.cacher.get_api((name, region, gv.APIType.LOL_PLAYER))
        if cached is None:
            print('No cache with {}, {}, {} found.'.format(name, region, gv.APIType.LOL_PLAYER))
            # Search for name in region
            summoner = await self.__find_summoner(name, region)
            if summoner is None:
                return
            # Get ranks
            ranks = self.watcher.league.positions_by_summoner(region, summoner['id'])
            p_ranks = []
            for r in ranks:
                rank = SummonerRank.SummonerRank(r['queueType'], r['leagueName'], r['tier'], r['rank'], r['leaguePoints'], r['wins'], r['losses'], r['veteran'], r['inactive'], r['freshBlood'], r['hotStreak'])
                p_ranks.append(rank)

            # Cache data
            player = Summoner.Summoner(summoner['name'], region, summoner['id'], summoner['accountId'], summoner['summonerLevel'], summoner['profileIconId'], p_ranks)
            self.cacher.cache_api((name, region, gv.APIType.LOL_PLAYER), player)

        else:
            print('Cache with {} {} found.'.format(name, region))
            player = cached

        # Download profile icon
        data_url = 'http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png'.format(self.current_patch, player.icon)
        self.downloader.download_file(gv.DataType.IMG, '{}.png'.format(player.icon), data_url)
        with open('Data\\img\\{}.png'.format(player.icon), 'rb') as f:
            await self.bot.send_file(ctx.message.channel, f)

        # Display
        await self.bot.say('```' + str(player) + '```')
        return None

    @commands.command(name='matches', aliases=['ml'], pass_context=True,
                      help='List the 20 most recent matches')
    async def matches(self, ctx, *, input: str = None):
        # Check inputs on name and region
        if input is None:
            await self.bot.say('**Usage**: matches *name* -[r=*region*] -[n=*number* max:20]')
            return
        name, region, number = await self.__parse_for_matches(input)
        if name is None:
            return

        if number is None:
            number = 20
        elif number > 20:
            await self.bot.say('Max number is 20.')
            number = 20

        cached = self.cacher.get_api((name, region, gv.APIType.LOL_MATCH))
        if cached is None:
            print('No cache with {}, {}, {} found.'.format(name, region, gv.APIType.LOL_MATCH))
            # Search for name in region
            # Check cache
            summoner = await self.__find_summoner(name, region)
            if summoner is None:
                return

            try:
                # Get matches
                matches = self.watcher.match.matchlist_by_account_recent(region, summoner['accountId'])
                p_matches = []

                for m in matches['matches']:
                    # Get match history
                    history = await self.__find_match(m['gameId'], region)
                    if history is None:
                        return
                    # Find player index
                    player_index, team_index = self.__calculate_indices(summoner['accountId'], history)
                    if player_index is None or team_index is None:
                        await self.bot.say('Something went wrong when looking through match history.')

                    # Get brief info into match
                    player_info = history['participants'][player_index - 1]['stats']
                    team_info = history['teams'][team_index - 1]
                    match = PlayerMatch.PlayerMatch(m['gameId'], m['champion'], m['queue'], m['season'], m['role'], m['lane'], kills=player_info['kills'], deaths=player_info['deaths'], assists=player_info['assists'], cs=player_info['totalMinionsKilled'], cc=player_info['timeCCingOthers'], vision=player_info['visionScore'], victory=team_info['win'] =='Win')
                    p_matches.append(match)

                # Cache data
                matchlist = PlayerMatchList.PlayerMatchList(summoner['name'], region, summoner['id'], p_matches)
                # Cache each match history
            except requests.HTTPError as e:
                return await self.__do_HTTP_error(e, 'No matches found.')

            self.cacher.cache_api((name, region, gv.APIType.LOL_MATCH), matchlist)

        else:
            print('Cache with {} {} found.'.format(name, region))
            matchlist = cached
        await self.bot.say('```' + matchlist.to_str(1, min(number, 10)) + '```')
        if number > 10:
            await self.bot.say('```' + matchlist.to_str_match_only(11, number) + '```')
        return None

    @commands.command(name='match', aliases=['game'], pass_context=True,
                      help='Get details on a specific match.')
    async def match(self, ctx, *, input: str = None):
        if input is None:
            await self.bot.say('**Usage**: match *id* -[t]')
            return
        await self.__not_yet_implemented()
        return None
    #endregion

    #region Parsing and Input Sanity Checks
    def __parse_input_and_args(self, input):
        splits = re.split(' ?-', input)
        return splits[0], splits[1:]

    async def __parse_to_summoner(self, input):
        name, args = self.__parse_input_and_args(input)
        region = None

        for a in args:
            try:
                split = re.split('=', a)
            except:
                await self.bot.say('Error using optional arguments. Usage: -key=val.')
                return None, None, None
            if split[0] == 'r':
                region = split[1]

        if name is None:
            await self.bot.say('Unknown summoner name.')
            name = None

        region = await self.__parse_region(region)
        if region is None:
            return None, None

        return name, region

    async def __parse_for_matches(self, input):
        name, args = self.__parse_input_and_args(input)
        region = None
        number = None
        for a in args:
            try:
                split = re.split('=', a)
            except:
                await self.bot.say('Error using optional arguments. Usage: -key=val.')
                return None, None, None
            if split[0] == 'r':
                region = split[1]
            elif split[0] == 'n':
                number = split[1]

        if name is None:
            await self.bot.say('Unknown summoner name.')
            name = None

        region = await self.__parse_region(region)
        if region is None:
            return None, None, None

        return name, region, int(number) if number is not None else None

    async def __parse_region(self, region):
        if region is None:
            region = LoLvals.default_region
        else:
            if region not in LoLvals.regions_list:
                if region + '1' not in LoLvals.regions_list:
                    await self.bot.say('Unknown region.')
                    region = None
                else:
                    region += '1'
        return region


    async def __find_summoner(self, name, region):
        try:
            cached = self.cacher.get_api((name, region, gv.APIType.LOL_SUMMONER))
            if cached is None:
                summoner = self.watcher.summoner.by_name(region, name)
                self.cacher.cache_api((name, region, gv.APIType.LOL_SUMMONER), summoner)
            else:
                summoner = cached
            return summoner
        except requests.HTTPError as e:
            return await self.__do_HTTP_error(e, '**{}** was not found in **{}**'.format(name, region))

    async def __find_match(self, id, region):
        try:
            cached = self.cacher.get_api((id, region, gv.APIType.LOL_MATCH_HISTORY))
            if cached is None:
                history = self.watcher.match.by_id(region, id)
                self.cacher.cache_api((id, region, gv.APIType.LOL_MATCH_HISTORY), history)
            else:
                history = cached
            return history
        except requests.HTTPError as e:
            return await self.__do_HTTP_error(e, 'Match not found.')

    #endregion

    def __calculate_indices(self, id, history):
        player_index = None
        team_index = 2
        for p in history['participantIdentities']:
            if p['player']['currentAccountId'] == id:
                player_index = p['participantId']
        if player_index is None:
            return None, None
        if player_index < 6 or (player_index < 7 and (history['queueId'] == 75 or history['queueId'] == 98)):
            team_index = 1
        return player_index, team_index

    def __get_latest_patch(self):
        versions_path = 'Data\\json\\versions.json'
        self.downloader.download_file(gv.DataType.JSON, 'versions.json', 'https://ddragon.leagueoflegends.com/api/versions.json')
        # Get the first entry.
        with open(versions_path, 'r', encoding='utf-8') as f:
            j_file = json.loads(f.read())
        return j_file[0]

    async def __not_yet_implemented(self):
        msg = await self.bot.say('Not yet implemented. <:dab:390040479951093771>')
        for e in self.bot.get_all_emojis():
            if e.name == 'hellyeah':
                await self.bot.add_reaction(msg, e)
            elif e.name == 'dorawinifred':
                await self.bot.add_reaction(msg, e)
            elif e.name == 'cutegroot':
                await self.bot.add_reaction(msg, e)

    async def __do_HTTP_error(self, e, not_found='Not found'):
        if e.response.status_code == 404:
            await self.bot.say(not_found)
        elif e.response.status_code == 429:
            print('Retrying...')
        else:
            await self.bot.say('Unknown error occured. Status code {}.'.format(e.response.status_code))
        return None

