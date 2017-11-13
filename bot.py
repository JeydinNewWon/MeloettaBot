import discord
import os
import sys
import asyncio
from utils import opus_loader
from utils import config as c
from discord.ext import commands

opus_loader.load_opus_lib()

config = c.Config

bot = commands.Bot(command_prefix=config.command_prefix, pass_context=True, pm_help=None)
bot.remove_command('help')

@bot.event
async def on_ready():
    print("Logged in as:")
    print(bot.user)
    print(bot.user.id)
    print('----------')
    print('CHECKS:')
    print('Opus Loaded: ' + str(discord.opus.is_loaded()))

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.command()
async def test(ctx):
    await bot.say(ctx.message.channel, 'Sexism.')

bot.run(config.token)
