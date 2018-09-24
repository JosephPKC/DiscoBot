from value import GeneralValues as Gv, LeagueValues as Lv


class LoLMatchList:
    def __init__(self, region, name, url, matches):
        self.region = region
        self.name = name
        self.url = url
        self.matches = matches

    def embed(self, ctx, amount):
        embed = Gv.create_embed(Lv.default_embed_color,
                                '{} most recent games for __**{}**__ in __**{}**__.'
                                .format(amount, self.name, self.region),
                                ctx.message.author)
        # Set Author
        embed.set_author(name='OP.GG: {}'.format(self.name), url=self.url,
                         icon_url=Lv.op_gg_icon_url)
        # Matches
        amount = min(amount, len(self.matches) - 1)
        for i, m in enumerate(self.matches[:amount]):
            result = 'VICTORY' if m.is_win else 'DEFEAT'
            mins, secs = Gv.get_minutes_seconds(m.duration)
            lane = ' {} {}'.format(m.lane, m.role) if m.has_lanes else ''
            embed.add_field(name='{}. __{}:__'.format(i + 1, m.match_id),
                            value='**{}**\n\t{}\n\t{}\n\t**Duration:** {:02d}:{:02d}\n\t**Champion:** {}{}\n'
                                  '\t**KDA:** {} / {} / {}\n\t**CS:** {} **CC:** {} **Vision:** {}'
                            .format(result, m.season, m.queue, mins, secs, m.champion, lane, m.kills, m.deaths,
                                    m.assists, m.cs, m.cc, m.vision),
                            inline=False)
        return embed


class LoLMatchListMatchPackage:
    def __init__(self, match_id, season, queue, role, lane, duration, champion, kills, deaths, assists, cs,
                 cc, vision, is_win, has_lanes=True):
        self.match_id = match_id
        self.season = season
        self.queue = queue
        self.role = role
        self.lane = lane
        self.duration = duration
        self.champion = champion
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.cs = cs
        self.cc = cc
        self.vision = vision
        self.is_win = is_win
        self.has_lanes = has_lanes
