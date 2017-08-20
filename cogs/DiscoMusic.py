import discord
from discord.ext import commands
import asyncio
import DiscoUtils

try:
    import youtube_dl
except ImportError:
    print('In DiscoMusic, youtube_dl module not found.')

try:
    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')
except Exception as e:
    print('Something went wrong when trying to load opus:\n {}: {}\n'
          .format(type(e).__name__, e))

__author__ = 'JosephPKC'
__version__ = '0.1'

YT_OPTS = {
    'quiet': True,
    'default_search': 'auto'
}

# Song data structure
class Song:
    def __init__(self, player, message, **kwargs):
        self.__dict__ = kwargs
        self.title = kwargs.pop('title', None)
        self.by = kwargs.pop('by', None)
        self.requester = message.author
        self.duration = kwargs.pop('duration', 0)
        self.player = player
        self.channel = message.channel
        self.next = None
        self.paused = False

    def __str__(self):
        return '{} uploaded by {} and requested by {} [length: {}m {}s]'\
            .format(self.title, self.by,
                    self.requester.display_name,
                    self.duration[0], self.duration[1])

    def __repr__(self):
        return '{} uploaded by {} and requested by {}'\
            .format(self.title, self.by, self.requester.display_name)

# Playlist (Linked List of Songs) data structure
class Playlist:
    def __init__(self):
        self.current = None
        self.last = None
        self.songs = 0

    def __str__(self):
        li = self.display()
        msg = ''
        for s in li:
            msg += s + '\n'
        return msg

    def enqueue(self, song, request):
        s = Song(song, request, title=song.title,
                 by=song.uploader, duration=divmod(song.duration, 60))
        self.songs += 1
        if self.current is None:
            self.current = s
            self.last = self.current
        else:
            self.last.next = s
            self.last = s

    def dequeue(self):
        if self.current is None:
            return None

        self.songs -= 1
        s = self.current
        if self.current.next is not None:
            self.current = self.current.next
        else:
            self.current = None
            self.last = None
        return s

    def display(self, number = 5):
        playlist = list()
        walk = self.current
        index = 0
        while walk is not None:
            if index >= 0 and index == number:
                break
            playlist.append('{}: {}'.format(index, str(walk)))
            index += 1
            walk = walk.next
        return playlist

    def clean(self):
        while self.current is not None:
            hold = self.current.next
            del self.current
            self.current = hold
        self.last = None

