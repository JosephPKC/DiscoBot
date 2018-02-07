# region Imports
import sqlite3 as sql
# endregion


class DatabaseManager:
    def __init__(self, lol_path, cache):
        self.cache = cache
        self.lol_con = None
        try:
            self.lol_con = sql.connect(lol_path)
            self.lol_con.cursor().execute('PRAGMA foreign_keys = 1;')
            self.lol_con.commit()
        except sql.Error as e:
            print('ERROR: {}'.format(e.args[0]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.lol_con:
            self.lol_con.close()