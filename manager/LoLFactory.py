from manager import LoLDatabase as Database, LoLDataDragon as Datadragon
from structure import LoLPlayer
from value import LeagueValues as Lv

# region Methods
def __check_params(params):
    if params is None:
        return False
    for p in params:
        if p is None:
            return False
    return True


def __get_participant_id_from_match(participants, account_id):
    for p in participants:
        if p['player']['accountId'] == account_id:
            return p['participantId']
    return -1


def __get_team_id(participant_id, number_of_players):
    return 100 if participant_id <= number_of_players // 2 else 200


# region Factory Methods
def create_player(region, player, ranks, matchlist, masteries):
    # Check Params
    if not __check_params([region, player, ranks, matchlist, masteries]):
        raise ValueError('At least one param is None.')
    # Create Ranks
    ranks_list = []
    for r in ranks:
        ranks_list.append(__create_player_rank(r))
    # Create Masteries
    masteries_list = []
    for m in masteries[:5]:
        masteries_list.append(__create_player_masteries(m))
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
        player['name'], region, Lv.region_string_map[region], player['profileIconId'],
        Datadragon.get_profile_icon(player['profileIconId']), player['summonerLevel'], ranks_list,
        masteries_list, recent_games, recent_wins, recent_losses, kills, deaths, assists, vision, cs
    )
# endregion


# region Helpers
def __create_player_rank(rank):
    return LoLPlayer.LoLPlayerRanksPackage(
            Lv.queue_string_map[rank['queueType']], rank['leagueName'], rank['tier'], rank['rank'], rank['wins'],
            rank['losses'], rank['leaguePoints'], rank['freshBlood'], rank['hotStreak'], rank['veteran']
        )


def __create_player_masteries(mastery):
    champion_name = Database.select_champion(mastery['championId'])['name']
    return LoLPlayer.LoLPlayerMasteriesPackage(
            champion_name, mastery['championLevel'], mastery['championPoints']
        )


def __add_to_player_recent_matches(team, participant, wins, kills, deaths, assists, vision, cs):
    if team['win'] == 'Win':
        wins += 1

    kills += participant['kills']
    deaths += participant['deaths']
    assists += participant['assists']
    vision += participant['visionScore']
    cs += participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
    return wins, kills, deaths, assists, vision, cs
# endregion
# endregion
