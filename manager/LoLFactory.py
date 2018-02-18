from manager import LoLDatabase as Database, LoLDataDragon as Datadragon
from structure import LoLMatchDetailed, LoLMatchList, LoLPlayer
from value import GeneralValues as Gv, LeagueValues as Lv


# region Methods
def __check_params(params):
    if params is None:
        return False
    for p in params:
        if p is None:
            return False
    return True


def __get_key_values(obj, key):
    try:
        return obj[key]
    except KeyError:
        return None


def __get_participant_id_from_match(participants, account_id):
    for p in participants:
        if p['player']['accountId'] == account_id:
            return p['participantId']
    return -1


def __get_team_id(participant_id, number_of_players):
    return 100 if participant_id <= number_of_players // 2 else 200


def __get_queue_string(queue_results):
    return '{}: {}{}'.format(queue_results['map'], queue_results['mode'],
                             '' if queue_results['extra'] is None else ' {}'.format(queue_results['extra']))



# region Factory Methods
def create_match(region, match):
    season = Database.select_season(match['seasonId'])['name']
    queue_results = Database.select_queue(match['queueId'], all=True)
    queue = __get_queue_string(queue_results)
    duration = Gv.get_minutes_seconds(match['gameDuration'])
    duration = '{:02d}:{:02d}'.format(duration[0], duration[1])
    teams = []
    for i in range(0, 2):
        teams.append(__build_match_team(region, match, i))
    url = Lv.get_match_history_url(
        region, match['platformId'], match['gameId']
    )

    return LoLMatchDetailed.LoLMatchDetailed(
        Lv.region_string_map[region], match['gameId'], season, queue, duration, teams, queue_results['hasLanes'],
        queue_results['hasTowers'], queue_results['hasTowers'], queue_results['hasDragons'],
        queue_results['hasBarons'], queue_results['hasHeralds'], queue_results['hasVilemaws'],
        queue_results['hasScore'], queue_results['hasVision'], queue_results['hasMonsters'], url
    )


def create_match_list_recent(region, player, matchlist):
    url = Lv.get_op_gg_url(region, player['name'])
    matches = []
    for m in matchlist:
        matches.append(__build_match_list_recent_match(player, m))
    return LoLMatchList.LoLMatchList(
        Lv.region_string_map[region], player['name'], url, matches
    )


