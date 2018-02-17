import re
import requests
import sys
from discord.ext import commands
try:
    import riotwatcher
except ImportError:
    riotwatcher = None
    print('Riotwatcher not found.')
    print('pip install riotwatcher.')
    sys.exit(2)
try:
    import py_gg
except ImportError:
    py_gg = None
    print('Py_gg not found.')
    print('pip install py_gg.')
    sys.exit(2)
from value import GeneralValues as Gv, LeagueValues as Lv
from manager import CacheManager as Cache, LoLDatabase as Database, LoLDataDragon as Datadragon, \
     LoLFactory as Factory, FileManager as File
from structure import DiscoHelp


class DiscoLoLCog:
    __command_info_list_map = {
        'player': ['{}player <player> [{}r{}<region>]'
                       .format(Gv.bot_prefix, Gv.bot_arg_prefix, Gv.bot_arg_value_prefix),
                   'Get information on given player.',
                   ['r - Set the region. Default: {}.'.format(Lv.default_region)]
                   ]
    }

    def __init__(self, bot, riot_key, ch_gg_key):
        self.__bot = bot
        self.__watcher = riotwatcher.RiotWatcher(riot_key)
        self.__help = self.__create_help()
        py_gg.init(ch_gg_key)


    # region Commands
    @commands.group(name='lol', pass_context=True)
    async def __group_lol(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.__bot.say('Invalid Command: {}. <:dab:390040479951093771>'.format(ctx.subcommand_passed))


    # Riot API Commands
    @__group_lol.command(name='help', pass_context=True)
    async def __cmd_help(self, ctx, cmd_input: str=None):
        Gv.print_command(ctx.command, cmd_input)
        msg = await self.__display_embed('{}'.format(ctx.message.author.mention), self.__help.embed(ctx))
        await self.__react_to(msg, ['hellyeah', 'dorawinifred', 'cutegroot', 'dab'])
    # endregion


    # region API Retrieval

    # endregion


    # region Parse, Get

    # endregion


    # region Display, Print
    async def __display_embed(self, content, embed):
        return await self.__bot.say(content=content, embed=embed)
    # endregion


    # region Misc.
    async def __react_to(self, msg, emojis):
        for e in self.__bot.get_all_emojis():
            if e.name in emojis:
                await self.__bot.add_reaction(msg, e)

    # endregion


    # region Factories
    def __create_help(self):
        commands = []
        for c, i in self.__command_info_list_map.items():
            commands.append(DiscoHelp.DiscoHelpCommandPackage(
                c, i[0], i[1], i[2]
            ))

        return DiscoHelp.DiscoHelp(
            'LoL', commands
        )
    # endregion