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

extensions = ['commands.misc']

bot = commands.Bot(command_prefix=config.command_prefix, description="Meloetta Bot is a bot designed for moderation, music and others.", pm_help=None)
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
    print("Logged in as:")
    print(bot.user)
    print(bot.user.id)
    print('----------')
    print(opus_load_status)

    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print("Failed to load extension {}\n{}: {}".format(extension, type(e).__name__, e))

@bot.event
async def on_message(message):
    if message.content.startswith('m.spam'):
        content = message.content[7:]
        content = content.split(' ')
        times_to_spam = content[-1]
        msg_to_spam = str(' '.join(content[0:-1]))

        if message.channel.server.get_member(config.owner_id) in message.mentions:
            await bot.send_message(message.channel, 'I shall not spam my master!')
            return
        elif not times_to_spam.isdigit():
            await bot.send_message(message.channel, 'I can\'t spam things "{}" times.'.format(times_to_spam))
            return
        else:
            x = int(times_to_spam)
            if x > 100:
                await bot.send_message(message.channel, 'I can\'t spam things more than 100 times.')
                return
            else:
                while x > 0:
                    asyncio.sleep(1)
                    await bot.send_message(message.channel, msg_to_spam)
                    x -= 1

    await bot.process_commands(message)

'''
@bot.command(pass_context=True)
async def test(ctx):
    await bot.say('Sexism.')
'''

@bot.command(pass_context=True)
async def restart(ctx):
    if ctx.message.author.id != config.owner_id:
        bot.say(":no_entry_sign: You are not permitted to use that command.")
        return
    print("{} is restarting the bot!".format(ctx.message.author))
    await _restart_bot()

bot.run(config.token)
