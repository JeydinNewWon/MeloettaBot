import discord
import shutil
import asyncio
import traceback
import youtube_dl

from discord.ext import commands
from utils.config import Config

config = Config()
fail = config.fail
success = config.success
owner_id = config.owner_id

ytdl_format_options = {
    "format": "bestaudio/best",
    "extractaudio": True,
    "audioformat": "mp3",
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    "preferredcodec": "libmp3lame",
    "forcefilename": True
}

def get_ytdl(id):
    format = ytdl_format_options
    format["outtmpl"] = "data/music/{}/%(id)s.mp3".format(id)
    return youtube_dl.YoutubeDL(format)


class Song:
    def __init__(self, path, message, player, video_info):
        self.path = path
        self.requester = message.author
        self.channel = message.channel
        self.voice_channel = message.author.voice.voice_channel
        self.server = message.server
        self.player = player
        self.title = video_info[0]
        self.duration = video_info[1]
        self.thumbnail = video_info[2]
        self.uploader = video_info[3]
        self.web_url = video_info[4]
        if self.duration:
            m, s = divmod(video_info[1], 60)
            h, m = divmod(m, 60)
            self.duration = "%02d:%02d:%02d" % (h, m, s)

    def embed(self):
        song_info = discord.Embed(
            colour=discord.Colour.green()
        )
        duration = self.duration
        song_info.add_field(name='Uploaded by', value=self.uploader)
        song_info.add_field(name='Requested by', value=self.requester.display_name)
        song_info.add_field(name='Duration', value=str(duration))
        song_info.set_author(name=self.title, url=self.web_url)
        song_info.set_thumbnail(url=self.thumbnail)
        return song_info

    def on_song_playing(self):
        return ":notes: **Now playing** {} (`{}`)".format(self.title, self.duration)


