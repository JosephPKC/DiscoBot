import sqlite3 as sql
from manager import CacheManager as Cache
from value import GeneralValues as Gv

# region Fields
__conn = None
# endregion


# region Methods
def __print_nothing_found(query):
    print('NOTHING: {}'.format(query))


def __select(query):
    cur = __conn.cursor()
    cached = Cache.retrieve(query, Cache.CacheType.DB)
    if cached is None:
        cur.execute(query)
        cached = cur.fetchone()
        if cached is None:
            __print_nothing_found(query)
            return None
        Cache.add(query, cached, Cache.CacheType.DB)
    return cached


def end():
    if __conn:
        __conn.close()


def init():
    global __conn
    try:
        __conn = sql.connect(Gv.lol_db_path)
        __conn.cursor().execute('PRAGMA foreign_keys = 1;')
        __conn.commit()
    except sql.Error as e:
        print('Error: {}'.format(e.args[0]))
        

def select_champion(champion_id, json_name=False):
    if champion_id is None:
        return None
    query = 'SELECT Name, JsonName FROM Champions WHERE Id = {};'.format(str(champion_id))
    cached = __select(query)
    results = {
        'name': cached[0]
    }
    if json_name:
        results['jsonName'] = cached[1]
    return results


def select_champion_inverted(champion_name):
    if champion_name is None:
        return None
    clean_name = champion_name.lower().replace(' ', '').replace('\'', '')
    query = 'SELECT Id FROM Champions WHERE replace(replace(lower(Name), \' \', \'\'), \'\'\'\', \'\') = \'{}\';'\
        .format(clean_name)
    cached = __select(query)
    results = {
        'id': cached[0]
    }
    return results


def select_item(item_id):
    if item_id is None:
        return None
    query = 'SELECT Name FROM Items WHERE Id = {};'.format(str(item_id))
    cached = __select(query)
    results = {
        'name': cached[0]
    }
    return results


def select_item_inverted(item_name):
    if item_name is None:
        return None
    clean_name = item_name.lower().replace(' ', '').replace('\'', '')
    query = 'SELECT Id FROM Items WHERE replace(replace(lower(Name), \' \', \'\'), \'\'\'\', \'\') = \'{}\';'\
        .format(clean_name)
    cached = __select(query)
    results = {
        'id': cached[0]
    }
    return results


def select_queue(queue_id, all=False, num_of_players=False, has_lanes=False, has_score=False, has_towers=False,
                 has_dragons=False, has_barons=False, has_heralds=False, has_vilemaws=False, has_monsters=False,
                 has_vision=False):
    if queue_id is None:
        return None
    query = 'SELECT Map, Mode, Extra, NumOfPlayers, HasLanes, HasScore, HasTowers, HasDragons, HasBarons, ' \
            'HasHeralds, HasVileMaws, HasMonsters, HasVision FROM QueueDescriptions WHERE Id = {};'\
        .format(str(queue_id))
    cached = __select(query)
    result = {
        'map': cached[0],
        'mode': cached[1],
        'extra': cached[2]
    }
    if all or num_of_players:
        result['numOfPlayers'] = cached[3]
    if all or has_lanes:
        result['hasLanes'] = cached[4]
    if all or has_score:
        result['hasScore'] = cached[5]
    if all or has_towers:
        result['hasTowers'] = cached[6]
    if all or has_dragons:
        result['hasDragons'] = cached[7]
    if all or has_barons:
        result['hasBarons'] = cached[8]
    if all or has_heralds:
        result['hasHeralds'] = cached[9]
    if all or has_vilemaws:
        result['hasVilemaws'] = cached[10]
    if all or has_monsters:
        result['hasMonsters'] = cached[11]
    if all or has_vision:
        result['hasVision'] = cached[12]
    return result


def select_rune(rune_id, has_vars=False):
    if rune_id is None:
        return None
    query = 'SELECT Name, Var1, Var2, Var3, HasTimeVar, HasPercentVar, HasSecVar, HasPerfectVar ' \
            'FROM Runes WHERE Id = {};'.format(str(rune_id))
    cached = __select(query)
    results = {
        'name': cached[0],
    }
    if has_vars:
        results['vars'] = [cached[1], cached[2], cached[3]]
        results['hasTimeVar'] = cached[4]
        results['hasPercentVar'] = cached[5]
        results['hasSecVar'] = cached[6]
        results['hasPerfectVar'] = cached[7]
    return results


def select_rune_style(rune_style_id):
    if rune_style_id is None:
        return None
    query = 'SELECT Name FROM RuneTrees WHERE Id = {};'.format(str(rune_style_id))
    cached = __select(query)
    results = {
        'name': cached[0]
    }
    return results


def select_season(season_id):
    if season_id is None:
        return None
    query = 'SELECT Name FROM Seasons WHERE Id = {};'.format(str(season_id))
    cached = __select(query)
    results = {
        'name': cached[0]
    }
    return results


def select_summoner_spell(summoner_spell_id):
    if summoner_spell_id is None:
        return None
    query = 'SELECT Name FROM SummonerSpells WHERE Id = {};'.format(str(summoner_spell_id))
    cached = __select(query)
    results = {
        'name': cached[0]
    }
    return results
# endregion
