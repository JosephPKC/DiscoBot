from value import GeneralValues as Gv, LeagueValues as Lv


class LoLMatchTimeline:
    def __init__(self, region, match_id, season, queue, teams, events, url):
        self.season = season
        self.queue = queue
        self.region = region
        self.match_id = match_id
        self.teams = teams
        self.events = events
        self.url = url

    def embed(self, ctx):
        embeds = []
        embed = Gv.create_embed(Lv.default_embed_color,
                                'Timeline of Match __**{}**__ in __**{}**__.'.format(self.match_id, self.region),
                                ctx.message.author)
        embed.set_author(name='Match {}'.format(self.match_id), url=self.url)
        embed.add_field(name='__Core:__',
                        value='{}\n{}\n'.format(self.season, self.queue),
                        inline=False)
        # Team info: Set victories and map players to champions.
        for t in self.teams:
            result = '**VICTORY**' if t.did_win else '**DEFEAT**'
            players = ''
            for i, p in enumerate(t.players):
                players += '{}. **{}:** {}\n'.format(i + 1, p[0], p[1])
            embed.add_field(name='__TEAM {}:__'.format(t.team_id // 100),
                            value='{}\n{}'.format(result, players),
                            inline=True)
        embeds.append(embed)

        embed = Gv.create_embed(Lv.default_embed_color,
                                'Events of Match __**{}**__ in __**{}**__ .'.format(self.match_id, self.region),
                                ctx.message.author)
        embed.set_author(name='{}'.format(self.match_id), url=self.url)
        for i, e in enumerate(self.events):
            embed.add_field(name='@{}'.format(e.time),
                            value=self.__get_event_string(e),
                            inline=False)
            if i % Lv.match_timeline_split >= Lv.match_timeline_split - 1:
                embeds.append(embed)
                embed = Gv.create_embed(Lv.default_embed_color,
                                        'Events of Match __**{}**__ in __**{}**__ .'.format(self.match_id, self.region),
                                        ctx.message.author)
                embed.set_author(name='{}'.format(self.match_id), url=self.url)
            elif len(self.events) - i == 1:
                embeds.append(embed)
        return embeds

    @staticmethod
    def __get_event_string(event):
        event_description = ''
        if event.category == 'CHAMPION_KILL':
            event_description += 'has slain'
        elif event.category == 'CHAMPION_KILL':
            event_description += 'has destroyed'
        else:
            event_description += 'has slain'
        string = '**TEAM {}** {} **{}**.\n'.format(event.team_killer // 100, event_description, event.victim)
        string += '\t**Killed By** {}\n'.format(event.killer)
        if event.assists:
            string += '\t**Assisted By:**'
            for a in event.assists:
                string += '  {}'.format(a)
        return string


class LoLMatchTimelineTeamPackage:
    def __init__(self, team_id, did_win, players):
        self.team_id = team_id
        self.did_win = did_win
        self.players = players


class LoLMatchTimelineEventPackage:
    def __init__(self, category, time, team_killer, killer, victim, assists):
        self.category = category
        self.time = time
        self.team_killer = team_killer
        self.killer = killer
        self.victim = victim
        self.assists = assists
