from value import LeagueValues as Lv, GeneralValues as Gv


class LoLBuildOrder:
    def __init__(self, region, name, match_id, champion, events, url):
        self.url = url
        self.region = region
        self.name = name
        self.match_id = match_id
        self.champion = champion
        self.events = events

    def embed(self, ctx):
        embeds = []
        # Overview and Brief
        embed = Gv.create_embed(Lv.default_embed_color,
                                'Overview of items built in Match __**{}**__ in __**{}**__.\n'
                                '__**{}**__ played __**{}**__.'
                                .format(self.match_id, self.region, self.name, self.champion),
                                ctx.message.author)
        embed.set_author(name='{} in Match {}'.format(self.name, self.match_id), url=self.url)
        embeds.append(embed)
        # For each set of 50 events
        embed = Gv.create_embed(Lv.default_embed_color,
                                'Overview of items built in Match __**{}**__ in __**{}**__.\n'
                                '__**{}**__ played __**{}**__.'
                                .format(self.match_id, self.region, self.name, self.champion),
                                ctx.message.author)
        for i, e in enumerate(self.events):
            embed.add_field(name='@{}'.format(e.time),
                            value=self.__get_event_string(e),
                            inline=False)
            if i % Lv.match_timeline_split >= Lv.match_timeline_split - 1:
                embeds.append(embed)
                embed = Gv.create_embed(Lv.default_embed_color,
                                        'Overview of items built in Match __**{}**__ in __**{}**__.\n'
                                        '__**{}**__ played __**{}**__.'
                                        .format(self.match_id, self.region, self.name, self.champion),
                                        ctx.message.author)
                embed.set_author(name='{}'.format(self.match_id), url=self.url)
            elif len(self.events) - i == 1:
                embeds.append(embed)
        return embeds

    @staticmethod
    def __get_event_string(event):
        string = ''
        if event.category == 'ITEM_PURCHASED':
            string += '**Purchased/Got:** {}\n'.format(event.item)
        else:
            string += '**Sold/Used/Removed:** {}\n'.format(event.item)
        return string


class LoLBuildOrderEventPackage:
    def __init__(self, category, time, item):
        self.category = category
        self.time = time
        self.item = item
