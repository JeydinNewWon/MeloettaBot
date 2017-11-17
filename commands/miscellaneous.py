import discord
import asyncio
import googletrans
from discord.ext import commands
from utils import config as c

config = c.Config

class Misc(object):
    def __init__(self, bot):
        self.bot = bot

    async def _spam(self, message):
        content = message.content[7:]
        content = content.split(' ')
        times_to_spam = content[-1]
        msg_to_spam = str(' '.join(content[0:-1]))

        if message.channel.server.get_member(config.owner_id) in message.mentions:
            await self.bot.say('I shall not spam my master!')
            return
        elif not times_to_spam.isdigit():
            await self.bot.say('I can\'t spam things "{}" times.'.format(times_to_spam))
            return
        else:
            x = int(times_to_spam)
            if x > 100:
                await self.bot.say('I can\'t spam things more than 100 times.')
                return
            else:
                while x > 0:
                    asyncio.sleep(1)
                    await self.bot.say(msg_to_spam)
                    x -= 1

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
        await self._spam(message)



def setup(bot):
    bot.add_cog(Misc(bot))
