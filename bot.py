import discord
import os
import sys
import asyncio
from utils import opus_loader
from utils import config as c
from discord.ext import commands

if discord.opus.is_loaded() == False:
    opus_loader.load_opus_lib()

config = c.Config

bot = commands.Bot(command_prefix=config.command_prefix, pass_context=True, description="Sexism", pm_help=None)
bot.remove_command('help')

'''
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.DisabledCommand):
        await ctx.send(Language.get("bot.errors.disabled_command", ctx))
        return

    #In case the bot failed to send a message to the channel, the try except pass statement is to prevent another error
    try:
        await ctx.send(Language.get("bot.errors.command_error", ctx).format(error))
    except:
        pass
'''

@bot.event
async def on_ready():
    print("Logged in as:")
    print(bot.user)
    print(bot.user.id)
    print('----------')
    print('Opus Loaded: ' + str(discord.opus.is_loaded()))

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.command(pass_context=True)
async def test(ctx):
    await bot.say('Sexism.')

bot.run(config.token)
