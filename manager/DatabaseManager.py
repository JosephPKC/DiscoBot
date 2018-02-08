# region Imports
import sqlite3 as sql

from value import GeneralValues as Gv
from manager import CacheManager
# endregion


class DatabaseManager:
    def __init__(self, lol_path, cache):
        self.__cache = cache
        self.__lol_con = None
        try:
            self.__lol_con = sql.connect(lol_path)
            self.__lol_con.cursor().execute('PRAGMA foreign_keys = 1;')
            self.__lol_con.commit()
        except sql.Error as e:
            print('ERROR: {}'.format(e.args[0]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__lol_con:
            self.__lol_con.close()

    # region LoL Select
    def select_lol_queue(self, queue_id, num_of_players=False, has_lanes=False,
                         has_score=False, has_towers=False, has_dragons=False,
                         has_barons=False, has_heralds=False, has_vilemaws=False,
                         has_monsters=False, has_vision=False):
        if queue_id is None:
            return None
        cur = self.__lol_con.cursor()
        query = 'SELECT Map, Mode, Extra, NumOfPlayers, ' \
                'HasLanes, HasScore, HasTowers, HasDragons, ' \
                'HasBarons, HasHeralds, HasVileMaws, HasMonsters, ' \
                'HasVision FROM QueueDescriptions WHERE Id = {};'\
            .format(str(queue_id))
        cached = self.__cache.retrieve(query, CacheManager.CacheType.DB)
        if cached is None:
            Gv.print_cache(query, False)
            cur.execute(query)
            cached = cur.fetchone()
            if cached is None:
                print('Nothing found with {}'.format(query))
                return None
            self.__cache.add(query, cached, CacheManager.CacheType.DB)
        else:
            Gv.print_cache(cached, True)
        result = {
            'map': cached[0],
            'mode': cached[1],
            'extra': cached[2]
        }
        if num_of_players:
            result['numOfPlayers'] = cached[3]
        if has_lanes:
            result['hasLanes'] = cached[4]
        if has_score:
            result['hasScore'] = cached[5]
        if has_towers:
            result['hasTowers'] = cached[6]
        if has_dragons:
            result['hasDragons'] = cached[7]
        if has_barons:
            result['hasBarons'] = cached[8]
        if has_heralds:
            result['hasHeralds'] = cached[9]
        if has_vilemaws:
            result['hasVilemaws'] = cached[10]
        if has_monsters:
            result['hasMonsters'] = cached[11]
        if has_vision:
            result['hasVision'] = cached[12]
        return result

    def select_lol_season(self, season_id):
        if season_id is None:
            return None
        cur = self.__lol_con.cursor()
        query = 'SELECT Name FROM Seasons WHERE Id = {};'\
            .format(str(season_id))
        cached = self.__cache.retrieve(query, CacheManager.CacheType.DB)
        if cached is None:
            Gv.print_cache(query, False)
            cur.execute(query)
            cached = cur.fetchone()
            if cached is None:
                print('Nothing found with {}'.format(query))
                return None
            self.__cache.add(query, cached, CacheManager.CacheType.DB)
        else:
            Gv.print_cache(query, True)
        return cached[0]

    def select_lol_champion(self, champion_id):
        if champion_id is None:
            return None
        cur = self.__lol_con.cursor()
        query = 'SELECT Name FROM Champions WHERE Id = {};'\
            .format(str(champion_id))
        cached = self.__cache.retrieve(query, CacheManager.CacheType.DB)
        if cached is None:
            Gv.print_cache(query, False)
            cur.execute(query)
            cached = cur.fetchone()
            if cached is None:
                print('Nothing found with {}'.format(query))
                return None
            self.__cache.add(query, cached, CacheManager.CacheType.DB)
        else:
            Gv.print_cache(query, True)
        return cached[0]

    def select_lol_summoner_spell(self, summoner_spell_id):
        if summoner_spell_id is None:
            return None
        cur = self.__lol_con.cursor()
        query = 'SELECT Name FROM SummonerSpells WHERE Id = {};'\
            .format(str(summoner_spell_id))
        cached = self.__cache.retrieve(query, CacheManager.CacheType.DB)
        if cached is None:
            Gv.print_cache(query, False)
            cur.execute(query)
            cached = cur.fetchone()
            if cached is None:
                print('Nothing found with {}'.format(query))
                return None
            self.__cache.add(query, cached, CacheManager.CacheType.DB)
        else:
            Gv.print_cache(query, True)
        return cached[0]

    def select_lol_item(self, item_id):
        if item_id is None:
            return None
        cur = self.__lol_con.cursor()
        query = 'SELECT Name FROM Items WHERE Id = {};'\
            .format(str(item_id))
        cached = self.__cache.retrieve(query, CacheManager.CacheType.DB)
        if cached is None:
            Gv.print_cache(query, False)
            cur.execute(query)
            cached = cur.fetchone()
            if cached is None:
                print('Nothing found with {}'.format(query))
                return None
            self.__cache.add(query, cached, CacheManager.CacheType.DB)
        else:
            Gv.print_cache(query, True)
        return cached[0]

    def select_lol_rune_style(self, rune_style_id):
        if rune_style_id is None:
            return None
        cur = self.__lol_con.cursor()
        query = 'SELECT Name FROM RuneTrees WHERE Id = {};'\
            .format(str(rune_style_id))
        cached = self.__cache.retrieve(query, CacheManager.CacheType.DB)
        if cached is None:
            Gv.print_cache(query, False)
            cur.execute(query)
            cached = cur.fetchone()
            if cached is None:
                print('Nothing found with {}'.format(query))
                return None
            self.__cache.add(query, cached, CacheManager.CacheType.DB)
        else:
            Gv.print_cache(query, True)
        return cached[0]

    def select_lol_rune(self, rune_id):
        if rune_id is None:
            return None
        cur = self.__lol_con.cursor()
        query = 'SELECT Name, Var1, Var2, Var3, ' \
                'HasTimeVar, HasPercentVar, HasSecVar, HasTimingVar ' \
                'FROM Runes WHERE Id = {};'\
            .format(str(rune_id))
        cached = self.__cache.retrieve(query, CacheManager.CacheType.DB)
        if cached is None:
            Gv.print_cache(query, False)
            cur.execute(query)
            cached = cur.fetchone()
            if cached is None:
                print('Nothing found with {}'.format(query))
                return None
            self.__cache.add(query, cached, CacheManager.CacheType.DB)
        else:
            Gv.print_cache(query, True)
        results = {
            'name': cached[0],
            'vars': [cached[1], cached[2], cached[3]],
            'hasTimeVar': cached[4],
            'hasPercentVar': cached[5],
            'hasSecVar': cached[6],
            'hasTimingVar': cached[7]
        }
        return results
    # endregion
