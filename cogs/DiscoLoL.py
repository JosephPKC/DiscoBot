import re
import requests
import json

import riotwatcher
from discord.ext import commands

import DiscoUtils
from helpers import DiscoFile

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

#TODO: Get version number for lol_status maybe to stay up to date
#TODO: Maybe move the constants to Database
#TODO: champion stats needs access to another API to get champion play stats
#TODO: Builds command to show the top builds needs access to another API maybe champion.gg?
#TODO: Need some kind of caching to cache the messages, so that it doesn't keep recomputing them when it was done recently (Store the type, data, and timestamp) - One for data (heavy) for displaying (like messages, etc), and one for db calls (lite) for internal use
#TODO: Move the downloading to a donwload manager, that simply downloads the given url, and saves it as some file. (It will place requests into a queue, and it will in a loop, download files one by one)
#TODO: For all: Move all discord.py and other non-std stuff into a try block (more pythony that way)
#ALL FILES should be in a folder with the version number
#MAYBE: Instead of downloading images and uploading them to discord, maybe just post the direct link?
#   Discord's embedded imaging will automatically show the image anyways. This saves us processing power and bandwidth

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
    ITEMS = {
        'doran\'sblade': '1055',
        'doransblade': '1055',
        'bootsofspeed': '1001',
        'faeriecharm': '1004',
        'rejuvenationbead': '1006',
        'giant\'sbelt': '1011',
        'giantsbelt': '1011',
        'cloakofagility': '1018',
        'blastingwand': '1026',
        'sapphirecrystal': '1027',
        'rubycrystal': '1028',
        'clotharmor': '1029',
        'chainvest': '1031',
        'null-magicmantle': '1033',
        'nullmagicmantle': '1033',
        'longsword': '1036',
        'pickaxe': '1037',
        'b.f.sword': '1038',
        'bfsword': '1038',
        'hunter\'stalisman': '1039',
        'hunterstalisman': '1039',
        'hunter\'smachete': '1041',
        'huntersmachete': '1041',
        'dagger': '1042',
        'recurvebow': '1043',
        'brawler\'sgloves': '1051',
        'brawlersgloves': '1051',
        'amplifyingtome': '1052',
        'vampiricscepter': '1053',
        'doran\'sshield': '1054',
        'doransshield': '1054',
        'doran\'sring': '1056',
        'doransring': '1056',
        'negatroncloak': '1057',
        'needlesslylargerod': '1058',
        'thedarkseal': '1082',
        'darkseal': '1082',
        'cull': '1083',
        'enchantment:warrior': '1400',
        'enchantmentwarrior': '1400',
        'warrior': '1400',
        'enchantment:cinderhulk': '1041',
        'enchantmentcinderhulk': '1401',
        'cinderhulk': '1401',
        'enchantment:runicechoes': '1402',
        'enchantmentrunicechoes': '1402',
        'runicechoes': '1402',
        'enchantment:bloodrazor': '1416',
        'enchantmentbloodrazor': '1416',
        'bloodrazor': '1416',
        'healthpotion': '2003',
        'potion': '2003',
        'pot': '2003',
        'totalbiscuitofrejuvenation': '2009',
        'biscuit': '2009',
        'elixirofskill': '2011',
        'kircheisshard': '2015',
        'refillablepotion': '2031',
        'hunter\'spotion': '2032',
        'hunterspotion': '2032',
        'corruptingpotion': '2033',
        'rubysightstone': '2045',
        'oracle\'sextract': '2047',
        'oraclesextract': '2047',
        'sightstone': '2049',
        'explorer\'sward': '2050',
        'explorersward': '2040',
        'guardian\'shorn': '2051',
        'guardianshorn': '2051',
        'poro-snax': '2052',
        'porosnax': '2052',
        'raptorcloak': '2053',
        'dietporo-snax': '2054',
        'dietporosnax': '2054',
        'controlward': '2055',
        'elixirofiron': '2138',
        'elixirofsorcery': '2139',
        'elixirofwrath': '2140',
        'eyeofthewatchers': '2301',
        'eyeoftheoasis': '2302',
        'eyeoftheequinox': '2303',
        'abyssalmask': '3001',
        'archangel\'sstaff': '3003',
        'archangelsstaff': '3003',
        'manamune': '3004',
        'berserker\'sgloves': '3006',
        'berserkersgloves': '3006',
        'archangel\'sstaff(quickcharge)': '3007',
        'archangelsstaffquickcharge': '3007',
        'manamune(quickcharge': '3008',
        'manamunequickcharge': '3008',
        'bootsofswiftness': '3009',
        'catalystofaeons': '3010',
        'sorcerer\'sshoes': '3020',
        'sorcerersshoes': '3020',
        'frozenmallet': '3022',
        'glacialshroud': '3024',
        'iceborngauntlet': '3025',
        'guardianangel': '3026',
        'rodofages': '3027',
        'chaliceofharmony': '3028',
        'rodofages(quickcharge)': '3029',
        'rodofagesquickcharge': '3029',
        'hextechglp-800': '3030',
        'hextechglp800': '3030',
        'infinityedge': '3031',
        'mortalreminder': '3033',
        'giantlsyaer': '3034',
        'lastwhisper': '3035',
        'lorddominik\'sregards': '3036',
        'lorddominiksregards': '3036',
        'seraph\'sembrace': '3040',
        'seraphsembrace': '3040',
        'mejai\'ssoulstealer': '3041',
        'mejaissoulstealer': '3041',
        'muramana': '3042',
        'phage': '3044',
        'phantomdancer': '3046',
        'ninjatabi': '3047',
        'zeke\'sconvergence': '3050',
        'zekesconvergence': '3050',
        'jaurim\'sfist': '3052',
        'jaurimsfist': '3052',
        'sterak\'sgage': '3053',
        'steraksgage': '3053',
        'ohmwrecker': '3056',
        'sheen': '3057',
        'bannerofcommand': '3060',
        'spiritvisage': '3065',
        'kindlegem': '3067',
        'sunfirecape': '3068',
        'talismanofascension': '3069',
        'tearofthegoddess': '3070',
        'theblackcleaver': '3071',
        'blackcleaver': '3071',
        'thebloodthirster': '3072',
        'bloodthirster': '3072',
        'tearofthegoddess(quickcharge)': '3073',
        'tearofthegoddessquickcharge': '3073',
        'ravenoushydra': '3074',
        'thornmail': '3075',
        'bramblevest': '3076',
        'tiamat': '3077',
        'trinityforce': '3078',
        'warden\'smail': '3082',
        'wardensmail': '3082',
        'warmog\'sarmor': '3083',
        'warmogsarmor': '3083',
        'overlord\'sbloodmail': '3084',
        'overlordsbloodmail': '3084',
        'runaan\'shurricane': '3085',
        'runaanshurricane': '3085',
        'zeal': '3086',
        'statikkshiv': '3087',
        'rabadon\'sdeathcap': '3089',
        'rabadonsdeathcap': '3089',
        'wooglet\'switchcap': '3090',
        'woogletswitchcap': '3090',
        'wit\'send': '3091',
        'witsend': '3091',
        'frostqueen\'sclaim': '3092',
        'frostqueensclaim': '3092',
        'rapidfirecannon': '3094',
        'nomad\'smedallion': '3096',
        'nomadsmedallion': '3096',
        'targon\'sbrace': '3097',
        'targonsbrace': '3097',
        'frostfang': '3098',
        'lichbane': '3100',
        'stinger': '3101',
        'banshee\'sveil': '3102',
        'bansheesveil': '3102',
        'lordvandamm\'spillager': '3104',
        'lordvandammspillager': '3104',
        'aegisofthelegion': '3105',
        'redemption': '3107',
        'fiendishcodex': '3108',
        'knight\'svow': '3109',
        'knightsvow': '3109',
        'frozenheart': '3110',
        'mercury\'streads': '3111',
        'mercurystreads': '3111',
        'guardian\'sorb': '3112',
        'guardiansorb': '3112',
        'aetherwisp': '3113',
        'forbiddenidol': '3114',
        'nashor\'stooth': '3115',
        'nashorstooth': '3115',
        'rylai\'scrystalscepter': '3116',
        'rylaiscrystalscepter': '3116',
        'bootsofmobility': '3117',
        'wickedhatchet': '3122',
        'executioner\'scalling': '3123',
        'executionerscalling': '3123',
        'guinsoo\'srageblade': '3124',
        'guinsoosrageblade': '3124',
        'caulfield\'swarhammer': '3133',
        'caulfieldswarhammer': '3133',
        'serrateddirk': '3134',
        'voidstaff': '3135',
        'hauntingguise': '3136',
        'dervishblade': '3137',
        'mercurialscimitar': '3139',
        'quicksilversash': '3140',
        'youmuu\'sghostblade': '3142',
        'youmuusghostblade': '3142',
        'randuin\'somen': '3143',
        'randuinsomen': '3143',
        'bilgewatercutlass': '3144',
        'hextechrevolver': '3145',
        'hextechgunblade': '3146',
        'gunblade': '3146',
        'duskbladeofdraktharr': '3147',
        'liandry\'storment': '3151',
        'liandrystorment': '3151',
        'hextechprotobelt-01': '3152',
        'hextechprotobelt01': '3152',
        'protobelt': '3152',
        'bladeoftheruinedking': '3153',
        'hexdrinker': '3155',
        'mawofmalmortius': '3156',
        'zhonya\'shourglass': '3157',
        'zhonyashourglass': '3157',
        'ionianbootsoflucidity': '3158',
        'morellonomicon': '3165',
        'moonflairspellblade': '3170',
        'athene\'sunholygrail': '3174',
        'athenesunholygrail': '3174',
        'headofkha\'zix': '3175',
        'headofkhazix': '3175',
        'sanguineblade': '3181',
        'guardian\'shammer': '3184',
        'guardianshammer': '3184',
        'thelightbringer': '3185',
        'lightbringer': '3185',
        'arcanesweeper': '3187',
        'locketoftheironsolari': '3190',
        'locket': '3190',
        'seeker\'sarmguard': '3191',
        'seekersarmguard': '3191',
        'gargoylestoneplate': '3193',
        'adaptivehelm': '3194',
        'thehexcoremk-1': '3196',
        'thehexcoremk1': '3196',
        'hexcoremk1': '3196',
        'thehexcoremk-2': '3197',
        'thehexcoremk2': '3197',
        'hexcoremk2': '3197',
        'perfecthexcore': '3198',
        'prototypehexcore': '3200',
        'spectre\'scowl': '3211',
        'spectrescowl': '3211',
        'mikael\'scrucible': '3222',
        'mikaelscrucible': '3222',
        'poacher\'sdirk': '3252',
        'poachersdirk': '3252',
        'luden\'secho': '3285',
        'ludensecho': '3285',
        'ancientcoin': '3301',
        'coin': '3301',
        'relicshield': '3302',
        'spellthief\'sedge': '3303',
        'spellthiefsedge': '3303',
        'spellthiefs' : '3303',
        'wardingtotem(trinket': '3340',
        'wardingtotem': '3340',
        'sweepinglens(trinket)': '3341',
        'sweepinglens': '3341',
        'soulanchor(trinket': '3345',
        'soulanchor': '3        345',
        'greaterstealthtotem(trinket': '3361',
        'greaterstealthtotem': '3361',
        'greatervisiontotem(trinket)': '3362',
        'greatervisiontotem': '3362',
        'farsightalteration(trinket)': '3363',
        'farsightalteration': '3363',
        'oraclealteration': '3364',
        'moltenedge': '3371',
        'forgefirecape': '3373',
        'rabadon\'sdeathcrown': '3374',
        'rabadonsdeathcrown': '3374',
        'infernalmask': '3379',
        'theobsidiancleaver': '3380',
        'obsidiancleaver': '3380',
        'salvation': '3382',
        'circletoftheironsolari': '3383',
        'trinityfusion': '3384',
        'wooglet\'switchcrown': '3385',
        'woogletswitchcrown': '3385',
        'faceofthemountain': '3401',
        'goldentrascendence': '3460',
        'seerstone(trinket': '3462',
        'seerstone': '3462',
        'ardentcenser': '3504',
        'essencereaver': '3508',
        'zz\'rotportal': '3512',
        'zzrotportal': '3512',
        'eyeoftheherald': '3513',
        'theblackspear': '3599',
        'siegeteleport': '3630',
        'siegeballista': '3631',
        'tower:beamofruination': '3634',
        'towerbeamofruination': '3634',
        'beamofruination': '3634',
        'portpad': '3635',
        'tower:stormbulwark': '3636',
        'towerstormbulwark': '3636',
        'stormbulwark': '3636',
        'flashzone': '3640',
        'vanguardbanner': '3641',
        'entropyfield': '3643',
        'shieldtotem': '3647',
        'siegesightwarder': '3649',
        'frostedsnax': '3680',
        'superspicysnax': '3681',
        'espressosnax': '3682',
        'rainbowsnaxpartypack!': '3683',
        'rainbowsnaxpartypack': '3683',
        'cosmicshackle': '3690',
        'singularitylantern': '3691',
        'darkmatterscythe': '3692',
        'gravityboots': '3693',
        'cloakofstars': '3694',
        'darkstarsigil': '3695',
        'stalker\'sblade': '3706',
        'stalkersblade': '3706',
        'tracker\'sblade': '3711',
        'trackersblade': '3711',
        'skirmisher\'ssabre': '3715',
        'skirmisherssabre': '3715',
        'deadman\'splate': '3742',
        'deadmansplate': '3742',
        'titanichydra': '3748',
        'bami\'scinder': '3751',
        'bamiscinder': '3751',
        'righteousglory': '3800',
        'crystallinebracer': '3801',
        'lostchapter': '3802',
        'death\'sdance': '3812',
        'deathsdance': '3812',
        'edgeofnight': '3814',
        'fireatwill': '3901',
        'death\'sdaughter': '3902',
        'deathsdaughter': '3902',
        'raisemorale': '3903',

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
    URLS = {
        'Champions': 'http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion/'.format(VERSION),
        'Splashes': 'http://ddragon.leagueoflegends.com/cdn/img/champion/splash/',
        'Icons': 'http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/'.format(VERSION),
        'Items': 'http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/item'.format(VERSION),
        'Item Icons': 'http://ddragon.leagueoflegends.com/cdn/{}/img/item/'.format(VERSION)
    }
    PATHS = {
        'Champions': 'data\\{}\\lol_champions\\'.format(VERSION),
        'Splashes': 'data\\{}\\lol_splash\\'.format(VERSION),
        'Icons': 'data\\{}\\lol_icons\\'.format(VERSION),
        'Items': 'data\\{}\\lol\\items.json'.format(VERSION),
        'Item Icons': 'data\\{}\\lol_item_icons\\'.format(VERSION)
    }
    OPTS = {
        'Champions': ['l', 't', 's', 'sk', 'st', 'i', 'all']
    }
    VARS = {
        'bonusattackdamage': 'Bonus AD',
        'spelldamage': 'AP',
        'attackdamage': 'AD'
    }
    def __init__(self, bot, riot):
        self.bot = bot
        self.watcher = riotwatcher.RiotWatcher(riot)
        self.items = None

    @commands.command(name='summoner', aliases=[], pass_context=True,
                      help='Display info on the summoner')
    async def summoner(self, ctx, *, input: str = None):
        # Do basic checks on the string
        name, region = await self.__check_summoner(input)
        if name == None:
            return
        # print(name, region)

        # Get summoner info
        try:
            # Get summoner info from Watcher
            summoner = await self.__find_summoner(name, region)
            # Get rank info for that summoner
            ranks = self.watcher.league.positions_by_summoner(region, summoner['id'])

            # Summoner rank message string
            sranks = ''
            if len(ranks) == 0: # If no ranks, then summoner is Unranked
                sranks += 'Unranked'
            else:
                # Go through each queue type the summoner is ranked in
                for r in ranks:
                    # Queue Type signifies what type this rank is for
                    sranks += self.QUEUES[r['queueType']] + '\n'
                    # League Name (for funsies)
                    sranks += '\t' + r['leagueName'] + '\n'
                    # Tier and rank (the actual info)
                    sranks += '\t' + r['tier'] + ' ' + r['rank'] + '\n'
                    # LP, W/L
                    sranks += '\t' + str(r['leaguePoints']) + ' LP, '
                    sranks += 'W/L: ' + str(r['wins']) \
                              + '/' + str(r['losses']) + '\n'
                    # Statuses in the League.
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

            # Get the Summoner's icon
            icon = str(summoner['profileIconId'])
            if not DiscoFile.find_file('{}.png'.format(icon), self.PATHS['Icons']):
                if DiscoUtils.DOWNLOAD:
                    DiscoFile.download_file(
                        self.URLS['Icons'] + icon + '.png',
                        self.PATHS['Icons'] + icon + '.png')

            # Print the info nicely
            info = '```'
            info += 'Name: ' + summoner['name'] + '\n'
            info += 'Level: ' + str(summoner['summonerLevel']) + '\n'
            info += '\nRanked Stats: \n' + sranks + '\n\n'
            info += '```\n'
            await self.bot.say(info)
            if DiscoUtils.DOWNLOAD:
                with open('data\\lol_icons\\{}_small.png'.format(icon), 'rb') as f:
                    await self.bot.send_file(ctx.message.channel, f)
            else:
                await self.bot.say(self.URLS['Icons'] + icon + '.png')
        except OSError:
            await self.bot.say('Error opening image for icon {}.'.format(summoner['profileIconId']))
        # except Exception as e:
        #     DiscoUtils.generic_except(e)

    @commands.command(name='mastery', aliases=[], pass_context=True,
                      help='Display mastery pages')
    async def mastery(self, ctx, *, name: str = None):
        name, region = await self.__check_summoner(name)
        if name == None:
            return

        try:
            summoner = await self.__find_summoner(name, region)
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
    async def champion(self, ctx, *, input: str = None):
        # Parse input string
        name, opts = self.__parse_champion(input)
        name = name.replace(' ', '').lower()
        if DiscoUtils.DEBUG:
            print('Input Parsed Name: ', name)
            print('Input Parsed Options: ', opts)
        # Check if the name is in Champions List
        if name not in self.CHAMPIONS:
            await self.bot.say('Champion **{}** does not exist.'.format(name))
            return

        # Display Champion info
        try:
            # Get the Name found in DDragon
            name = self.CHAMPIONS[name]
            if DiscoUtils.DEBUG:
                print('DDragon Name: ', name)

            # Download or open the json file
            champ = self.__get_json(name, self.PATHS['Champions'],
                                    self.URLS['Champions'])['data'][name]
            if DiscoUtils.DEBUG and DiscoUtils.VERBOSE:
                print('JSON: ', champ)

            # Begin creating the message string
            # Get the basic info
            cname = champ['name'] + ', ' + champ['title'] + '\n'
            #TODO: Cache this
            if DiscoUtils.DEBUG:
                print('NAME: ', cname)

            # The first is misc info: Name, Title, Tags, Ratings
            info = 'Tags: ' + champ['tags'][0] + ((', ' + champ['tags'][1]) if len(champ['tags']) > 1 else '') + '\n'
            istats = champ['info']
            info += 'Attack: ' + \
                     str(istats['attack']) + ', Defense: ' + \
                     str(istats['defense']) + '\nMagic: ' + \
                     str(istats['magic']) + ', Difficulty: ' + \
                     str(istats['difficulty']) + '\n\n'
            #TODO: Cache this
            if DiscoUtils.DEBUG:
                print('Info: ', info)

            # Get numerical stats.
            titles = {
                'Health': 'hp',
                'Mana': 'mp',
                'Armor': 'armor',
                'Magic Resist': 'spellblock',
                'Health Regen': 'hpregen',
                'Mana Regen': 'mpregen',
                'Attack Damage': 'attackdamage'
            }
            nstats = champ['stats']
            stats = ''
            # Instead of copy-pasting, loop for each stat
            for title, key in titles.items():
                stats += '{}: {} + {} per level\n'\
                    .format(title, nstats[key], nstats[key + 'perlevel'])

            # Attack Speed, Attack Range, and Move Speed are special
            stats += 'Attack Speed: {:.3} + {}% per level\n'\
                .format(self.__get_champion_base_as(nstats['attackspeedoffset']),
                        nstats['attackspeedperlevel'])
            stats += 'Movement Speed: ' + str(nstats['movespeed']) + '\n'
            stats += 'Attack Range: ' + str(nstats['attackrange']) + '\n'
            #TODO: Cache this
            if DiscoUtils.DEBUG:
                print('Stats: ', stats)

            # Get spells to cache. Only display if -s is enabled.
            nspells = champ['spells']
            # Get Passive (In the json, it is separate from spells)/Replace <br><br> with \n\t as Discord does not parse tags
            spells = []
            spells.append('PASSIVE  ' + champ['passive']['name'] + ': ' \
                      + self.__parse_tagged_spells(champ['passive']['description']
                          .replace('<br><br>', '\n\t'), [], [], None) + '\n\n')
            # Get the four spells. (Same idea as Passive with <br><br>)
            for i, s in enumerate(nspells):
                # Q/W/E/R Name: Description
                tspells = self.SPELLS[i] + '  ' \
                          + s['name'] + ': ' + s['description'].replace('<br><br>', '\n\t') + '\n\n'
                # EffectBurn and Vars are the value arrays
                effect_burn = s['effectBurn']
                vars = s['vars']
                if DiscoUtils.DEBUG:
                    print('Effect Burn: ', effect_burn)
                    print('Vars: ', vars)

                # Do the resource, cooldown, and range
                tspells += '\t' + 'Cost: ' \
                          + self.__parse_tagged_spells(s['resource'],
                                                       effect_burn, vars,
                                                       s['costBurn']) + '\n'
                tspells += '\t' + 'Cooldown: ' + s['cooldownBurn'] + '\n'
                tspells += '\t' + 'Range: ' + s['rangeBurn'] + '\n\n'
                # Do the tooltip
                tspells += '\t' + self.__parse_tagged_spells(s['tooltip'].replace('<br><br>', '\n\t'),
                                                            effect_burn, vars,
                                                            s['costBurn']) + '\n\n'
                spells.append(tspells)
            #TODO: Cache this
            if DiscoUtils.DEBUG:
                print('Spells: ', spells)

            # Get the lore (Just like Spells)
            lore = '\t' + champ['lore']\
                .replace('<br><br>', '\n\t')\
                .replace('<br>', '\n')\
                .replace('Â\\xa0', '') + '\n'  # Third replace is a strange artifact from Aurelion Sol's lore.
            # Split the lore (it can be very long, and Discord has a 2000 char limit per message)
            lore_fragments = [lore[i:i + 1800] for i in range(0, len(lore), 1800)]
            #TODO: Cache this
            if DiscoUtils.DEBUG:
                print('Lore: ', lore_fragments)

            # Get the tips (Just like Spells)
            ally_tips = ''
            for t in champ['allytips']:
                ally_tips += '\t' + t + '\n\n'
            enemy_tips = ''
            for t in champ['enemytips']:
                enemy_tips += '\t' + t + '\n\n'
            tips = 'Ally Tips:\n' + ally_tips + 'Enemy Tips:\n' + enemy_tips
            #TODO: Cache this
            if DiscoUtils.DEBUG:
                print('Tips: ', tips)

            # Get the splashes (of the default and skins)
            nskins = champ['skins']
            skins = {}
            for sk in nskins:
                skins[sk['name']] = sk['num']
                if DiscoUtils.DOWNLOAD:
                    if not DiscoFile.find_file('{}_{}.png'
                                                       .format(sk['name'], sk['num']),
                                               self.PATHS['Splashes']
                                                       + sk['name'] + '_{}.png'
                                                       .format(sk['num'])):
                        DiscoFile.download_file(self.URLS['Splashes']
                                                + sk['name'] + '_{}.jpg'
                                                .format(sk['num']),
                                                self.PATHS['Splashes']
                                                + sk['name'] + '_{}.png'
                                                .format(sk['num']))
            #TODO: Cache this
            if DiscoUtils.DEBUG:
                print('Skins: ', skins)

            # Load into msg list, and a splash list (Which would either be a list of image paths, or image urls)
            msg = [
                cname,
                info,
                stats,
                spells,
                tips,
                lore_fragments,
                skins
            ]
            #TODO: Cache this instead

            await self.bot.say('```' + cname + '```')
            if opts['i']:
                await self.bot.say('```' + info + '```')
            if opts['st']:
                await self.bot.say('```' + stats + '```')
            if opts['s']:
                for s in spells:
                    await self.bot.say('```' + s + '```')
            if opts['t']:
                await self.bot.say('```' + tips + '```')
            if opts['l']:
                for i, lf in enumerate(lore_fragments[:-1]):
                    await self.bot.say('```Lore pt. {}:\n'.format(i + 1)
                                       + lore_fragments[0] + '...```')
                await self.bot.say('```Lore pt. {}:\n'.format(len(lore_fragments))
                                   + lore_fragments[-1] + '```')
            if opts['sk']:
                for sname, snum in skins.items():
                    if DiscoUtils.DOWNLOAD:
                        await self.bot.say(sname + ':\n')
                        # Upload the splash
                        DiscoFile.upload_file(self.PATHS['Splashes']
                                              + '{}_{}.png'.format(name, snum))
                    else:
                        await self.bot.say(sname + ':\n' + self.URLS['Splashes']
                                           + '{}_{}.jpg'.format(name, snum))


        except requests.HTTPError as err:
            if err.response.status_code == 404:
                await self.bot.say('**{}** was not found.'.format(name))
            elif err.response.status_code == 429:
                await self.bot.say('Rate Limit reached. Retry in {} seconds.'.format(err.response.headers['Retry-After']))
            else:
                await self.bot.say('Unknown error occurred. Status code {}.'
                                   .format(err.response.status_code))

    # @commands.command(name='recommend',
    #                   help='Show recommended items for champion in map')
    # async def recommend(self, *, input: str = None):
    #     if input is None:
    #         await self.bot.say('Input needed: recommend [champion name] -(map name)')
    #
    #     # Parse input into champion, map
    #     name, map = self.__parse_champion_recommend(input)
    #     if name.lower() not in self.CHAMPIONS:
    #         await self.bot.say('Champion **{}** does not exist.'.format(name))
    #         return
    #     if map not in ['SR', 'TT', 'HA']:
    #         await self.bot.say('Map **{}** does not exist or is not supported.'.format(map))
    #         return
    #
    #     # Load json
    #     try:
    #         champ = self.__get_json(name.lower(),
    #                                 self.PATHS['Champions'],
    #                                 self.URLS['Champions'])
    #         items = champ['recommended']
    #         recommend = []
    #         mitems = []
    #         # Check for a match in maps (and valid mode), then load up the item blocks
    #         for i in items:
    #             if i['map'] == map and i['mode'] in ['CLASSIC', 'ARAM']:
    #                 mitems = i['blocks']
    #                 break
    #         # Load up each item mapping in each block
    #         for b in mitems:
    #             type = b['type']
    #             it = b['items']
    #             msg = type + ':\n'
    #             for i in it:
    #                 id = i['id']
    #                 # Load up the item json
    #                 self.watcher.static_data.item()
    #                 msg += '\t' +
    #
    #     except Exception as e:
    #         DiscoUtils.generic_except(e)

    @commands.command(name='item', pass_context=True,
                      help='Display item info')
    async def item(self, ctx, *, input: str = None):
        if input is None:
            await self.bot.say('Input needed: item [item name]')

        try:
            # Check if the item is correct or not
            input = input.replace(' ', '').lower()
            if input not in self.ITEMS:
                await self.bot.say('Item **{}** not found.'.format(input))
                return

            if self.items is None:
                # Load up the items json
                self.items = self.__get_json('', self.PATHS['Items'], self.URLS['Items'])['data']

            idata = self.items[self.ITEMS[input]]
            # Create the display message
            # Name
            name = idata['name']
            # Description
            desc = self.__clean_item_description(idata['description'])
            # Blurb
            blurb = idata['plaintext']
            # Buy/Sell
            base, total, sell = idata['gold']['base'], idata['gold']['total'], idata['gold']['sell']
            # print(base, total, sell)
            # Tags
            tags = idata['tags']

            msg = name + ': ' + blurb + '\n'
            msg += '\tBuy: ' + str(base) +  ', Total: ' + str(total) + ', Sell: ' + str(sell) + '\n'
            msg += '\t' + desc + '\n'
            if len(tags) > 0:
                msg += 'Tags: ' + tags[0]
                for t in tags[1:]:
                    msg += ', ' + t
                msg += '\n'

            #TODO: Cache this

            # Get the picture
            icon = self.ITEMS[input]
            if not DiscoFile.find_file('{}.png'.format(icon),
                                       self.PATHS['Item Icons']):
                if DiscoUtils.DOWNLOAD:
                    DiscoFile.download_file(
                        self.URLS['Item Icons'] + icon + '.png',
                        self.PATHS['Item Icons'] + icon + '.png')

            await self.bot.say('```' + msg + '```')

            if DiscoUtils.DOWNLOAD:
                DiscoFile.upload_file(self.PATHS['Item Icons'] + icon + '.png',
                                      self.bot, ctx.message.channel)
            else:
                await self.bot.say(self.URLS['Item Icons'] + icon + '.png')
        except requests.HTTPError as err:
            if err.response.status_code == 404:
                await self.bot.say('**{}** was not found.'.format(input))
            elif err.response.status_code == 429:
                await self.bot.say(
                    'Rate Limit reached. Retry in {} seconds.'.format(err.response.headers['Retry-After']))
            else:
                await self.bot.say('Unknown error occurred. Status code {}.'
                                   .format(err.response.status_code))


    @commands.command(name='info', pass_context=True)
    async def info(self, ctx, *, name: str = None):
        name, region = await self.__check_summoner(name)
        if name == None:
            return
        try:
            summoner = await self.__find_summoner(name, region)
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

    def __parse_champion(self, string):
        """
        Parses the input string for the champion command
        :param string: input string to parse
        :return: Name, Options
        """
        # Split the string on an optional space and -
        splits = re.split(' ?-', string)
        if DiscoUtils.DEBUG and DiscoUtils.VERBOSE:
            print('Splits on Champions: ', splits)
        # The first entry must be the name
        name = splits[0]
        # Create a dictionary for each possible option, set to False by default
        opts = {o: False for o in self.OPTS['Champions']}
        # If there is more than one, there are options
        if len(splits) > 1:
            # For each option:
            for s in splits[1:]:
                # If it is a valid option
                if s in self.OPTS['Champions']:
                    # Mark it as true
                    opts[s] = True
            if opts['all']:
                for o in opts.keys():
                    opts[o] = True
        # Return the name and the options
        return name, opts

    def __parse_champion_recommend(self, string):
        splits = re.split(' ?-', string)
        name = splits[0]
        # Only available maps are SR Classic, TT Classic, and HA ARAM
        if len(splits) > 1:
            map = splits[1]
        else:
            map = 'SR'
        return name, map

    def __get_champion_base_as(self, offset):
        return 0.625 / (1 + offset)

    def __parse_tagged_spells(self, description, effect_burn = [], vars = [], cost = None):
        parsed = description
        # Replace the ficky fX values with the colorings (for now)
        # fX_string = r'<span class=\"color[A-Z0-9]*\">\(+\{\{ f\d \}\}\)</span>'
        # colors = re.findall(fX_string, parsed)
        # print(colors)
        # if len(colors) > 0:
        #     for i in range(1, 10):
        #         # Get the color value
        #         color = colors[i - 1][19:26]
        #         parsed = parsed.replace(fX_string, '(+' + color + ' f' + str(i) + ')')
        # Ignore certain things
        # parsed = re.sub('\(?\+?\{\{ f\d \}\}\)?', '', parsed)
        parsed = re.sub('<[a-zA-Z0-9]*>', '', parsed)
        parsed = re.sub('</[a-zA-Z0-9]*>', '', parsed)
        parsed = re.sub('<span class="[a-zA-Z0-9]*">', '', parsed)
        parsed = re.sub('<span class=\"[a-zA-Z0-9]*\">', '', parsed)
        parsed = re.sub('<span class="size\d* color[A-Z0-9]*">\d*', '', parsed)
        parsed = re.sub('</span>', '', parsed)
        # Might be best to just ignore the detailed spells for now, until the tooltips thing is sorted out
        # Replace health, armor, and magic resist scalings.
        # FFFF00 = Armor
        # FF3300 = Health
        # FF0000 = ?
        # FF00FF = Magic Resist
        # Do Effect Burn Substitution first
        for i in range(1, len(effect_burn)):
            parsed = parsed.replace('{{ e' + str(i) + ' }}', effect_burn[i])
        # Next do Vars
        for i in range(0, len(vars)): # Vars do not have a null at index 0 like effectburn
            key = 'a' + str(i + 1)
            if DiscoUtils.DEBUG:
                print('Vars Key in Parse Tagged Spells: ', key)
            # Get the var with corresponding key (if any)
            for v in vars:
                if v['key'] == key:
                    parsed = parsed.replace('{{ ' + key + ' }}',
                                            str(v['coeff'] * 100)
                                            + '% of ' + self.VARS[v['link']])
        # Finally do cost
        if cost is not None:
            parsed = parsed.replace('{{ cost }}', cost)

        return parsed

    def __clean_item_description(self, item):
        item = item.replace('<br>', '\n\t')
        item = re.sub('\</?[a-zA-Z0-9 #=\']*\>', '', item)
        return item

    async def __parse_summoner(self, string):
        name, region = DiscoUtils.parse_into_two(string, ' ?-')
        if region is None:
            region = self.DEFAULT_REGION
        elif region not in self.REGIONS:
            if region + '1' not in self.REGIONS:
                await self.bot.say('Region **{}** does not exist.'.format(region))
                return name, None
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
                await self.bot.say('Unknown error occurred. Status code {}.'
                                   .format(e.response.status_code))
        except Exception as e:
            DiscoUtils.generic_except(e)

    async def __check_summoner(self, name):
        if name is None:
            await self.bot.say('Please put a summoner name.')
            return None, None
        name, region = await self.__parse_summoner(name)
        if region is None:
            return None, None
        return name, region

    def __get_json(self, name, path, url = None):
        """
        Checks to see if there is a json downloaded. If not, download it. Open the json.
        :param name: Name of the json
        :param path: Path to the directory of the json. Should be data\{VERSION}\{TYPE}\
        :param url: URL to download if not found. Can be None.
        :return: A dict containing json data, or None.
        """
        # Check if the json exists
        if not DiscoFile.find_file('{}.json'.format(name), path):
            if url is None: # If it does not exist, and no URL, do nothing
                return None
            # Download the json file
            DiscoFile.download_file(url + name + '.json', path + name + '.json')
        # Open the json file
        with open(path + name + '.json') as f:
            j = json.loads(f.read())
        return j
