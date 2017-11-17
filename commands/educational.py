import discord
import asyncio
from fractions import Fraction
from utils import config as c
from discord.ext import commands

config = c.Config
fail = config.fail
success = config.success

class Educational(object):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def eqn(self, ctx, x_1, x_2, y_1, y_2):
        '''
        coordinate_li = content.split(' ')[1:]
        try:
            coordinate_li = [int(coord) for coord in coordinate_li]
            try:
                x_1, y_1 = coordinate_li[0], coordinate_li[1]
                x_2, y_2 = coordinate_li[2], coordinate_li[3]

        except ValueError:
            await self.bot.say('{} Could not calculate equation of straight line due to incorrect coordinate inputs.'.format(fail))
        '''
        try:
            m = (y_2 - y_1)/(x_2 - x_1)
            b = str(int(y_2 - m * x_2))
            m = str(Fraction(m).limit_denominator())
        except ValueError:
            await self.bot.say('{} Could not calculate equation of straight line due to incorrect coordinate inputs.'.format(fail))

        if '-' not in b:
            b = '+ ' + b
        else:
            b = b.replace('-', '- ')

        await self.bot.say('equation: y = {}x '.format(m) + b)


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
            final_score = (scores[0] / scores[1]) * 100
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

def setup(bot):
    bot.add_cog(Educational(bot))