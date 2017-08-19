import requests
import json

import riotwatcher
from discord.ext import commands

import DiscoUtils

""" LoL commands
Game - show the current game info for a player in a region
Champion - show champion statistics and info
Item - show item statistics and info
Best - show the top champions in each role
Stats - Show highest picked, highest banned, highest winrate, etc 
Build - Show best builds for champion in role
Counters - Show best counters for champion in role
Other Sites that have APIs

"""
#TOMORROW IS REFACTORING DAY
#TODO: Get version number for lol_status maybe to stay up to date
#TODO: Maybe move the constants to Database
#TODO: Implement the skins command. (It will show the splashes for each skin for the given champion)
#TODO: Implement the recommended command. (This will show recommended items for each gamemode for the champion)
#TODO: champion stats needs access to another API to get champion play stats
#TODO: Builds command to show the top builds needs access to another API maybe champion.gg?
#TODO: Need some kind of caching to cache the messages, so that it doesn't keep recomputing them when it was done recently (Store the type, data, and timestamp) - One for data (heavy) for displaying (like messages, etc), and one for db calls (lite) for internal use
#TODO: Move the downloading to a donwload manager, that simply downloads the given url, and saves it as some file. (It will place requests into a queue, and it will in a loop, download files one by one)
#TODO: For all: Move all discord.py and other non-std stuff into a try block (more pythony that way)
#ALL FILES should be in a folder with the version number

#NOTE: champion.gg api has a python warapper called py_gg

