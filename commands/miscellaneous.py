import discord
import asyncio
import googletrans
from discord.ext import commands
from utils import config as c

config = c.Config

class Misc(object):
    def __init__(self, bot):
        self.bot = bot

    async def _spam(self, message, secret_spam=False):

        if message.channel.server.get_member(config.owner_id) in message.mentions:
            await self.bot.say('I shall not spam my master!')
            return
        elif secret_spam:
            content = message.content[12:]
            content = content.split(' ')
            can_use_command = ['254014339567058955', '253803512369119233', '347989318012502017']
            times_to_spam = content[-1]
            msg_to_spam = str(' '.join(content[0:-1]))

            await self.bot.delete_message(message)
            if not times_to_spam.isdigit():
                return
            elif str(message.author.id) not in can_use_command:
                return

            x = int(times_to_spam)

            if x > 5:
                print(x)
                return
            else:
                while x > 0:
                    var = await self.bot.send_message(message.channel, msg_to_spam)
                    await self.bot.delete_message(var)
                    x -= 1
        elif not secret_spam:
            content = message.content[7:]
            content = content.split(' ')
            times_to_spam = content[-1]
            msg_to_spam = str(' '.join(content[0:-1]))

            if not times_to_spam.isdigit():
                await self.bot.say('I can\'t spam things "{}" times.'.format(times_to_spam))
                return

            x = int(times_to_spam)
            if x > 100:
                await self.bot.say('I can\'t spam things more than 100 times.')
                return
            else:
                while x > 0:
                    asyncio.sleep(1)
                    await self.bot.say(msg_to_spam)
                    x -= 1
        else:
            return

    @commands.command(pass_context=True)
    async def translate(self, ctx):
        message = ctx.message
        content = message.content.split(' ')
        ln = content[-1].lower()
        src = ' '.join(content[1:-1])
        translator = googletrans.Translator()
        try:
            if ln == 'chinese':
                cn = translator.detect(src)
                translated_msg = translator.translate(src, dest='chinese (simplified)')
                await self.bot.say('**Translated message:** ' + translated_msg.text + '\n**Accuracy:** ' + str(cn.confidence * 100) + '%')
            else:
                cn = translator.detect(src)
                translated_msg = translator.translate(src, dest=ln)
                await self.bot.say('**Translated message:** ' + translated_msg.text + '\n**Accuracy:** ' + str(cn.confidence * 100) + '%')
        except ValueError:
            await self.bot.say('Please enter a valid language request.')

    @commands.command(pass_context=True)
    async def spam(self, ctx):
        message = ctx.message
        await self._spam(message, secret_spam=False)

    @commands.command(pass_context=True)
    async def secretspam(self, ctx):
        message = ctx.message
        await self._spam(message, secret_spam=True)

    @commands.command(pass_context=True)
    async def g(self, ctx):
        await self.bot.reply("Can you actually contribute to discussion instead of sending mindless messages?")


def setup(bot):
    bot.add_cog(Misc(bot))
