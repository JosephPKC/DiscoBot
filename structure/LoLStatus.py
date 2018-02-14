# region Imports
from value import LeagueValues as Lv
# endregion


class LoLStatusServiceIncident:
    def __init__(self, content):
        self.content = content

    def to_str(self, depth=0):
        tabs = '\t' * depth
        return '{}{}\n'.format(tabs, self.content)


class LoLStatusService:
    def __init__(self, name, status, incidents_list):
        self.name = name
        self.status = status
        self.incidents_list = incidents_list

    def to_str(self, depth=0):
        tabs = '\t' * depth
        string = '{}Service: {}\n'.format(tabs, self.name)
        string += '{}Status: {}\n'.format(tabs, self.status)
        if self.incidents_list:
            string += '{}Incidents:\n'.format(tabs)
        for i in self.incidents_list:
            string += '{}\n'.format(i.to_str(depth + 1))
        return string


class LoLStatus:
    def __init__(self, region, name, services_list):
        self.region = region
        self.name = name
        self.services_list = services_list

    def to_str(self, depth=0):
        tabs = '\t' * depth
        strings = []
        string = '{}{}\n'.format(tabs, self.name)
        string += '{}Region: {}\n'.format(tabs, Lv.regions_string_map[self.region])
        strings.append(string)

        for s in self.services_list:
            strings.append('{}'.format(s.to_str(depth)))
        return strings
