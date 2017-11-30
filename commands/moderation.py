import discord
import asyncio
from discord.ext import commands
from utils import config as c

config = c.Config()
success = config.success
fail = config.fail
s_id = str(config.mute_role_id)
d_id = config.default_server_role_id
mod_ids = config.mod_role_ids

class Moderation(object):
    def __init__(self, bot):
        self.bot = bot

    def get_role(self, _id, message):
        if message is None:
            return
        else:
            for i in message.channel.server.roles:
                print(i.id)
                if i.id == _id:
                    return i

    def is_mod(self, member_roles):
        for x in member_roles:
            if x.id in mod_ids:
                return True

        return False

    async def _mute_members(self, message, member_li, mute_from_server=False):

        if mute_from_server:
            _muted = []
            _could_not_mute = []
            snake_role = [self.get_role(s_id, message)]

            if not snake_role:
                return

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
                    _muted.append('<@{}>'.format(member.id))
                except discord.Forbidden:
                    _could_not_mute.append('<@{}>'.format(member.id))

            if len(_muted) > 0:
                await self.bot.say('{} Successfully muted {} from <#{}>.'.format(success, ', '.join(_muted), message.channel.id))

            if len(_could_not_mute) > 0 and len(_muted) == 0:
                await self.bot.say('{} Could not mute {} due to insufficient permissions.'.format(fail, ', '.join(_could_not_mute)))

        else:
            return

    async def _unmute_members(self, message, member_li, unmute_from_server=False):
        if unmute_from_server:
            _unmuted = []
            _could_not_unmute = []
            DEFAULT_ROLE = [self.get_role(d_id, message)]

            for member in member_li:
                try:
                    member_roles = member.roles
                    del member_roles[0]
                    await self.bot.remove_roles(member, *member_roles)
                    await self.bot.add_roles(member, *DEFAULT_ROLE)
                    _unmuted.append('<@{}>'.format(member.id))

                except discord.Forbidden:
                    _could_not_unmute.append('<@{}>'.format(member.id))

            if len(_unmuted) > 0:
                await self.bot.say('{} Successfully unmuted {} from **{}**.'.format(success, ', '.join(_unmuted), message.channel.server.name))

            if len(_could_not_unmute) > 0 and len(_unmuted) == 0:
                await self.bot.say('{} Could not unmute {} due to insufficient permissions.'.format(fail, ', '.join(_could_not_unmute)))


        elif not unmute_from_server:
            _unmuted = []
            _could_not_unmute = []

            for member in member_li:
                try:
                    member_roles = member.roles
                    del member_roles[0]
                    await self.bot.remove_roles(member, *member_roles)
                    await self.bot.edit_channel_permissions(message.channel, member, discord.PermissionOverWrite(send_messages=None, connect=None))
                    _unmuted.append('<@{}>'.format(member.id))
                except discord.Forbidden:
                    _could_not_unmute.append('<@{}>'.format(member.id))

            if len(_unmuted) > 0:
                await self.bot.say('{} Successfully unmuted {} from <#{}>.'.format(success, ', '.join(_unmuted), message.channel.id))

            if len(_could_not_unmute) > 0 and len(_unmuted) == 0:
                await self.bot.say('{} Could not unmute {} due to insufficient permissions.'.format(fail, ', '.join(_could_not_unmute)))

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
                kicked.append('<@{}>'.format(i.id))
            except discord.Forbidden:
                could_not_kick.append('<@{}>'.format(i.id))

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
                banned.append('<@{}>'.format(i.id))
            except discord.Forbidden:
                could_not_ban.append('<@{}>'.format(i.id))

        if len(banned) > 0:
            await self.bot.say('{} Successfully banned {} from **{}**.'.format(success, ', '.join(banned), ctx.message.channel.server.name))

        if len(could_not_ban) > 0 and len(banned) == 0:
            await self.bot.say('{} Could not ban {} due to insufficient permissions.'.format(fail, ', '.join(could_not_ban)))

    @commands.command(pass_context=True)
    async def mute(self, ctx):
        message = ctx.message
        members_to_mute = message.mentions
        author_roles = message.author.roles

        if not self.is_mod(author_roles):
            await self.bot.say('{} Sorry, you can\'t use that command.'.format(fail))
            return
        else:
            await self._mute_members(message, members_to_mute, mute_from_server=False)

    @commands.command(pass_context=True)
    async def servermute(self, ctx):
        message = ctx.message
        members_to_mute = message.mentions
        author_roles = message.author.roles

        if not self.is_mod(author_roles):
            await self.bot.say('{} Sorry, you can\'t use that command.'.format(fail))
            return
        else:
            await self._mute_members(message, members_to_mute, mute_from_server=True)

    @commands.command(pass_context=True)
    async def unmute(self, ctx):
        message = ctx.message
        members_to_unmute = message.mentions
        author_roles = message.author.roles

        if not self.is_mod(author_roles):
            await self.bot.say('{} Sorry, you can\'t use that command.'.format(fail))
            return
        else:
            await self._unmute_members(message, members_to_unmute, unmute_from_server=False)

    @commands.command(pass_context=True)
    async def serverunmute(self, ctx):
        message = ctx.message
        members_to_unmute = message.mentions
        author_roles = message.author.roles

        if not self.is_mod(author_roles):
            await self.bot.say('{} Sorry, you can\'t use that command.'.format(fail))
            return
        else:
            await self._unmute_members(message, members_to_unmute, unmute_from_server=True)
        
def setup(bot):
    bot.add_cog(Moderation(bot))
