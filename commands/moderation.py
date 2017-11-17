import discord
import asyncio
from discord.ext import commands
from utils import config as c

config = c.Config
success = config.success
fail = config.fail

class Moderation(object):
    def __init__(self, bot):
        self.bot = bot

    def get_role(_id, message):
        if message is None:
            return
        else:
            for i in message.channel.server.roles:
                if i.id == _id:
                    return i

    async def _mute_members(self, message, member_li, mute_from_server=False):
        if mute_from_server:
            _muted = []
            _could_not_mute = []
            snake_role = [self.get_role('353500331361042453', message)]

            for member in member_li:
                try:
                    member_roles = member.roles
                    del member_roles[0]
                    await self.bot.remove_roles(member, *member_roles)
                    await self.bot.add_roles(member, *snake_role)
                    _muted.append(member.name)
                except discord.Forbidden:
                    _could_not_mute.append(member.name)

            if len(_muted) > 0:
                await self.bot.say('{} Successfully muted {} from **{}**.'.format(success, ', '.join(_muted), message.channel.server.name))

            if len(_could_not_mute) > 0 and len(_muted) == 0:
                await self.bot.say('{} Could not mute {} due to insufficient permissions.'.format(fail, ', '.join(_could_not_mute)))


        elif not mute_from_server:
            _muted = []
            _could_not_mute = []

            for member in member_li:
                try:
                    member_roles = member.roles
                    del member_roles[0]
                    await self.bot.remove_roles(member, *member_roles)
                    await self.bot.edit_channel_permissions(message.channel, member, discord.PermissionOverwrite(send_messages=False, connect=False))
                    _muted.append(member.name)
                except discord.Forbidden:
                    _could_not_mute.append(member.name)

            if len(_muted) > 0:
                await self.bot.say('{} Successfully muted {} from #{}.'.format(success, ', '.join(_muted), message.channel.name))

            if len(_could_not_mute) > 0 and len(_muted) == 0:
                await self.bot.say('{} Could not mute {} due to insufficient permissions.'.format(fail, ', '.join(_could_not_mute)))

        else:
            return

    @commands.command(pass_context=True)
    async def kick(self, ctx):
        members_to_kick = ctx.message.mentions
        kicked = []
        could_not_kick = []
        for i in members_to_kick:
            try:
                await self.bot.kick(i)
                kicked.append(i.name)
            except discord.Forbidden:
                could_not_kick.append(i.name)

        if len(kicked) > 0:
            await self.bot.say('{} Successfully kicked {} from **{}**.'.format(success, ', '.join(kicked), ctx.message.channel.server.name))

        if len(could_not_kick) > 0 and len(kicked) == 0:
            await self.bot.say('{} Could not kick {} due to insufficient permissions.'.format(fail, ', '.join(could_not_kick)))


    @commands.command(pass_context=True)
    async def ban(self, ctx):
        members_to_ban = ctx.message.mentions
        banned = []
        could_not_ban = []
        for i in members_to_ban:
            try:
                await self.bot.ban(i, delete_message_days=0)
                banned.append(i.name)
            except discord.Forbidden:
                could_not_ban.append(i.name)

        if len(banned) > 0:
            await self.bot.say('{} Successfully banned {} from **{}**.'.format(success, ', '.join(banned), ctx.message.channel.server.name))

        if len(could_not_ban) > 0 and len(banned) == 0:
            await self.bot.say('{} Could not ban {} due to insufficient permissions.'.format(fail, ', '.join(could_not_ban)))

    @commands.command(pass_context=True)
    async def mute(self, ctx):
        message = ctx.message
        members_to_mute = message.mentions

        await self._mute_members(message, members_to_mute, mute_from_server=False)

    @commands.command(pass_context=True)
    async def servermute(self, ctx):
        message = ctx.message
        members_to_mute = message.mentions

        await self._mute_members(message, members_to_mute, mute_from_server=True)





def setup(bot):
    bot.add_cog(Moderation(bot))