# Music cog
class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice = None
        self.player = None
        self.volume = 30
        self.playlist = Playlist()
        self.skips = set()
        self.seconds = 0
        self.ready = False

    def is_ready(self):
        return not self.player.is_done()

    # Commands
    @commands.command(name='play', aliases=['queue'], pass_context=True,
                      no_pm=True, help='Play or Queue up a song')
    async def play(self, ctx, *, song: str):
        """ Queues up the given song or link
        -If there are no other songs in the queue (the given song is the first), then it automatically plays it.
        -If the bot is not already in a voice channel, it will join the voice channel of the requester.
        """

        # Thoughts: Should I move the download to when the song needs to start playing? If so, then the voice channel check and the download is moved to play music. But enqueueing a song requires simply queueing the string, and the playlist will simply be a linked list of strings
        if self.voice is None:
            if not await self._join(ctx.message.author.voice_channel):
                return
        try:
            player = await self.voice.create_ytdl_player(song, ytdl_options=YT_OPTS)

        except Exception as e:
            await self.bot.send_message(ctx.message.channel, 'An error occurred:```py\n{}: {}\n```'.format(type(e).__name__, e))
        else:
            check = self.playlist.current is None
            self.playlist.enqueue(player, ctx.message)
            await self.bot.say('Enqueued ' + str(self.playlist.last))
            if check:
                await self._play_next_song()

    @commands.command(name='volume', aliases=['vol'],
                      no_pm=True, help='Change the volume')
    async def vol(self, val: int):
        """ Changes the volume
        -The volume must be an integer between 0 and 100 (inclusive)
        -The volume cannot be changed if there is no player running (i.e. no music playing)
        """
        if val < 0 or val > 100:
            await self.bot.say('{} is an invalid volume level. Choose 0 - 100.'.format(val))
            return

        check = await self._base_check()
        if not check:
            return

        self.volume = val
        self.player.volume = self.volume / 100
        await self.bot.say('Setting volume to {}%.'.format(self.volume))

    @commands.command(name='skip', aliases=['next'], pass_context=True,
                      no_pm=True, help='Vote to skip the current song')
    async def skip(self, ctx):
        """ Skips the current song by vote
        -Skips cannot occur if there is no voice channel, or if there is no player.
        -If the requester of the current song calls this, it automatically skips.
        -Otherwise, the author's id is added to the skip set.
        -If the number of skip votes is at anytime equal to or greater than the minimal majority, the current song is skipped
        """
        check = await self._base_check()
        if not check:
            return

        author = ctx.message.author
        majority = (len(self.voice.channel.voice_members) // 2) + 1
        if author == self.playlist.current.requester:
            await self._skip_song()
            await self.bot.say('The requester of this song, **{}**, requested skipping this song. Skipping song...'.format(author.display_name))
        elif author.id not in self.skips:
            self.skips.add(author.id)
            await self.bot.say('**{}**\' skip vote added. Now at {}/{} votes.'.format(author.display_name, len(self.skips), majority))
            await self._check_skips(majority)
        else:
            await self.bot.say('**{}** has already voted. At {}/{} votes.'.format(author.display_name, len(self.skips), majority))
            await self._check_skips(majority)

    @commands.command(name='pause', aliases=[], pass_context=True,
                      no_pm=True, help='Pause or resume the song')
    async def pause(self, ctx):
        """ Pauses or resumes the song
        -Cannot pause/resume if there is no voice channel or player
        -Pause is a toggle that is applied to the current song only
        """
        check = await self._base_check()
        if not check:
            return

        if not self.playlist.current.paused:
            self.player.pause()
            self.playlist.current.paused = True
            await self.bot.say('**{}** paused the song.'.format(ctx.message.author.display_name))
        else:
            self.player.resume()
            self.playlist.current.paused = False
            await self.bot.say('**{}** resumed the song.'.format(ctx.message.author.display_name))

    @commands.command(name='stop', aliases=['leave'], pass_context=True,
                      no_pm=True, help='Stop the bot from playing music')
    async def stop(self, ctx):
        """ Stops the music stream
        -Cannot stop if there is no voice channel or player
        -Stops the current player
        -Leaves the voice channel
        -Removes all songs from the playlist
        -Clears the votes and duration
        -Essentially, a reset on the music
        """
        check = await self._base_check()
        if not check:
            return

        await self.bot.say('**{}** stopped the music.'.format(ctx.message.author.display_name))

        await self._leave()
        self.skips.clear()
        self.seconds = 0
        self.playlist.clean()

    @commands.command(name='list', aliases=['songs'], pass_context=True,
                      no_pm=True, help='List songs in queue')
    async def list(self, ctx, amount: int = -1):
        """ Lists the songs in queue
        -Cannot queue if there is no voice channel or player
        -Simply lists the songs in order up to amount
        -Mentions the calling author
        """
        check = await self._base_check()
        if not check:
            return

        if amount == 0:
            await self.bot.say('@{} ```Listed no songs.``` ```There are {} song(s) in queue.```'.format(ctx.message.author.mention, self.playlist.songs))
        else:
            msg = '@{} ```'.format(ctx.message.author.mention)
            prep = self.playlist.display(amount)
            if len(prep) == 0:
                msg += 'No songs queued.'

            for p in prep:
                msg += p + '\n'
            msg += '```'
            await self.bot.say(msg + '```There are {} song(s) in queue.```'.format(self.playlist.songs))

    @commands.command(name='current', aliases=['song'], pass_context=True,
                      no_pm=True, help='List current song info')
    async def get_current(self, ctx):
        """ Gets info on the current song (Similar to the Now Playing say)
        -Cannot check current if there is no voice channel or player
        -Mentions the calling author
        -Displays the current info (including time so far)
        """
        check = await self._base_check()
        if not check:
            return

        if self.playlist.current is None:
            await self.bot.say('@{} No song currently playing.'.format(ctx.message.author.mention))
        else:
            msg = '@{} ```'.format(ctx.message.author.mention)
            msg += repr(self.playlist.current)
            current_song = self.playlist.current
            msg += '[duration: {0[0]}m {0[1]}s / {1[0]}m {1[1]}s]'.format(divmod((current_song.duration[0] * 60 + current_song.duration[1]) - self.seconds, 60), current_song.duration)
            msg += '```'
            await self.bot.say(msg)

    # DEBUG commands

    @commands.group(name='debug')
    async def debug(self):
        return

    @debug.command()
    async def fskip(self):
        self.player.stop()
        self.seconds = 0
        # self.playlist.dequeue()
        # self.lock = False

    @debug.command()
    async def state(self):
        msg = '```'
        msg += 'Bot: {}\n'.format(self.bot)
        msg += 'Voice: {}\n'.format(self.voice)
        msg += 'Player: {}\n'.format(self.player)
        msg += 'Volume: {}\n'.format(self.volume)
        msg += 'Playlist: {}\n'.format(str(self.playlist))
        msg += 'Skips: {}\n'.format(self.skips)
        msg += 'Seconds: {}\n'.format(self.seconds)
        msg += 'Ready: {}\n'.format(self.ready)
        msg += '```'
        await self.bot.say(msg)

    # Helper methods
    async def _join(self, channel):
        try:
            self.voice = await self.bot.join_voice_channel(channel)
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel...')
            return False
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
            return False
        else:
            self.ready = True
            return True

    async def _leave(self):
        self.ready = False
        if self.player is not None:
            self.player.stop()
            self.player = None
        if self.voice is not None:
            await self.voice.disconnect()
            self.voice = None

    async def _play_next_song(self):
        # By calling this method,
        # you are saying that it is OK to force stop
        # whatever song is currently playing (if there is any)
        # and play the next song
        # self.lock = True
        if not self.ready:
            return

        if self.player:
            self.player.stop()

        self.skips.clear()
        self.player = self.playlist.current.player
        await self.bot.say('Now playing ' + str(self.playlist.current))
        self.player.volume = self.volume / 100
        self.player.start()
        self.seconds = self.player.duration
        await self.bot.change_presence(game=discord.Game(name=self.player.title))
        await self._loop_play_song()

    async def _loop_play_song(self):
        while self.seconds > 0:
            self.seconds -= 1
            await asyncio.sleep(1)

        # If there are more songs to be played
        self.playlist.dequeue()
        if self.playlist.songs > 0:
            await self._play_next_song()
        else:
            await self.bot.change_presence(game=discord.Game(name='Ascension'))

    async def _check_skips(self, majority):
        if len(self.skips) >= majority:
            self.skips.clear()
            await self.bot.say('Majority vote passed. Skipping song...')
            self._skip_song()

    async def _skip_song(self):
        if self.player is None:
            return
        self.player.stop()
        self.seconds = 0

    async def _base_check(self):
        if self.voice is None:
            await self.bot.say('Bot is not in a voice channel. No music is currently playing.')
            return False

        if self.player is None:
            await self.bot.say('No music is currently playing.')
            return False

        return True
