import discord
from value import GeneralValues as Gv, LeagueValues as Lv


class DiscoHelp:
    def __init__(self, group, commands_list):
        self.group = group
        self.commands_list = commands_list

    def embed(self, ctx):
        embed = Gv.create_embed(Lv.default_embed_color,
                                'Commands for **{}**'.format(self.group),
                                ctx.message.author)
        for c in self.commands_list:
            tips = ''
            for i, t in enumerate(c.tips_list):
                tips += '{}. {}\n'.format(i + 1, t)
            embed.add_field(name='__**{}:**__'.format(c.name),
                            value='**Usage:** {}\n**Brief:** {}\n{}'.format(c.usage, c.brief, tips),
                            inline=False)
        return embed


class DiscoHelpCommandPackage:
    def __init__(self, name, usage, brief, tips_list):
        self.name = name
        self.usage = usage
        self.brief = brief
        self.tips_list = tips_list