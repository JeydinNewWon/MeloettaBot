import discord
import asyncio
import copy
import glob

from discord.ext import commands
from utils import config as c
from utils.youtubedl_downloader import Extract

config = c.Config
fail = config.fail
success = config.success



class Song:
    def __init__(self, message, player):
        self.server = message.server.name
        self.requester = message.author
        self.channel = message.channel
        self.voice_channel = message.author.voice_channel
        self.player = player
        self.duration = None
        if self.player.duration:
            m, s = divmod(self.player.duration, 60)
            h, m = divmod(m, 60)
            self.duration = "%02d:%02d:%02d" % (h, m, s)

    def embed(self):
        song_info = discord.Embed(
            colour=discord.Colour.green()
        )
        duration = self.duration
        song_info.add_field(name="Uploaded by", value=self.player.uploader)
        song_info.add_field(name="Requested by", value=self.requester.display_name)
        song_info.add_field(name="Duration", value=str(duration))
        song_info.set_author(name=self.player.title, url=self.player.webpage_url)
        song_info.set_thumbnail(url=self.player.thumbnail)
        return song_info

    def on_song_playing(self):
        return "**Now playing** {} (`{}`)".format(self.player.title, str(self.duration))

'''
class VoiceEntry:

    def __init__(self, message, player):
        self.server = message.server.name
        self.requester = message.author
        self.channel = message.channel
        self.voice_channel = message.author.voice_channel
        self.player = player

    def __str__(self):
        fmt = '**{0.title}** uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt += ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

    def embed(self):
        data = discord.Embed(
            color=discord.Color.green()
        )
        duration = self.player.duration
        data.add_field(name="Uploaded by", value=self.player.uploader)
        data.add_field(name="Requested by", value=self.requester.display_name)
        if duration:
            data.add_field(name="Duration", value='{0[0]}m {0[1]}s'.format(
                divmod(duration, 60)))
        data.set_author(name=self.player.title, url=self.player.webpage_url)
        data.set_thumbnail(url=self.player.thumbnail)
        return data
'''

class Queue:
    # represents a Discord Music Queue
    def __init__(self, bot, cog):
        self.volume = 0.6
        self.stop = False
        self.current = None
        self.bot = bot
        self.cog = cog
        self.voice = self.cog.get_voice_state()
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.songlist = []
        self.skip_votes = set()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())
        self.Extract = Extract()

    def votes_needed(self):
        return round(len([i.name for i in self.voice.channel.voice_members if i.name != self.bot.user.name]) * 0.6)

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def disconnect(self, message=False):
        try:
            self.player.stop()
        except:
            pass
        try:
            await self.voice.disconnect()
        except:
            pass
        try:
            self.audio_player.cancel()
        except:
            pass
        try:
            for k, v in copy.copy(self.cog.voice_states).items():
                if v == self:
                    del self.cog.voice_states[k]

        except:
            pass

    async def audio_player_task(self):
        while True:
            self.current = await self.songs.get()
            self.play_next_song.clear()
            try:
                if not self.stop:
                    await self.bot.send_message(self.current.channel, self.current.on_song_playing())
                self.songlist.remove(str(self.current))
            except:
                pass
            self.current.player.volume = self.volume
            self.current.player.start()
            self.skip_votes.clear()
            await self.play_next_song.wait()

    @asyncio.coroutine
    def create_player(self, entry):
        args = glob.glob('data/music/{}.*'.format(entry.display_id))
        print(args)
        player = self.voice.create_ffmpeg_player(args, after=self.toggle_next)

        player.url = entry.url
        player.yt = entry.yt
        player.title = entry.title
        player.display_id = entry.display_id
        player.thumbnail = entry.thumbnail
        player.webpage_url = entry.webpage_url
        player.download_url = entry.download_url
        player.views = entry.views
        player.is_live = entry.is_live
        player.likes = entry.likes
        player.dislikes = entry.dislikes
        player.duration = entry.duration
        player.uploader = entry.uploader

        return player



class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = Queue(self.bot, self)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        state = self.get_voice_state(channel.server)
        voice = await self.bot.join_voice_channel(channel)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice.voice_channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song: str):
        state = self.get_voice_state(ctx.message.server)
        player = None

        summoned_channel = ctx.message.author.voice.voice_channel
        if summoned_channel is None:
            try:
                await self.summon(ctx)
            except asyncio.futures.TimeoutError:
                await self.create_voice_client(summoned_channel)
            '''
            except Exception as e:
                await self.bot.say('Error: {}'.format(e))
                raise Exception
            '''

        try:
            entry = await state.Extract.extract(song)
            if entry:
                player = await state.create_player(entry)

            if int(player.duration) > 3600:
                await self.bot.say("{} Your video could not be loaded because it is too long.").format(fail)
                return

        except Exception as e:
            '''
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(e.__class__.__name__, e))
            if state.voice is None or not state.is_playing():
                await state.disconnect()
            '''
            raise Exception

        else:
            entry = Song(ctx.message, player)
            state.songlist.append(entry)
            await state.songs.put(entry)
            await self.bot.say('Enqueued ' + str(entry))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()
        else:
            await self.bot.say('Not playing anything...')
            return
        await self.bot.say('{} Paused current song.'.format(success))

    @commands.command(pass_context=True)
    async def resume(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()
        else:
            await self.bot.say("Not playing anything...")
            return
        await self.bot.say("Resumed current song.")

    @commands.command(pass_context=True)
    async def stop(self, ctx):
        server = ctx.message.server
        state = self.get_voice_state(server)

        state.stop = True
        await state.disconnect()
        await self.bot.say("{} Successfully disconnected the voice channel and cleared the queue.".format(success))

    @commands.command(pass_context=True)
    async def skip(self, ctx):
        state = self.get_voice_state(ctx.message.server)

        if not state.is_playing():
            await self.bot.say("Not playing anything...")
            return

        voter = ctx.message.author
        if voter not in state.voice.channel.voice_members and voter.id != config.owner_id:
            await self.bot.say('you are not in the current playing voice channel')
            return

        role_names = [i.name.lower() for i in voter.roles]
        if voter == state.current.requester or voter.id == config.owner_id or 'dj' in role_names:
            await self.bot.say("{} Skipping song...".format(success))
            state.skip()
            return

        if voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= state.votes_need():
                await self.bot.say("{} Skipping song...".format(success))
                state.skip()
            else:
                await self.bot.say("Skip vote added, vote is at: {}/{}".format(total_votes, state.votes_needed()))
        else:
            await self.bot.say("{} You have already voted to skip this song.".format(fail))

    @commands.command(pass_context=True, no_pm=True)
    async def current(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('Not playing anything...')
        else:
            skip_count = len(state.skip_votes)
            embed = state.current.embed().add_field(
                name="Skip count", value="{}/{}".format(skip_count, state.votes_needed()))
            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def queue(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        skip_count = len(state.skip_votes)
        data = discord.Embed(
            color=discord.Color.green(),
            description="Queued songs"
        )
        if len(state.songlist) < 1:
            await self.bot.say("nothing is in the queue currently")
            return
        for i in state.songlist:
            data.add_field(name="{}. {}".format(state.songlist.index(
                i) + 1, i.player.title), value="Skip count: {}/{}".format(skip_count, state.votes_needed()))
        await self.bot.say(embed=data)


def setup(bot):
    bot.add_cog(Music(bot))








