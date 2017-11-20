import discord
import os
import heroku3
import sys
import subprocess
import aiohttp
import asyncio
from utils import opus_loader
from utils import config as c
from discord.ext import commands

config = c.Config
HEROKU_KEY = config.heroku_api_key
is_prod = os.environ.get('ON_HEROKU', None)
print(is_prod)
opus_load_status = opus_loader.load_opus_lib()
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

    if str(is_prod) == True:
        try:
            heroku_conn = heroku3.from_key(HEROKU_KEY)
            app = heroku_conn.apps()['meloetta-bot']
            dyno = app.dynos()['worker.1']
            dyno.restart()
            return
        except:
            pass
    else:
        subprocess.call(["python3", "bot.py"])

async def _shutdown_bot():
    try:
        aiosession.close()
    except:
        pass
    await bot.logout()

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
    else:
        print("{} is restarting the bot!".format(ctx.message.author))
        await _restart_bot()

@bot.command(pass_context=True)
async def shutdown(ctx):
    if ctx.message.author.id != config.owner_id:
        bot.say(":no_entry_sign: You are not permitted to use that command.")
        return
    else:
        print("{} is restarting the bot!".format(ctx.message.author))
        await _shutdown_bot()


bot.run(config.token)
