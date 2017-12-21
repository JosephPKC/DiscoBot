import datetime

class CacheManager:
    def __init__(self):
        self.db_cache = {} # db_cache maps sql queries to query results. They have a high time to live
        self.api_cache = {} # api_cache maps a dictionary of keys to api results. They have a short time to live

        # In minutes
        self.db_ttl = 300
        self.api_ttl = 30


    def get_db(self, query):
        # Check if the query exists
        if not self.check_if_have_db(query):
            return None
        # Check if the ttl has not been exceeded
        if not self.__check_if_ttl_db(query):
            return None
        # Get the result
        return self.db_cache[query][0]

    def get_api(self, key_terms):
        # Check if the query exists
        if not self.check_if_have_api(key_terms):
            return None
        # Check if the ttl has not been exceeded
        if not self.__check_if_ttl_api(key_terms):
            return None
        # Get the result
        return self.api_cache[key_terms][0]

    def cache_db(self, query, result):
        self.db_cache[query] = [result, datetime.datetime.now()]

    def cache_api(self, key_terms, result):
        self.api_cache[key_terms] = [result, datetime.datetime.now()]

    def check_if_have_db(self, query):
        return query in self.db_cache

    def check_if_have_api(self, key_terms):
        return key_terms in self.api_cache

    def __check_if_ttl_db(self, query):
        mins = (datetime.datetime.now() - self.db_cache[query][1]).total_seconds() / 60
        return mins <= self.db_ttl

    def __check_if_ttl_api(self, key_terms):
        mins = (datetime.datetime.now() - self.api_cache[key_terms][1]).total_seconds() / 60
        return mins <= self.api_ttl


