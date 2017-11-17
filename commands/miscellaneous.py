import discord
import asyncio
import googletrans
from discord.ext import commands
from utils import config as c

c = c.Config

class Misc(object):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def grade(self, ctx):
        msg = ctx.message.content[8:]

        if not '/' in msg:
            await self.bot.say('You must give a value for your raw score between a "/". E.g. 56/60')
            return
        else:
            percent_calc = msg.split('/')

        scores = [float(i) for i in percent_calc if i.isdigit()]

        if len(scores) != 2:
            await self.bot.say('You inputted an incorrect value; ALL values must be numbers')
            return
        elif scores[0] > scores[1]:
            await self.bot.say('You\'re mark cannot be higher than your total.')
            return
        else:
            final_score = (scores[0]/scores[1]) * 100
            final_score = float(final_score)

        final_grade = ''

        if final_score >= 85:
            final_grade = 'A'
        elif final_score >= 70:
            final_grade = 'B'
        elif final_score >= 50:
            final_grade = 'C'
        elif final_score >= 30:
            final_grade = 'D'
        else:
            final_grade = 'E'

        await self.bot.say("Your percentage is: " + str(final_score) + "\nYour grade is: " + final_grade)

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



def setup(bot):
    bot.add_cog(Misc(bot))
