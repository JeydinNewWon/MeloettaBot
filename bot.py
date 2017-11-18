import discord
import os
import sys
import subprocess
import aiohttp
import asyncio
from utils import opus_loader
from utils import config as c
from discord.ext import commands


opus_load_status = opus_loader.load_opus_lib()

config = c.Config

extensions = ['commands.miscellaneous', 'commands.moderation', 'commands.educational']

bot = commands.Bot(command_prefix=config.command_prefix, description="Meloetta Bot is a bot designed for moderation, music and functions.", pm_help=None)
bot.remove_command('help')
aiosession = aiohttp.ClientSession(loop=bot.loop)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

async def _restart_bot():
    try:
        aiosession.close()
    except:
        pass
    await bot.logout()
    subprocess.call(["python3", "bot.py"])

@bot.event
async def on_ready():
    for extension in extensions:
        #bot.load_extension(extension)
        try:
            bot.load_extension(extension)
        except Exception as e:
            print("Failed to load extension {}\n{}: {}".format(extension, type(e).__name__, e))
    print('----------')
    print("Logged in as:")
    print(bot.user)
    print(bot.user.id)
    print('----------')
    print(opus_load_status)
    print('----------')


@bot.event
async def on_message(message):
    if message.content == 'rwby':
        await bot.send_message(message.channel, 'is the best anime!')


    await bot.process_commands(message)

@bot.command(pass_context=True)
async def restart(ctx):
    if ctx.message.author.id != config.owner_id:
        bot.say(":no_entry_sign: You are not permitted to use that command.")
        return
    print("{} is restarting the bot!".format(ctx.message.author))
    await _restart_bot()

bot.run(config.token)