def create_player(region, player, ranks, matchlist, masteries):
    # Check Params
    if not __check_params([region, player, ranks, matchlist, masteries]):
        raise ValueError('At least one param is None.')
    url = Lv.get_op_gg_url(region, player['name'])
    # Create Ranks
    ranks_list = []
    for r in ranks:
        ranks_list.append(__build_player_rank(r))
    # Create Masteries
    masteries_list = []
    for m in masteries[:5]:
        masteries_list.append(__build_player_masteries(m))
    # Calculate Recent Matches
    recent_games, recent_wins = len(matchlist), 0
    kills, deaths, assists, vision, cs = 0, 0, 0, 0, 0
    for m in matchlist:
        number_of_players = Database.select_queue(m['queueId'], num_of_players=True)['numOfPlayers']
        participant_id = __get_participant_id_from_match(m['participantIdentities'], player['accountId'])
        team_id = __get_team_id(participant_id, number_of_players)
        recent_wins, kills, deaths, assists, vision, cs = __add_to_player_recent_matches(
            m['teams'][team_id // 100 - 1], m['participants'][participant_id - 1]['stats'], recent_wins,
            kills, deaths, assists, vision, cs
        )
    recent_losses = recent_games - recent_wins
    if recent_games > 0:
        kills /= recent_games
        deaths /= recent_games
        assists /= recent_games
        vision /= recent_games
        cs /= recent_games
    # Create Player
    return LoLPlayer.LoLPlayer(
        player['name'], Lv.region_string_map[region], url, player['profileIconId'],
        Datadragon.get_profile_icon(player['profileIconId']), player['summonerLevel'], ranks_list,
        masteries_list, recent_games, recent_wins, recent_losses, kills, deaths, assists, vision, cs
    )
# endregion


# region Helpers
def __add_to_player_recent_matches(team, participant, wins, kills, deaths, assists, vision, cs):
    if team['win'] == 'Win':
        wins += 1

    kills += participant['kills']
    deaths += participant['deaths']
    assists += participant['assists']
    vision += participant['visionScore']
    cs += participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
    return wins, kills, deaths, assists, vision, cs


def __build_match_damage(total, physical, magic, true):
    return LoLMatchDetailed.LoLMatchDetailedDamagePackage(
        total, physical, magic, true
    )


def __build_match_player(region, match, index):
    player = match['participants'][index]
    timeline = player['timeline']
    stats = player['stats']
    identity = match['participantIdentities'][index]['player']

    champion = Database.select_champion(player['championId'])['name']
    spell1 = Database.select_summoner_spell(player['spell1Id'])['name']
    spell2 = Database.select_summoner_spell(player['spell2Id'])['name']
    items = []
    for i in range(0, 7):
        item = Database.select_item(stats['item{}'.format(i)])
        items.append(item['name'] if item is not None else 'None')
    damage_dealt = __build_match_damage(
        stats['totalDamageDealt'], stats['physicalDamageDealt'], stats['magicDamageDealt'], stats['trueDamageDealt']
    )
    damage_to_champs = __build_match_damage(
        stats['totalDamageDealtToChampions'], stats['physicalDamageDealtToChampions'],
        stats['magicDamageDealtToChampions'], stats['trueDamageDealtToChampions']
    )
    damage_taken = __build_match_damage(
        stats['totalDamageTaken'], stats['physicalDamageTaken'], stats['magicalDamageTaken'],
        stats['trueDamageTaken']
    )
    runes = []
    for i in range(0, 6):
        runes.append(__build_match_rune(stats, i))
    url = Lv.get_op_gg_url(region, identity['summonerName'])

    try:
        first_inhibitor = stats['firstInhibitorKill'] or stats['firstInhibitorAssist']
    except KeyError:
        first_inhibitor = False
    try:
        first_blood = stats['firstBloodKill'] or stats['firstBloodAssist']
    except KeyError:
        first_blood = False
    try:
        first_tower = stats['firstTowerKill'] or stats['firstTowerAssist']
    except KeyError:
        first_tower = False

    return LoLMatchDetailed.LoLMatchDetailedPlayerPackage(
        identity['summonerName'], champion, Lv.lane_string_map[timeline['lane']],
        Lv.role_string_map[timeline['role']], player['highestAchievedSeasonTier'], [spell1, spell2], items,
        stats['kills'], stats['deaths'], stats['assists'], stats['largestKillingSpree'], stats['largestMultiKill'],
        stats['killingSprees'], stats['doubleKills'], stats['tripleKills'], stats['quadraKills'],
        stats['pentaKills'], stats['unrealKills'], damage_dealt, stats['largestCriticalStrike'], damage_to_champs,
        stats['totalHeal'], stats['damageSelfMitigated'], stats['damageDealtToObjectives'],
        stats['damageDealtToTurrets'], stats['visionScore'], stats['timeCCingOthers'], damage_taken,
        stats['goldEarned'], stats['goldSpent'], stats['turretKills'], stats['inhibitorKills'],
        stats['totalMinionsKilled'], stats['neutralMinionsKilled'], __get_key_values(stats, 'visionWardsBoughtInGame'),
        __get_key_values(stats, 'wardsPlaced'), __get_key_values(stats, 'wardsKilled'), first_blood, first_tower,
        first_inhibitor, stats['totalPlayerScore'], runes, url
    )


def __build_match_rune(stats, index):
    rune_style = 'Primary' if index < 4 else 'Sub'
    rune_string = 'perk{}'.format(index)
    rune = Database.select_rune(stats[rune_string], True)
    style = Database.select_rune_style(stats['perk{}Style'.format(rune_style)])['name']
    var_vals = []
    time, percent, sec = True, True, True
    for i, v in enumerate(rune['vars']):
        if v is None:
            continue
        val = ''
        if rune['hasTimeVar'] and time:
            val += '{}:{:02d}'.format(stats['{}Var{}'.format(rune_string, i + 1)],
                                      stats['{}Var{}'.format(rune_string, i + 2)])
            time = False
        elif rune['hasPercentVar'] and percent:
            val += '{}%'.format(stats['{}Var{}'.format(rune_string, i + 1)])
            percent = False
        elif rune['hasSecVar'] and sec:
            val += '{}s'.format(stats['{}Var{}'.format(rune_string, i + 1)])
            sec = False
        elif rune['hasPerfectVar']:
            val += 'Perfect'
        elif time or percent or sec:
            val = '{}'.format(stats['{}Var{}'.format(rune_string, i + 1)])
        var_vals.append([v, val])

    return LoLMatchDetailed.LoLMatchDetailedRunePackage(
        rune['name'], style, var_vals
    )


def __build_match_team(region, match, index):
    team = match['teams'][index]
    bans = []
    for b in team['bans']:
        champ = Database.select_champion(b['championId'])
        bans.append(champ['name'] if champ is not None else 'None')

    start = 0 if team['teamId'] == 100 else len(match['participants']) // 2
    end = start + len(match['participants']) // 2
    players = []
    for i in range(start, end):
        players.append(__build_match_player(region, match, i))

    return LoLMatchDetailed.LoLMatchDetailedTeamPackage(
        team['teamId'], team['win'] == 'Win', team['firstBlood'], team['firstTower'], team['firstInhibitor'],
        team['firstBaron'], team['firstDragon'], team['firstRiftHerald'], team['towerKills'],
        team['inhibitorKills'], team['baronKills'], team['dragonKills'], team['vilemawKills'],
        team['riftHeraldKills'], team['dominionVictoryScore'], bans, players
    )


def __build_match_list_recent_match(player, match):
    season = Database.select_season(match['seasonId'])['name']
    queue_results = Database.select_queue(match['queueId'], all=True)
    queue = __get_queue_string(queue_results)
    participant_id = __get_participant_id_from_match(match['participantIdentities'], player['accountId'])
    participant = match['participants'][participant_id - 1]
    timeline = participant['timeline']
    stats = participant['stats']
    champion = Database.select_champion(participant['championId'])['name']

    return LoLMatchList.LoLMatchListMatchPackage(
        match['gameId'], season, queue, Lv.role_string_map[timeline['role']], Lv.lane_string_map[timeline['lane']],
        match['gameDuration'], champion, stats['kills'], stats['deaths'], stats['assists'],
        stats['totalMinionsKilled'] + stats['neutralMinionsKilled'], stats['timeCCingOthers'], stats['visionScore'],
        stats['win'], queue_results['hasLanes']
    )


def __build_player_rank(rank):
    return LoLPlayer.LoLPlayerRanksPackage(
            Lv.queue_string_map[rank['queueType']], rank['leagueName'], rank['tier'], rank['rank'], rank['wins'],
            rank['losses'], rank['leaguePoints'], rank['freshBlood'], rank['hotStreak'], rank['veteran']
        )


def __build_player_masteries(mastery):
    champion_name = Database.select_champion(mastery['championId'])['name']
    return LoLPlayer.LoLPlayerMasteriesPackage(
            champion_name, mastery['championLevel'], mastery['championPoints']
        )
# endregion
# endregion
