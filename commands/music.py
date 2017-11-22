import discord
import shutil
import asyncio
import traceback
import youtube_dl

from discord.ext import commands
from utils.config import Config

config = Config
fail = config.fail
success = config.success
owner_id = config.owner_id

ytdl_format_options = {"format": "bestaudio/best", "extractaudio": True, "audioformat": "mp3", "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": False, "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto", "source_address": "0.0.0.0", "preferredcodec": "libmp3lame", "forcefilename": True}


def get_ytdl(id):
    format = ytdl_format_options
    format["outtmpl"] = "data/music/{}/%(id)s.mp3".format(id)
    return youtube_dl.YoutubeDL(format)


class Song:
    def __init__(self, path, message, title, duration, uploader, thumbnail, webpage_url):
        self.path = path
        self.server = message.server
        self.requester = message.author
        self.channel = message.channel
        self.voice_channel = message.author.voice.voice_channel
        self.title = title
        self.duration = duration
        self.uploader = uploader
        self.thumbnail = thumbnail
        self.webpage_url = webpage_url
        self.player = None
        if self.duration:
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            self.duration = "%02d:%02d:%02d" % (h, m, s)

    def embed(self):
        song_info = discord.Embed(
            colour=discord.Colour.green()
        )
        duration = self.duration
        song_info.add_field(name="Uploaded by", value=self.uploader)
        song_info.add_field(name="Requested by", value=self.requester.display_name)
        song_info.add_field(name="Duration", value=str(duration))
        song_info.set_author(name=self.title, url=self.webpage_url)
        song_info.set_thumbnail(url=self.thumbnail)
        return song_info

    def on_song_playing(self):
        return "**Now playing** {} (`{}`)".format(self.title, self.duration)

class Queue():
    def __init__(self, message, bot, voice_client):
        self.message = message
        self.bot = bot
        self.voice_client = voice_client
        self.play_next_song = asyncio.Event()
        self.song_list = []
        self.current = None
        self.songs = asyncio.Queue()
        self.audio_player = self.bot.loop.create_task(self.audio_change_task())
        self.skip_votes = []


    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set())

    async def audio_change_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            self.song_list.remove(str(self.current))
            self.skip_votes.clear()
            await self.bot.send_message(self.message.channel, self.current.on_song_playing())
            player = self.voice_client.create_ffmpeg_player(self.current.path, after=lambda e: self.play_next_song.set())
            self.current.player = player
            self.current.player.start()
            await self.play_next_song.wait()

    @property
    def player(self):
        return self.current.player

class Music:
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    def get_queue(self, ctx):
        queue = self.queues.get(ctx.message.server.id)
        if queue is None:
            queue = Queue(ctx.message, self.bot, ctx.message.server.voice_client)
            self.queues[ctx.message.server.id] = queue
            return queue
        else:
            return queue

    async def disconnect(self):
        queues = self.queues
        for id in queues:
            try:
                await self.queues[id].voice_client.disconnect()
                self.clear_data(id)
                del self.queues[id]
            except:
                pass

    @staticmethod
    def clear_data(id=None):
        if id is None:
            shutil.rmtree('data/music')
        else:
            shutil.rmtree('data/music/{}'.format(id))

    @staticmethod
    def download_video(ctx, url):
        ytdl = get_ytdl(ctx.message.server.id)
        data = ytdl.extract_info(url, download=True)
        if 'entries' in data:
            data = data['entries'][0]
        title = data['title']
        uploader = data['uploader']
        duration = None
        thumbnail = data['thumbnail']
        webpage_url = data['webpage_url']
        id = data['id']
        try:
            duration = data['duration']
        except KeyError:
            pass
        path = "data/music/{}".format(ctx.message.server.id)
        filepath = "{}/{}.mp3".format(path, id)
        song = Song(filepath, ctx.message, title, duration, uploader, thumbnail, webpage_url)

        return song

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, url:str):
        await self.bot.send_typing(ctx.message.channel)
        voice_to_join = ctx.message.author.voice.voice_channel
        if self.bot.voice_client_in(ctx.message.server) is None:
            if voice_to_join:
                try:
                    await self.bot.join_voice_channel(voice_to_join)
                except discord.errors.Forbidden:
                    await self.bot.say("{} I cannot join the voice channel due to insufficient permissions.".format(fail))
                    return
            else:
                await self.bot.say("{} You are not connected to a voice channel.".format(fail))
                return

        queue = self.get_queue(ctx)
        url = url.strip('<>')
        try:
            song = self.download_video(ctx, url)
        except youtube_dl.utils.DownloadError as error:
            await self.bot.say('Error: ```py\n{}: {}\n```'.format(error.__class__.__name__, error))
            return
        except:
            print(traceback.format_exc())
            return
        await queue.songs.put(song)
        queue.song_list.append(str(song))
        await self.bot.say(embed=song.embed())

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        queue = self.get_queue(ctx)
        try:
            queue.player.pause()
        except:
            await self.bot.say('{} Failed to pause song.'.format(fail))

        await self.bot.say('{} Successfully paused **{}**.'.format(success, queue.current.title))

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        queue = self.get_queue(ctx)
        try:
            queue.player.resume()
        except:
            await self.bot.say('{} Failed to resume song.'.format(fail))

        await self.bot.say('{} Successfully resumed **{}**.'.format(success, queue.current.title))

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        queue = self.get_queue(ctx)
        voter = ctx.message.author
        role_names = [i.name.lower() for i in voter.roles]
        if voter == queue.current.requester or voter.id == owner_id or 'dj' in role_names:
            queue.player.stop()
            await self.bot.say('{} Skipping **{}** ...'.format(success, queue.current.title))
        else:
            min_votes = round(len([i.name for i in queue.voice_client.channel.voice_members if i.name != self.bot.user.name]) * 0.6)

            if ctx.message.author.id not in queue.skip_votes:
                queue.skip_votes.append(ctx.message.author.id)
            elif ctx.message.author.id in queue.skip_votes:
                await self.bot.say('{} You have already voted to skip.'.format(fail))
                return

            if len(queue.skip_votes) >= min_votes:
                queue.player.stop()
                await self.bot.say('{} Skipping **{}**...'.format(success, queue.current.title))

    @commands.command(pass_context=True, no_pm=True)
    async def queue(self, ctx):
        queue = self.get_queue(ctx)
        if queue.current:
            if not queue.player.is_playing():
                await self.bot.say('{} Nothing is queued.'.format(fail))
                return
            else:
                song_list = queue.current
        else:
            await self.bot.say('{} Nothing is queued.'.format(fail))
            return

        if len(queue.song_list) != 0:
            embed = discord.Embed(
                colour=discord.Colour.green()
            )
            for i in queue.song_list:
                embed.add_field(
                    name="{}. {}".format(queue.song_list.index(i) + 1, i),
                    value='\u200b'
                )

            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        queue = self.get_queue(ctx)
        server_id = ctx.message.server.id
        voice_channel_id = queue.current.voice_channel.id
        try:
            await queue.voice_client.disconnect()
            self.clear_data(server_id)
            del self.queues[server_id]
            await self.bot.say('{} Successfully disconnected from <#{}>'.format(success, voice_channel_id))
        except:
            pass


def setup(bot):
    bot.add_cog(Music(bot))
