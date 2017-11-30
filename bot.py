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

config = c.Config()
s_id = str(config.mute_role_id)
d_id = config.default_server_role_id
mod_ids = config.mod_role_ids
HEROKU_KEY = config.heroku_api_key
is_prod = os.environ.get('ON_HEROKU', None)
opus_load_status = opus_loader.load_opus_lib()
extensions = ['commands.miscellaneous', 'commands.moderation', 'commands.educational', 'commands.music', 'commands.pokedex']

bot = commands.Bot(command_prefix=config.command_prefix, description="Meloetta Bot is a bot designed for moderation, music and functions.", pm_help=None)
bot.remove_command('help')
aiosession = aiohttp.ClientSession(loop=bot.loop)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return


async def _restart_bot(is_prod=is_prod):
    if str(is_prod) == "True":
        heroku_conn = heroku3.from_key(HEROKU_KEY)
        app = heroku_conn.apps()[config.heroku_app_name]
        try:
            app.restart()
            aiosession.close()
            await bot.get_cog("Music").disconnect()
            await bot.logout()
        except:
            pass

        return
    else:

        try:
            aiosession.close()
            await bot.get_cog("Music").disconnect()
            await bot.logout()
        except:
            pass

        subprocess.call(["python3", "bot.py"])


async def _shutdown_bot():
    try:
        aiosession.close()
        await bot.cogs["Music"].disconnect_all_voice_clients()
        await bot.logout()
    except:
        pass

@bot.event
async def on_ready():
    for extension in extensions:
        #bot.load_extension(extension)
        try:
            bot.load_extension(extension)
        except Exception as e:
            print("Failed to load extension {}\n{}: {}".format(extension, type(e).__name__, e))

    print('Discord version:', str(discord.__version__))
    print('----------')
    print('Logged in as:')
    print(bot.user)
    print(bot.user.id)
    print('----------')
    print(opus_load_status)
    if not discord.opus.is_loaded():
        bot.remove_cog('Music')
        print('Removed the Music module because the opus library is not loaded.')
    print('\n')
    if not s_id or not d_id or not mod_ids:
        bot.remove_cog('Moderation')
        print('Removed the Moderation module because the mute role, the default server role or the moderator roles have not been specified.')
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
        print("{} is shutting down the bot!".format(ctx.message.author))
        await _shutdown_bot()

@bot.command(pass_context=True)
async def invite(ctx):
    if not config.invite:
        await bot.say(':no_entry_sign: There seems to be no existing public invite available for this bot as of now.')
        print('The bot has not been given an invite.')
        return
    else:
        await bot.say('**Invite link:** {}'.format(config.invite))

print(type(config.token))

bot.run(config.token)