class Queue:
    def __init__(self, bot, voice_client):
        self.bot = bot
        self.repeat = False
        self.voice_client = voice_client
        self.play_next_song = asyncio.Event()
        self.current = None
        self.skip_votes = set()
        self.songs = asyncio.Queue()
        self.song_list = []
        self.was_repeating = False
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice_client is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing():
            if self.repeat:
                self._set_repeat()
                self.was_repeating = True
                self.player.stop()
            else:
                self.player.stop()

    def _set_repeat(self):
        if not self.repeat:
            self.repeat = True
            self.was_repeating = False
            return True
        elif self.repeat:
            self.repeat = False
            return False
        else:
            return

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            if self.repeat:
                player = self.voice_client.create_ffmpeg_player(self.current.path, after=self.toggle_next)
                self.current.player = player
                await self.bot.send_message(self.current.channel, self.current.on_song_playing())
                player.start()
                await self.play_next_song.wait()
                continue

            self.current = await self.songs.get()
            self.song_list.remove(self.current)
            await self.bot.send_message(self.current.channel, self.current.on_song_playing())
            self.current.player.start()
            await self.play_next_song.wait()
            if self.was_repeating:
                self._set_repeat()


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    def get_queue(self, server):
        # Gets/Registers a Queue() object.

        queue = self.queues.get(server.id)
        if queue is None:
            queue = Queue(self.bot, server.voice_client)
            self.queues[server.id] = queue

        return queue

    async def disconnect_all_voice_clients(self):
        # Disconnects all voice clients the bot is connected to.

        queues = self.queues
        for queue in queues.values():
            try:
                queue.audio_player.cancel()
                if queue.voice_client:
                    self.bot.loop.create_task(queue.voice_client.disconnect())
                del queue
            except:
                pass

    @staticmethod
    def clear_data(id=None):
        # Clears music data.

        if id is None:
            shutil.rmtree('data/music')
        else:
            shutil.rmtree('data/music/{}'.format(id))

    @staticmethod
    def download_video(ctx, url):
        # Downloads a YouTube video and saves it in data/music/server_id/.

        ytdl = get_ytdl(ctx.message.server.id)
        data = ytdl.extract_info(url, download=True)
        if 'entries' in data:
            data = data['entries'][0]
        title = data['title']
        uploader = data['uploader']
        duration = None
        thumbnail = data['thumbnail']
        web_url = data['webpage_url']
        id = data['id']
        try:
            duration = data['duration']
        except KeyError:
            pass
        path = "data/music/{}".format(ctx.message.server.id)
        filepath = "{}/{}.mp3".format(path, id)

        video_info = {
            "path": filepath,
            "title": title,
            "duration": duration,
            "thumbnail": thumbnail,
            "uploader": uploader,
            "web_url": web_url
        }

        return video_info

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, url: str):
        # Enqueues a song to be played.

        await self.bot.send_typing(ctx.message.channel)
        voice_to_join = ctx.message.author.voice.voice_channel
        if self.bot.voice_client_in(ctx.message.server) is None:
            if voice_to_join:
                try:
                    await self.bot.join_voice_channel(voice_to_join)
                except discord.errors.Forbidden:
                    await self.bot.say(
                        "{} I cannot join the voice channel due to insufficient permissions.".format(fail))
                    return
            else:
                await self.bot.say("{} You are not connected to a voice channel.".format(fail))
                return

        queue = self.get_queue(ctx.message.server)
        url = url.strip('<>')
        try:
            video_info = self.download_video(ctx, url)
        except youtube_dl.utils.DownloadError as error:
            await self.bot.say('Error: ```py\n{}: {}\n```'.format(error.__class__.__name__, error))
            return
        except:
            print(traceback.format_exc())
            return
        else:
            path = video_info['path']
            title = video_info['title']
            duration = video_info['duration']
            thumbnail = video_info['thumbnail']
            uploader = video_info['uploader']
            web_url = video_info['web_url']

            player = queue.voice_client.create_ffmpeg_player(path, after=queue.toggle_next)

            song = Song(path, ctx.message, player, [title, duration, thumbnail, uploader, web_url])
            await queue.songs.put(song)
            queue.song_list.append(song)
            await self.bot.say(embed=song.embed())

    @commands.command(pass_context=True, no_pm=True)
    async def queue(self, ctx):
        # Sends an embed with a list of songs in the queue and their duration.

        queue = self.get_queue(ctx.message.server)
        if queue.current:
            if not queue.is_playing():
                await self.bot.say('{} Nothing is playing...'.format(fail))
                return
            else:
                song_list = queue.song_list
        else:
            await self.bot.say('{} Nothing is queued...'.format(fail))
            return

        if len(song_list) != 0:
            embed = discord.Embed(
                colour=discord.Colour.green()
            )
            for i in song_list:
                embed.add_field(
                    name="{}. {}".format(song_list.index(i) + 1, i.title),
                    value="`{}`".format(str(i.duration)),
                    inline=False
                )

            await self.bot.say(embed=embed)
        else:
            await self.bot.say('{} Nothing is queued...'.format(fail))

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        # Stops a song, disconnects from voice, clears the queue and clears song data.

        server = ctx.message.server
        queue = self.get_queue(server)
        author_voice = ctx.message.author.voice.voice_channel

        if author_voice != queue.voice_client.channel and ctx.message.author.id != owner_id:
            await self.bot.say('{} You\'re not in the correct voice channel.'.format(fail))
            return

        if queue.is_playing():
            player = queue.player
            player.stop()

        queue.audio_player.cancel()
        await queue.voice_client.disconnect()
        del self.queues[server.id]
        self.clear_data(server.id)

        await self.bot.say('{} Disconnected from the voice channel and cleared the queue.'.format(success))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        # Pauses a song that is currently playing.

        server = ctx.message.server
        queue = self.get_queue(server)
        author_voice = ctx.message.author.voice.voice_channel

        if author_voice != queue.voice_client.channel and ctx.message.author.id != owner_id:
            await self.bot.say('{} You\'re not in the correct voice channel.'.format(fail))
            return

        if not queue.is_playing():
            return

        try:
            queue.player.pause()
        except:
            await self.bot.say('{} Failed to pause song.'.format(fail))
            return

        await self.bot.say(':pause_button: Successfully paused **{}**.'.format(queue.current.title))

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        # Resumes a paused song.

        server = ctx.message.server
        queue = self.get_queue(server)
        author_voice = ctx.message.author.voice.voice_channel

        if author_voice != queue.voice_client.channel and ctx.message.author.id != owner_id:
            await self.bot.say('{} You\'re not in the correct voice channel.'.format(fail))
            return

        if not queue.is_playing():
            return

        try:
            queue.player.resume()
        except:
            await self.bot.say('{} Failed to resume song.'.format(fail))
            return

        await self.bot.say(':arrow_forward: Successfully resumed **{}**.'.format(queue.current.title))

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        # Skips a song.

        server = ctx.message.server
        queue = self.get_queue(server)
        votes_needed = round(
            len([i.name for i in queue.voice_client.channel.voice_members if i.name != self.bot.user.name]) * 0.5)
        author_voice = ctx.message.author.voice.voice_channel

        if not queue.is_playing():
            await self.bot.say('{} Nothing is playing...'.format(fail))
            return

        if author_voice != queue.voice_client.channel and ctx.message.author.id != owner_id:
            await self.bot.say('{} You\'re not in the correct voice channel.'.format(fail))
            return

        voter = ctx.message.author
        author_role_names = [role.name.lower() for role in voter.roles]
        if voter == queue.current.requester or voter.id == owner_id or 'dj' in author_role_names:
            queue.skip()
            await self.bot.say(':track_next: Skipping **{}** ...'.format(queue.current.title))
        elif voter.id not in queue.skip_votes:
            queue.skip_votes.add(voter.id)
            total_votes = len(queue.skip_votes)
            if total_votes >= votes_needed:
                await self.bot.say(':track_next: Skipping **{}** ...'.format(queue.current.title))
                queue.skip()
            else:
                await self.bot.say(
                    '{} Skip vote added, currently at `{}/{}`'.format(success, total_votes, votes_needed))
        else:
            await self.bot.say('{} You have already voted to skip.'.format(fail))

    @commands.command(pass_context=True, no_pm=True)
    async def current(self, ctx):
        # Sends an Embed with the current song info.

        queue = self.get_queue(ctx.message.server)
        if queue.current is None:
            await self.bot.say('{} Not playing anything...'.format(fail))
            return
        else:
            embed = queue.current.embed()
            await self.bot.say(embed=embed)


    @commands.command(pass_context=True, no_pm=True)
    async def repeat(self, ctx):
        # Sets the repeat state
        server = ctx.message.server
        queue = self.get_queue(server)
        author_voice = ctx.message.author.voice.voice_channel

        if author_voice != queue.voice_client.channel and ctx.message.author.id != owner_id:
            await self.bot.say('{} You\'re not in the correct voice channel.'.format(fail))
            return

        if not queue.is_playing():
            await self.bot.say('{} Nothing is playing...'.format(fail))
            return

        repeat_state = queue._set_repeat()

        if repeat_state:
            await self.bot.say('{} Repeat state set to True.'.format(':repeat:'))
        else:
            await self.bot.say('{} Repeat state set to False.'.format(':repeat:'))


def setup(bot):
    bot.add_cog(Music(bot))
