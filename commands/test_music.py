import discord
import asyncio
from discord.ext import commands


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.default_vol = 100

    @commands.command(pass_context=True)
    async def join(self, ctx):
        channel = ctx.message.author.voice.voice_channel

        voice_client = await self.bot.join_voice_channel(channel)


        player = voice_client.create_ffmpeg_player('commands/music_test.mp3', after=None)
        player.start()

        while True:
            self.get_players()

    def get_players(self):
        print(self.players)


def setup(bot):
    bot.add_cog(Music(bot))