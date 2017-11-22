import asyncio
import discord
import copy
import glob
import shutil
import youtube_dl

from discord.ext import commands
from utils.youtubedl_downloader import Extract
from utils import config as c

config = c.Config
fail = config.fail

ytdl_options = {
    'default_search': 'auto',
    'format': 'bestaudio/best',
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'audioformat': 'mp3',
    'extractaudio': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }],
    'force_ipv4': True,
    'source_address': '0.0.0.0',
    "playlist_items": "0",
    "playlist_end": "0",
    "noplaylist": True
}

def get_ytdl(id):
    format = ytdl_options
    format["outtmpl"] = "data/music/{}/%(id)s.mp3".format(id)
    return youtube_dl.YoutubeDL(format)


class Song():
    def __init__(self, path, title, duration, requester):
        self.path = path
        self.title = title
        self.duration = duration
        self.requester = requester
        if self.duration:
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            self.duration = "%02d:%02d:%02d" % (h, m, s)

    def __str__(self):
        return "**{}** `[{}]`".format(self.title, self.duration)

    def title_with_requester(self):
        return "{} ({})".format(self.__str__(), self.requester)

class Queue():
    def __init__(self, bot, voice_client, text_channel):
        self.bot = bot
        self.voice_client = voice_client
        self.text_channel = text_channel
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
            await self.say(("music.now_playing", self.text_channel).format(self.current.title_with_requester()))
            self.voice_client.create_ffmpeg_player(self.current.entry, after=lambda e: self.play_next_song.set())
            await self.play_next_song.wait()

class Music:
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}


    def get_queue(self, ctx):
        queue = self.queues.get(ctx.message.guild.id)
        if queue is None:
            queue = Queue(self.bot, ctx.voice_client, ctx.channel)
            self.queues[ctx.guild.id] = queue
        return queue


    async def disconnect_all_voice_clients(self):
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
            shutil.rmtree("data/music")
        else:
            shutil.rmtree("data/music/{}".format(id))

    @staticmethod
    def download_video(ctx, url):
        ytdl = get_ytdl(ctx.message.guild.id)
        data = ytdl.extract_info(url, download=True)
        if "entries" in data:
            data = data["entries"][0]
        title = data["title"]
        id = data["id"]
        duration = None
        try:
            duration = data["duration"]
        except KeyError:
            pass
        path = "data/music/{}".format(ctx.message.guild.id)
        filepath = "{}/{}.mp3".format(path, id)
        song = Song(filepath, title, duration, ctx.message.author)
        return song


def setup(bot):
    bot.add_cog(Music(bot))