class LoL:
    DEFAULT_REGION = 'na1'
    VERSION = '7.17.1'
    REGIONS = [
        'br1',
        'eun1',
        'euw1',
        'jp1',
        'kr',
        'la1',
        'la2',
        'na1',
        # 'na',
        'oc1',
        'tr1',
        'ru',
        'pbe1'
    ]
    CHAMPIONS = {
        'aatrox': 'Aatrox',
        'ahri': 'Ahri',
        'akali': 'Akali',
        'alistar': 'Alistar',
        'ali': 'Alistar',
        'amumu': 'Amumu',
        'anivia': 'Anivia',
        'annie': 'Annie',
        'ashe': 'Ashe',
        'aurelion sol': 'AurelionSol',
        'aurelionsol': 'AurelionSol',
        'aurelion': 'AurelionSol',
        'azir': 'Azir',
        'bard': 'Bard',
        'blitzcrank': 'Blitzcrank',
        'blitz': 'Blitzcrank',
        'brand': 'Brand',
        'braum': 'Braum',
        'caitlyn': 'Caitlyn',
        'cait': 'Caitlyn',
        'camille': 'Camille',
        'cassiopeia': 'Cassiopeia',
        'cass': 'Cassiopeia',
        'cho\'gath': 'Chogath',
        'cho gath': 'Chogath',
        'chogath': 'Chogath',
        'cho': 'Chogath',
        'corki': 'Corki',
        'darius': 'Darius',
        'diana': 'Diana',
        'draven': 'Draven',
        'dr. mundo': 'DrMundo',
        'dr.mundo': 'DrMundo',
        'dr mundo': 'DrMundo',
        'drmundo': 'DrMundo',
        'mundo': 'DrMundo',
        'ekko': 'Ekko',
        'elise': 'Elise',
        'evelynn': 'Evelynn',
        'eve': 'Evelynn',
        'ezreal': 'Ezreal',
        'ez': 'Ezreal',
        'fiddlesticks': 'FiddleSticks',
        'fiddle': 'FiddleSticks',
        'fiora': 'Fiora',
        'fizz': 'Fizz',
        'galio': 'Galio',
        'gangplank': 'Gangplank',
        'gp': 'Gangplank',
        'garen': 'Garen',
        'gnar': 'Gnar',
        'gragas': 'Gragas',
        'graves': 'Graves',
        'hecarim': 'Hecarim',
        'heimerdinger': 'Heimerdinger',
        'heimer': 'Heimerdinger',
        'illaoi': 'Illaoi',
        'irelia': 'Irelia',
        'ivern': 'Ivern',
        'janna': 'Janna',
        'jarvan iv': 'JarvanIV',
        'jarvaniv': 'JarvanIV',
        'jarvan': 'JarvanIV',
        'jax': 'Jax',
        'jayce': 'Jayce',
        'jhin': 'Jhin',
        'jinx': 'Jinx',
        'kalista': 'Kalista',
        'karma': 'Karma',
        'karthus': 'Karthus',
        'kassadin': 'Kassadin',
        'kass': 'Kassadin',
        'katarina': 'Katarina',
        'kat': 'Katarina',
        'kayle': 'Kayle',
        'kayn': 'Kayn',
        'kennen': 'Kennen',
        'kha\'zix': 'Khazix',
        'kha zix': 'Khazix',
        'khazix': 'Khazix',
        'kha': 'Khazix',
        'kindred': 'Kindred',
        'kled': 'Kled',
        'kog\'maw': 'KogMaw',
        'kog maw': 'KogMaw',
        'kogmaw': 'KogMaw',
        'kog': 'KogMaw',
        'leblanc': 'Leblanc',
        'lee sin': 'LeeSin',
        'leesin': 'LeeSin',
        'lee': 'LeeSin',
        'leona': 'Leona',
        'lissandra':' Lissandra',
        'liss': 'Lissandra',
        'lucian': 'Lucian',
        'lulu': 'Lulu',
        'lux': 'Lux',
        'malphite': 'Malphite',
        'malzahar': 'Malzahar',
        'malz': 'Malzahar',
        'maokai': 'Maokai',
        'mao': 'Maokai',
        'master yi': 'MasterYi',
        'masteryi': 'MasterYi',
        'yi': 'MasterYi',
        'miss fortune': 'MissFortune',
        'mf': 'MissFortune',
        'wukong': 'MonkeyKing',
        'mordekaiser': 'Mordekaiser',
        'mord': 'Mordekaiser',
        'morgana': 'Morgana',
        'morg': 'Morgana',
        'nami': 'Nami',
        'nasus': 'Nasus',
        'nautilus': 'Nautilus',
        'naut': 'Nautilus',
        'nidalee': 'Nidalee',
        'nid': 'Nidalee',
        'nocturne': 'Nocturne',
        'noc': 'Nocturne',
        'nunu': 'Nunu',
        'olaf': 'Olaf',
        'orianna': 'Orianna',
        'ori': 'Orianna',
        'ornn': 'Ornn',
        'pantheon': 'Pantheon',
        'panth': 'Pantheon',
        'poppy': 'Poppy',
        'quinn': 'Quinn',
        'rakan': 'Rakan',
        'rammus': 'Rammus',
        'rek\'sai': 'RekSai',
        'rek sai': 'RekSai',
        'reksai': 'RekSai',
        'rek': 'RekSai',
        'renekton': 'Renekton',
        'rengar': 'Rengar',
        'riven': 'Riven',
        'rumble': 'Rumble',
        'ryze': 'Ryze',
        'sejuani': 'Sejuani',
        'shaco': 'Shaco',
        'shen': 'Shen',
        'shyvana': 'Shyvana',
        'singed': 'Singed',
        'sion': 'Sion',
        'sivir': 'Sivir',
        'skarner': 'Skarner',
        'sona': 'Sona',
        'soraka': 'Soraka',
        'swain': 'Swain',
        'syndra': 'Syndra',
        'tahm kench': 'TahmKench',
        'tahmkench': 'TahmKench',
        'tahm': 'TahmKench',
        'taliyah': 'Taliyah',
        'talon': 'Talon',
        'taric': 'Taric',
        'teemo': 'Teemo',
        'thresh': 'Thresh',
        'tristana': 'Tristana',
        'trundle': 'Trundle',
        'tryndamere': 'Tryndamere',
        'twisted fate': 'TwistedFate',
        'twistedfate': 'TwistedFate',
        'tf': 'TwistedFate',
        'twitch': 'Twitch',
        'udyr': 'Udyr',
        'urgot': 'Urgot',
        'varus': 'Varus',
        'vayne': 'Vayne',
        'veigar': 'Veigar',
        'vel\'koz': 'Velkoz',
        'vel koz': 'Velkoz',
        'velkoz': 'Velkoz',
        'vel': 'Velkoz',
        'vi': 'Vi',
        'viktor': 'Viktor',
        'vladimir': 'Vladimir',
        'volibear': 'Volibear',
        'warwick': 'Warwick',
        'xayah': 'Xayah',
        'xerath': 'Xerath',
        'xin zhao': 'XinZhao',
        'xinzhao': 'XinZhao',
        'xin': 'XinZhao',
        'yasuo': 'Yasuo',
        'yorick': 'Yorick',
        'zac': 'Zac',
        'zed': 'Zed',
        'ziggs': 'Ziggs',
        'zilean': 'Zilean',
        'zyra': 'Zyra'
    }
    QUEUES = {
        'RANKED_FLEX_TT': 'Flex 3v3',
        'RANKED_FLEX_SR': 'Flex 5v5',
        'RANKED_SOLO_5x5': 'Solo 5v5',
        'RANKED_TEAM_3x3': 'Team 3v3',
        'RANKED_TEAM_5x5': 'Team 5v5'
    }
    SPELLS = [
        'Q',
        'W',
        'E',
        'R'
    ]
    def __init__(self, bot, riot):
        self.bot = bot
        self.watcher = riotwatcher.RiotWatcher(riot)

    @commands.command(name='summoner', aliases=[], pass_context=True,
                      help='Display info on the summoner')
    async def summoner(self, ctx, *, name: str = None):
        name, region = await self._base_op(name)
        if name == None:
            return

        try:
            summoner = await self._find_summoner(name, region)
            ranks = self.watcher.league.positions_by_summoner(region, summoner['id'])
            sranks = ''
            if len(ranks) == 0:
                sranks += 'Unranked'
            else:
                for r in ranks:
                    sranks += self.QUEUES[r['queueType']] + '\n'
                    sranks += '\t' + r['leagueName'] + '\n'
                    # Find the summoner in entries

                    sranks += '\t' + r['tier'] + ' ' + r['rank'] + '\n'
                    sranks += '\t' + str(r['leaguePoints']) + ' LP, '
                    sranks += 'W/L: ' + str(r['wins']) \
                              + '/' + str(r['losses']) + '\n'

                    tags = [r['veteran'], r['inactive'],
                            r['freshBlood'], r['hotStreak']]
                    if True in tags:
                        sranks += '\t'
                        if tags[0]:
                            sranks += 'Veteran. '
                        if tags[1]:
                            sranks += 'Inactive. '
                        if tags[2]:
                            sranks += 'Fresh Blood. '
                        if tags[3]:
                            sranks += 'Hot Streak. '
                    sranks += '\n'

            icon = str(summoner['profileIconId'])
            pics = DiscoUtils.find('{}.png'.format(icon), 'data\\lol_icons')

            if len(pics) == 0:
                DiscoUtils.download_file('http://ddragon.leagueoflegends.com/'
                                 'cdn/{}/img/profileicon/{}.png'.format(self.VERSION, icon),
                                          'data\\lol_icons\\{}.png'.format(icon))

                DiscoUtils.shrink_image('data\\lol_icons\\{}.png'.format(icon),
                                        'data\\lol_icons\\{}_small.png'.format(icon),
                                        40, 40)
            # Print the info nicely
            info = '```'
            info += 'Name: ' + summoner['name'] + '\n'
            info += 'Level: ' + str(summoner['summonerLevel']) + '\n'
            info += '\nRanked Stats: \n' + sranks + '\n\n'
            info += '```\n'
            #     .format(str(summoner['profileIconId']))
            await self.bot.say(info)
            with open('data\\lol_icons\\{}_small.png'.format(icon), 'rb') as f:
                await self.bot.send_file(ctx.message.channel, f)
        # except ChildProcessError:
            # print('blah')
        except OSError:
            await self.bot.say('Error opening image for icon {}.'.format(summoner['profileIconId']))
        except Exception as e:
            DiscoUtils.generic_except(e)

    @commands.command(name='mastery', aliases=[], pass_context=True,
                      help='Display mastery pages')
    async def mastery(self, ctx, *, name: str = None):
        name, region = await self._base_op(name)
        if name == None:
            return

        try:
            summoner = await self._find_summoner(name, region)
            masteries = self.watcher.masteries.by_summoner(region, summoner['id'])
            masteries = masteries['pages']
            smas = ''
            for i, m in enumerate(masteries):
                smas += str(i + 1) + ': '
            # await self.bot.say(masteries)
        # except Exception as e:
            # DiscoUtils.generic_except(e)
        finally:
            await self.bot.say('Not implemented yet')

    @commands.command(name='champion', aliases=[], pass_context=True,
                      help='Display champion info')
    async def champion(self, ctx, *, name: str = None):
        name, verbose = self._parse_champion(name)
        name = name.lower()

        try:
            # champions_list = self.watcher.static_data.champions(self.DEFAULT_REGION)
            if name not in self.CHAMPIONS:
                await self.bot.say('Champion **{}** does not exist.'.format(name))
                return

            name = self.CHAMPIONS[name]

            # Download or open the json file
            jchamp = DiscoUtils.find('{}.json'.format(name), 'data\\lol_champions')
            if len(jchamp) == 0:
                DiscoUtils.download_file('http://ddragon.leagueoflegends.com/'
                                         'cdn/{}/data/en_US/champion/{}.json'
                                         .format(self.VERSION, name),
                                         'data\\lol_champions\\{}.json'.format(name))
            champ = None
            with open('data\\lol_champions\\{}.json'.format(name)) as f:
                champ = f.read()
                champ = json.loads(champ)
                # await self.bot.say(str(champ))


            champ = champ['data'][name]
            # print(champ)
            info = ''
            info += champ['name'] + ', ' + champ['title'] + '\n'
            info += '\t' + champ['tags'][0] + ', ' + champ['tags'][1]

            stats = ''
            gstats = champ['info']
            stats += '\tAttack: ' + \
                     str(gstats['attack']) + ' Defense: ' + \
                     str(gstats['defense']) + '\n\tMagic: ' + \
                     str(gstats['magic']) + ' Difficulty: ' + \
                     str(gstats['difficulty']) + '\n\n'

            nstats = champ['stats']
            stats += '\tHealth: ' + str(nstats['hp']) + ' + ' \
                     + str(nstats['hpperlevel']) + '/level\n'
            stats += '\tMana: ' + str(nstats['mp']) + ' + ' \
                     + str(nstats['mpperlevel']) + '/level\n'
            stats += '\tArmor: ' + str(nstats['armor']) + ' + ' \
                     + str(nstats['armorperlevel']) + '/level\n'
            stats += '\tMagic Resist: ' + str(nstats['spellblock']) + ' + ' \
                     + str(nstats['spellblockperlevel']) + '/level\n'
            stats += '\tHealth Regen: ' + str(nstats['hpregen']) + ' + ' \
                     + str(nstats['hpregenperlevel']) + '/level\n'
            stats += '\tMana Regen: ' + str(nstats['mpregen']) + ' + ' \
                     + str(nstats['mpregenperlevel']) + '/level\n'
            stats += '\tAttack Damage: ' + str(nstats['attackdamage']) + ' + ' \
                     + str(nstats['attackdamageperlevel']) + '/level\n'
            stats += '\tAttack Speed: {:.3} + {}%/level\n'\
                         .format(DiscoUtils.champion_base_as(nstats['attackspeedoffset']),
                                 nstats['attackspeedperlevel'])
            stats += '\tMovement Speed: ' + str(nstats['movespeed']) + '\n'
            stats += '\tAttack Range: ' + str(nstats['attackrange']) + '\n'

            nspells = champ['spells']
            spells = ''
            spells += 'Passive: ' + champ['passive']['name'] + ': ' \
                      + champ['passive']['description'].replace('<br><br>', '\n\t') + '\n\n'
            for i, s in enumerate(nspells):
                spells += self.SPELLS[i] + ': ' \
                          + s['name'] + ': ' + s['description'].replace('<br><br>', '\n\t') + '\n\n'
                # spells += '\tCooldown: ' + s['cooldownBurn'] + '\n'
                # spells += '\tCost: ' + s['costBurn'] + '\n'
                # spells += '\t'

            lore = ''
            tips = ''
            if verbose is not None:
                lore = '\t' + champ['lore'] + '\n'
                lore = lore.replace('<br><br>', '\n\t').replace('<br>', ' ')
                tips = 'Ally Tips:\n'
                for t in champ['allytips']:
                    tips += '\t' + t + '\n'
                tips += 'Enemy Tips:\n'
                for t in champ['enemytips']:
                    tips += '\t' + t + '\n'

            pics = DiscoUtils.find('{}_0.png'.format(name), 'data\\lol_splash')

            if len(pics) == 0:
                DiscoUtils.download_file('http://ddragon.leagueoflegends.com'
                                          '/cdn/img/champion/splash/{}_0.jpg'.format(name),
                                          'data\\lol_splash\\{}_0.png'.format(name))

                # DiscoUtils.shrink_image('data\\lol_splash\\{}_0.png'.format(name),
                #                         'data\\lol_splash\\{}_0_small.png'.format(name),
                #                         100, 100)

            with open('data\\lol_splash\\{}_0.png'.format(name), 'rb') as f:
                await self.bot.send_file(ctx.message.channel, f)

            msg = '```' + info + '\nSTATS:\n' + stats + '\nSPELLS:\n' + spells + '```'
            await self.bot.say(msg)
            if verbose is not None:
                msg = '```' + tips + '```'
                await self.bot.say(msg)

                # pages = len(lore) / 2000
                # pages = round(len(lore) )
                # print(pages)
                pages = [lore[i:i + 1800] for i in range(0, len(lore), 1800)]
                msg = '```Lore pt. {}:\n'.format(1) + pages[0] + '...```'
                await self.bot.say(msg)
                for i, p in enumerate(pages[1:-1]):
                    msg = '```Lore pt. {}:\n...'.format(i + 2) + p + '...```'
                    await self.bot.say(msg)
                msg = '```Lore pt. {}:\n...'.format(len(pages)) + pages[-1] + '```'
                await self.bot.say(msg)

            # print(msg)
            # await self.bot.say(msg)

        except requests.HTTPError as err:
            if err.response.status_code == 404:
                await self.bot.say('**{}** was not found.'.format(name))
            elif err.response.status_code == 429:
                await self.bot.say('Rate Limit reached. Retry in {} seconds.'.format(err.response.headers['Retry-After']))
            else:
                await self.bot.say('Unknown error occurred. Status code {}.'
                                   .format(err.response.status_code))




    @commands.command(name='info', pass_context=True)
    async def info(self, ctx, *, name: str = None):
        name, region = await self._base_op(name)
        if name == None:
            return
        try:
            summoner = await self._find_summoner(name, region)
            # Look at cool stuff
            pi = self.watcher.static_data.profile_icons(region)
            print('PROFILE ICON:\n\n')
            print(pi, end='\n\n')

            cm = self.watcher.champion_mastery.by_summoner(region, summoner['id'])
            print('CHAMPION MASTERY:\n\n')
            print(cm, end='\n\n')
            m = self.watcher.match.matchlist_by_account_recent(region, summoner['accountId'])
            print('MATCH:\n\n')
            print(m, end='\n\n')
            s = self.watcher.spectator.by_summoner(region, summoner['id'])
            print('SPECTATOR:\n\n')
            print(s, end='\n\n')
            r = self.watcher.runes.by_summoner(region, summoner['id'])
            print('RUNES:\n\n')
            print(r, end='\n\n')
            # c = self.watcher.champion.all(region)
            # print('CHAMPIONS:\n\n')
            # print(c, end='\n\n')
            ls = self.watcher.lol_status.shard_data(region)
            print('LOL STATUS:\n\n')
            print(ls, end='\n\n')
            ch = self.watcher.static_data.champion(region,1)
            print('CHAMPION:\n\n')
            print(ch, end='\n\n')
            ru = self.watcher.static_data.rune(region, 1)
            print('RUNE:\n\n')
            print(ru, end='\n\n')
            it = self.watcher.static_data.item(region, 1)
            print('ITEM:\n\n')
            print(it, end='\n\n')
            ma = self.watcher.static_data.mastery(region, 1)
            print('MASTERY:\n\n')
            print(ma, end='\n\n')
            map = self.watcher.static_data.maps(region, 1)
            print('MAP:\n\n')
            print(map, end='\n\n')

            ss = self.watcher.static_data.summoner_spell(region, 1)
            print('SUMMONER SPELL:\n\n')
            print(ss, end='\n\n')
            # self.watcher.match.

        finally:
            None

    def _parse_champion(self, string):
        name, verbose = DiscoUtils.parse_into_two(string, ' ?-')
        if not verbose == 'v' and not verbose == 'verbose':
            verbose = None
        return name, verbose

    async def _parse_summoner(self, string):
        name, region = DiscoUtils.parse_into_two(string, ' ?-')
        if region is None:
            region = self.DEFAULT_REGION
        elif region not in self.REGIONS:
            if region + '1' not in self.REGIONS:
                await self.bot.say('Region **{}** does not exist.'.format(region))
                return name, None
            region += '1'

        return name, region

    async def _find_summoner(self, name, region):
        try:
            summoner = self.watcher.summoner.by_name(region, name)
            return summoner
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                await self.bot.say('**{}** was not found in **{}**.'.format(name, region))
            elif e.response.status_code == 429:
                print('Retrying...')
            else:
                await self.bot.say('Unknown error occurred. Status code {}.'
                                   .format(e.response.status_code))
        except Exception as e:
            DiscoUtils.generic_except(e)

    async def _base_op(self, name):
        if name is None:
            await self.bot.say('Please put a summoner name.')
            return None, None
        name, region = await self._parse_summoner(name)
        if region is None:
            return None, None
        return name, region


