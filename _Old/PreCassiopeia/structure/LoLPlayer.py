import discord
from value import GeneralValues as Gv, LeagueValues as Lv


class LoLPlayer:
    def __init__(self, name, region, url, icon_id, icon_url, level, ranks_list, masteries_list, recent_games,
                 recent_wins, recent_losses, kills, deaths, assists, vision, cs):
        self.cs = cs
        self.name = name
        self.region = region
        self.url = url
        self.icon_id = icon_id
        self.icon_url = icon_url
        self.level = level
        self.ranks_list = ranks_list
        self.masteries_list = masteries_list
        self.recent_games = recent_games
        self.recent_wins = recent_wins
        self.recent_losses = recent_losses
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.vision = vision
        self.win_rate = recent_wins / (recent_wins + recent_losses) * 100 if recent_games > 0 else 0
        self.kda = (kills + assists) / (deaths + 1)

    def embed(self, ctx):
        embed = Gv.create_embed(Lv.default_embed_color,
                                'Brief overview of __**{}**__ in __**{}**__.'.format(self.name, self.region),
                                ctx.message.author,
                                self.icon_url)
        # Set Author
        embed.set_author(name='OP.GG: {}'.format(self.name), url=self.url,
                         icon_url=Lv.op_gg_icon_url)
        # Basic Info: Region, Level
        embed.add_field(name='__Basic Info:__',
                        value='**Level:** {}'.format(self.level),
                        inline=False)
        # Recent Games: Games Analyzed, W/L, Win Rate
        embed.add_field(name='__Recent {} Games:__'.format(self.recent_games),
                        value='**W/L:** {}W / {}L\n**Winrate:** {:.02f}%\n'
                              '**KDA:** {:.02f} / {:.02f} / {:.02f} **R:** {:.02f}\n**CS:** {:.02f}\n'
                              '**Vision:** {:.02f}'
                        .format(self.recent_wins, self.recent_losses, self.win_rate, self.kills, self.deaths,
                                self.assists, self.kda, self.cs, self.vision),
                        inline=True)
        # Top Champions: Champion, Level, Points
        masteries = ''
        if len(self.masteries_list) < 1:
            masteries += 'No Champions Mastered.'
        for i, m in enumerate(self.masteries_list):
            masteries += '{}. **{}:** Level {}, {} pts.\n'.format(i + 1, m.name, m.level, m.points)
        embed.add_field(name='__Top 5 Champions:__',
                        value=masteries)
        # Ranked Stats: Division, Rank, W/L, Win Rate
        if self.ranks_list:
            for r in self.ranks_list:
                rank_info = '{}\n**Rank:** {} {}\n**W/L:** {}W {}L, {} LP\n**Winrate:** {:.02f}%\n'\
                    .format(r.name, r.division, r.rank, r.wins, r.losses, r.lp, r.win_rate)
                if r.is_fresh_blood:
                    rank_info += 'Fresh Blood\n'
                if r.is_hot_streak:
                    rank_info += 'Hot Streak\n'
                if r.is_veteran:
                    rank_info += 'Veteran\n'
                embed.add_field(name='__**{}:**__'.format(r.queue_burn),
                                value=rank_info,
                                inline=False)
        return embed


class LoLPlayerRanksPackage:
    def __init__(self, queue_burn, name, division, rank, wins, losses, lp, is_fresh_blood, is_hot_streak, is_veteran):
        self.queue_burn = queue_burn
        self.name = name
        self.division = division
        self.rank = rank
        self.wins = wins
        self.losses = losses
        self.lp = lp
        self.is_fresh_blood = is_fresh_blood
        self.is_hot_streak = is_hot_streak
        self.is_veteran = is_veteran
        self.win_rate = wins / (wins + losses) * 100


class LoLPlayerMasteriesPackage:
    def __init__(self, name, level, points):
        self.name = name
        self.level = level
        self.points = points
