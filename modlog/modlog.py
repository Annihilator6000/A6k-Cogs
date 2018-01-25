from discord.ext import commands
from cogs.utils import checks
import datetime
from cogs.utils.dataIO import fileIO
import discord
import asyncio
import os
import re
from random import choice, randint

inv_settings = {"Channel": None, "toggleedit": False, "toggledelete": False, "toggleuser": False, "toggleroles": False,
                "togglevoice": False, "togglejoin": False, "toggleleave": False, "toggleban": False}


class ModLog:
    def __init__(self, bot):
        self.bot = bot
        self.direct = "data/modlogset/settings.json"

    @checks.admin_or_permissions(manage_server=True)
    @commands.group(name='modlogtoggle', pass_context=True, no_pm=True)
    async def modlogtoggles(self, ctx):
        """Toggle which server activity to log"""
        if ctx.invoked_subcommand is None:
            db = fileIO(self.direct, "load")
            await self.bot.send_cmd_help(ctx)
            try:
                await self.bot.say("```Current settings:\a\n\a\n" + "Edit: " + str(
                    db[ctx.message.server.id]['toggleedit']) + "\nDelete: " + str(
                    db[ctx.message.server.id]['toggledelete']) + "\nUser: " + str(
                    db[ctx.message.server.id]['toggleuser']) + "\nRoles: " + str(
                    db[ctx.message.server.id]['toggleroles']) + "\nVoice: " + str(
                    db[ctx.message.server.id]['togglevoice']) + "\nJoin: " + str(
                    db[ctx.message.server.id]['togglejoin']) + "\nLeave: " + str(
                    db[ctx.message.server.id]['toggleleave']) + "\nBan: " + str(
                    db[ctx.message.server.id]['toggleban']) + "```")
            except KeyError:
                return

    @checks.admin_or_permissions(manage_server=True)
    @commands.group(pass_context=True, name='modlogset', no_pm=True)
    async def modlogset(self, ctx):
        """Change modlog settings"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @modlogset.command(pass_context=True, name='channel', no_pm=True)
    async def channel(self, ctx):
        """Set the channel to send notifications to"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if ctx.message.server.me.permissions_in(ctx.message.channel).send_messages:
            if server.id in db:
                db[server.id]['Channel'] = ctx.message.channel.id
                fileIO(self.direct, "save", db)
                await self.bot.say("Channel changed.")
                return
            if not server.id in db:
                db[server.id] = inv_settings
                db[server.id]["Channel"] = ctx.message.channel.id
                fileIO(self.direct, "save", db)
                await self.bot.say("I will now send toggled modlog notifications here")
        else:
            return

    @modlogset.command(name='disable', pass_context=True, no_pm=True)
    async def disable(self, ctx):
        """Disables the modlog"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            await self.bot.say("Server not found, use modlogset to set a channnel")
            return
        del db[server.id]
        fileIO(self.direct, "save", db)
        await self.bot.say("I will no longer send modlog notifications here")

    @modlogtoggles.command(name='edit', pass_context=True, no_pm=True)
    async def edit(self, ctx):
        """Toggle notifications when a member edits their message"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleedit"] == False:
            db[server.id]["toggleedit"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Edit messages enabled")
        elif db[server.id]["toggleedit"] == True:
            db[server.id]["toggleedit"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Edit messages disabled")

    @modlogtoggles.command(name='delete', pass_context=True, no_pm=True)
    async def delete(self, ctx):
        """Toggle notifications when a member delete their message"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggledelete"] == False:
            db[server.id]["toggledelete"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Delete messages enabled")
        elif db[server.id]["toggledelete"] == True:
            db[server.id]["toggledelete"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Delete messages disabled")
    
    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def join(self, ctx):
        """toggles notofications when a member joins the server."""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["togglejoin"] == False:
            db[server.id]["togglejoin"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Enabled join logs.")
        elif db[server.id]['togglejoin'] == True:
            db[server.id]['togglejoin'] = False
            fileIO(self.direct, 'save', db)
            await self.bot.say("Disabled join logs.")
    
    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def leave(self, ctx):
        """toggles notofications when a member leaves the server."""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleleave"] == False:
            db[server.id]["toggleleave"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Enabled leave logs.")
        elif db[server.id]['toggleleave'] == True:
            db[server.id]['toggleleave'] = False
            fileIO(self.direct, 'save', db)
            await self.bot.say("Disabled leave logs.")

    @modlogtoggles.command(name='user', pass_context=True, no_pm=True)
    async def user(self, ctx):
        """Toggle notifications when a user changes their profile"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleuser"] == False:
            db[server.id]["toggleuser"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("User messages enabled")
        elif db[server.id]["toggleuser"] == True:
            db[server.id]["toggleuser"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("User messages disabled")

    @modlogtoggles.command(name='roles', pass_context=True, no_pm=True)
    async def roles(self, ctx):
        """Toggle notifications when roles change"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleroles"] == False:
            db[server.id]["toggleroles"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Role messages enabled")
        elif db[server.id]["toggleroles"] == True:
            db[server.id]["toggleroles"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Role messages disabled")

    @modlogtoggles.command(name='voice', pass_context=True, no_pm=True)
    async def voice(self, ctx):
        """Toggle notifications when voice status change"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["togglevoice"] == False:
            db[server.id]["togglevoice"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Voice messages enabled")
        elif db[server.id]["togglevoice"] == True:
            db[server.id]["togglevoice"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Voice messages disabled")

    @modlogtoggles.command(name='ban', pass_context=True, no_pm=True)
    async def ban(self, ctx):
        """Toggle notifications when a user is banned"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleban"] == False:
            db[server.id]["toggleban"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Ban messages enabled")
        elif db[server.id]["toggleban"] == True:
            db[server.id]["toggleban"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Ban messages disabled")

    async def on_message_delete(self, message):
        poofid = "268940135331135490"
        radioid = "267047902839308298"
        if poofid in message.author.id:
            return
        if radioid in message.channel.id and message.content.str().startswith('1'):
            return
        server = message.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggledelete'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '[ %H:%M:%S ]'
        
        name = message.author
        name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
        delmessage = discord.Embed(description=name, colour=discord.Color.purple())
        infomessage = "A message by __{}__, was deleted in {} (mobile friendly: {})".format(message.author.nick if message.author.nick else message.author.name, message.channel.mention, message.channel.name)
        delmessage.add_field(name="Info:", value=infomessage, inline=False)
        #print("\nMessage type name: " + message.type.name + "\nMessage type val: " + str(message.type.value) + "\nMessage content: " + message.content + "\nNumber of embeds: " + str(len(message.embeds)) + "\nNumber of attachments: " + str(len(message.attachments)) + "\n")
        delmessage.add_field(name="Message:", value=message.content if len(message.content) > 0 else "<*Message content was empty or was an embed*>") # need to process embed. Also need to figure out if message is an uploaded image - those do not show up either. Maybe use image.url (discord url) in the delete message?
        if len(message.attachments) > 0:
            delmessage.add_field(name="Attachments:", value="{}".format(message.attachments))
        #if len(message.embeds) > 0:
        #    delmessage.add_field(name="Embeds:", value="{}".format(message.embeds))
        delmessage.set_footer(text="User ID: {}".format(message.author.id))
        delmessage.set_author(name=time.strftime(fmt) + " - Deleted Message", url="http://i.imgur.com/fJpAFgN.png")
        delmessage.set_thumbnail(url="http://i.imgur.com/fJpAFgN.png")

        try:
            await self.bot.send_message(server.get_channel(channel), embed=delmessage)
        except discord.HTTPException:
            await self.bot.send_message(server.get_channel(channel),
                                        "``{}`` {} ({}) Deleted his message in {}:\a\n\a\n ``{}``".format(
                                            time.strftime(fmt), message.author, message.author.id, message.channel,
                                            message.content))

    async def on_member_join(self, member):
        server = member.server
        db = fileIO(self.direct, 'load')
        if not server.id in db:
            return
        if db[server.id]['togglejoin'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '%H:%M:%S'
        #users = len([e.name for e in server.members]) #this is such a bad way to do this
        users = len(server.members)
        member_number = sorted(server.members, key=lambda m: m.joined_at).index(member) + 1
        #if db[server.id]["embed"] == True:
        # next lines up to 247 were indented 4 spaces...
        name = member
        name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
        joinmsg = discord.Embed(description=name, colour=discord.Color.red())
        memberwithdiscrim = member.name + "#" + member.discriminator
        infomessage = "__{}__ has joined the server.".format(memberwithdiscrim)
        joinmsg.add_field(name="Info:", value=infomessage, inline=False)
        joinmsg.add_field(name="Total Members:", value="{}".format(users), inline=False)
        joinmsg.set_footer(text="User ID: {} | Member #{}".format(member.id, member_number))
        joinmsg.set_author(name=time.strftime(fmt) + " - User Joined", url="http://www.emoji.co.uk/files/twitter-emojis/objects-twitter/11031-inbox-tray.png")
        joinmsg.set_thumbnail(url="http://www.emoji.co.uk/files/twitter-emojis/objects-twitter/11031-inbox-tray.png")
        try:
            await self.bot.send_message(server.get_channel(channel), embed=joinmsg)
        except:
        #    pass
        #if db[server.id]["embed"] == False:
            msg = ":white_check_mark: `{}` **{}** joined the server. Total members: {}.".format(time.strftime(fmt), member.name, users)
            await self.bot.send_message(server.get_channel(channel), msg)
        
    async def on_member_remove(self, member):
        server = member.server
        db = fileIO(self.direct, 'load')
        if not server.id in db:
            return
        if db[server.id]['toggleleave'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = "%H:%M:%S"
        #users = len([e.name for e in server.members])
        users = len(server.members)
        #member_number = sorted(server.members, key=lambda m: m.joined_at).index(member) + 1
        #if db[server.id]["embed"] == True:
        # next lines up to 279 were indented 4 spaces
        name = member
        name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
        leave = discord.Embed(description=name, colour=discord.Color.red())
        memberwithdiscrim = member.name + "#" + member.discriminator
        infomessage = "__{}__ has left the server.".format(memberwithdiscrim)
        leave.add_field(name="Info:", value=infomessage, inline=False)
        leave.add_field(name="Total Members:", value="{}".format(users), inline=False)
        leave.set_footer(text="User ID: {}".format(member.id))
        leave.set_author(name=time.strftime(fmt) + " - Leaving User", url="http://www.emoji.co.uk/files/mozilla-emojis/objects-mozilla/11928-outbox-tray.png")
        leave.set_thumbnail(url="http://www.emoji.co.uk/files/mozilla-emojis/objects-mozilla/11928-outbox-tray.png")
        try:
            await self.bot.send_message(server.get_channel(channel), embed=leave)
        except:
        #    pass
        #if db[server.id]["embed"] == False:
            msg = ":x: `{}` **{}** has left the server or was kicked. Total members {}.".format(time.strftime(fmt), member.name, users)
            await self.bot.send_message(server.get_channel(channel), msg)

    async def on_message_edit(self, before, after):
        server = before.server
        #print("on_message_edit server id: {}".format(server.id))
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggleedit'] == False:
            return
        if before.content == after.content:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '[ %H:%M:%S ]'
        
        name = before.author
        name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
        delmessage = discord.Embed(description=name, colour=discord.Color.green())
        infomessage = "A message by __{}__, was edited in {}".format(before.author.nick if before.author.nick else before.author.name, before.channel.mention)
        delmessage.add_field(name="Info:", value=infomessage, inline=False)
        delmessage.add_field(name="Before Message:", value=before.content, inline=False)
        delmessage.add_field(name="After Message:", value=after.content)
        delmessage.set_footer(text="User ID: {}".format(before.author.id))
        delmessage.set_author(name=time.strftime(fmt) + " - Edited Message", url="http://i.imgur.com/Q8SzUdG.png")
        delmessage.set_thumbnail(url="http://i.imgur.com/Q8SzUdG.png")

        try:
            await self.bot.send_message(server.get_channel(channel), embed=delmessage)
        except discord.HTTPException:        
            await self.bot.send_message(server.get_channel(channel),
                                    "``{}`` {} ({}) Edited his message in {}:\a\n\a\n__**Before:**__ ``{}``\a\n\a\n__**After:**__ ``{}``".format(
                                        time.strftime(fmt), before.author, before.author.id, before.channel,
                                        before.content, after.content))

    async def on_voice_state_update(self, before, after):
        server = before.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['togglevoice'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '[ %H:%M:%S ]'
        
        name = before
        name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
        updmessage = discord.Embed(description=name, colour=discord.Color.blue())
        infomessage = "__{}__'s voice status has changed".format(before.name)
        updmessage.add_field(name="Info:", value=infomessage, inline=False)
        updmessage.add_field(name="Voice Channel Before:", value=before.voice_channel)
        updmessage.add_field(name="Voice Channel After:", value=after.voice_channel)
        updmessage.set_footer(text="User ID: {}".format(before.id))
        updmessage.set_author(name=time.strftime(fmt) + " - Voice Channel Changed", url="http://i.imgur.com/8gD34rt.png")
        updmessage.set_thumbnail(url="http://i.imgur.com/8gD34rt.png")

        try:
            await self.bot.send_message(server.get_channel(channel), embed=updmessage)
        except discord.HTTPException:
            await self.bot.send_message(server.get_channel(channel),
                                        "``{}`` {} ({}) Voice status changed:\a\n\a\n__**Before:**__ ``{}``\a\n\a\n__**After:**__ ``{}``".format(
                                            time.strftime(fmt), before, before.id,
                                            before.voice_channel, after.voice_channel))

    async def on_member_update(self, before, after):
        server = before.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggleuser'] and db[server.id]['toggleroles'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '[ %H:%M:%S ]'
        if not before.nick == after.nick:
            name = before
            name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
            updmessage = discord.Embed(description=name, colour=discord.Color.orange())
            infomessage = "__{}__'s nickname has changed".format(before.name)
            updmessage.add_field(name="Info:", value=infomessage, inline=False)
            updmessage.add_field(name="Nickname Before:", value=before.nick)
            updmessage.add_field(name="Nickname After:", value=after.nick)
            updmessage.set_footer(text="User ID: {}".format(before.id))
            updmessage.set_author(name=time.strftime(fmt) + " - Nickname Changed", url="http://i.imgur.com/I5q71rj.png")
            updmessage.set_thumbnail(url="http://i.imgur.com/I5q71rj.png")

            try:
                await self.bot.send_message(server.get_channel(channel), embed=updmessage)
            except discord.HTTPException: 
                await self.bot.send_message(server.get_channel(channel),
                                            "``{}`` {} ({}) User nickname changed:\a\n\a\n__**Before:**__ ``{}``\a\n\a\n__**After:**__ ``{}``".format(
                                                time.strftime(fmt), before, before.id,
                                                before.nick, after.nick))
            return # hacky way to prevent the role change message below from showing up when a nick is changed

        if not before.roles == after.roles:
            bsenbool = False
            asenbool = False
            for b in before.roles:
                if "TFC Senate" in b.name:
                    bsenbool = True
            for a in after.roles:
                if "TFC Senate" in a.name:
                    asenbool = True
            #if "TFC Senate" in after.roles:
            #    print("Senate role detected in {}".format(after.nick if after.nick else after.name))
            #if "TFC Senate" in after.roles and "TFC Senate" not in before.roles:
            if asenbool and not bsenbool:
                #print("Senate logic works")
                senatemessage = "Hi {},\n\nWelcome to the TFC Senate on the r/BoomBeach server! By voting in the senate you are fulfilling one of the requirements to maintain your Task Force's verification status within the community. In #proposal people submit proposals they wish to discuss. Each week a docket is created to discuss in the #senate room. At the end of the week we vote via a Google form posted in #clerks-notes. Please contribute to discussion, or at the very least vote at the end of each week when you are pinged. You also will want to familiarize yourself with the Senate Acts log: https://docs.google.com/spreadsheets/d/1VBKm1Ly7j7MtLN71Dq7RDYQwSoQ9xRQQTMx1YZVIY7s/edit?usp=sharing".format(after.nick if after.nick else after.name)
                try:
                    await self.bot.send_message(discord.User(id=before.id), senatemessage)
                except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.HTTPException):
                    await self.bot.send_message(self.bot.get_channel('268477809343725568'), "{}, I'm posting this message here because I wasn't able to DM you.\n\n{}".format(senatemessage))
                except:
                    print("Something went wrong with the Senate DM to {}".format(after.nick if after.nick else after.name))
            name = before
            name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
            updmessage = discord.Embed(description=name, colour=discord.Color.gold())
            infomessage = "__{}__'s roles have changed".format(before.name)
            updmessage.add_field(name="Info:", value=infomessage, inline=False)
            # Add sorting to the roles
            before.roles.sort()
            after.roles.sort()
            updmessage.add_field(name="Roles Before:", value=", ".join([r.name for r in before.roles if r.name != "@everyone"]) if len(before.roles) > 1 else "-", inline=False)
            updmessage.add_field(name="Roles After:", value=", ".join([r.name for r in after.roles if r.name != "@everyone"]) if len(after.roles) > 1 else "-")
            updmessage.set_footer(text="User ID: {}".format(before.id))
            updmessage.set_author(name=time.strftime(fmt) + " - Role Changed", url="http://i.imgur.com/QD39cFE.png")
            updmessage.set_thumbnail(url="http://i.imgur.com/QD39cFE.png")

            try:
                await self.bot.send_message(server.get_channel(channel), embed=updmessage)
            except discord.HTTPException:
                await self.bot.send_message(server.get_channel(channel),
                                            "``{}`` {} ({}) User roles changed:\a\n\a\n__**Before:**__ ``{}``\a\n\a\n__**After:**__ ``{}``".format(
                                                time.strftime(fmt), before, before.id,
                                                ",".join([r.name for r in before.roles if r.name != "@everyone"]),
                                                ",".join([r.name for r in after.roles if r.name != "@everyone"])))

    async def on_member_ban(self, member):
        server = member.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggleuser'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '[ %H:%M:%S ]'
        
        name = member
        name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
        banmessage = discord.Embed(description=name, colour=discord.Color.red())
        infomessage = "__{}__ has been banned from the server.".format(member.nick if member.nick else member.name)
        banmessage.add_field(name="Info:", value=infomessage, inline=False)
        banmessage.set_footer(text="User ID: {}".format(member.id))
        banmessage.set_author(name=time.strftime(fmt) + " - Banned User", url="http://i.imgur.com/Imx0Znm.png")
        banmessage.set_thumbnail(url="http://i.imgur.com/Imx0Znm.png")

        try:
            await self.bot.send_message(server.get_channel(channel), embed=banmessage)
        except discord.HTTPException:
            await self.bot.send_message(server.get_channel(channel),
                                        "``{}`` {} ({}) has been __**banned**__".format(
                                            time.strftime(fmt), member, member.id))

    async def on_message(self, message):
        if message.server is None:
            # DM - don't try to add reactions
            return
        reactmtg = ['\U0001F1F2', '\U0001F1F9', '\U0001F1EC', '\U0001F1FC', '\U0001f1eb']
        if "181243681951449088" or "324245036961103883" in message.server.id:
            # BB Server
            #  if "336614088044183553" in message.channel.id:  # narwhals Hambo ping
            #      if "<@336614088044183553>" in message.content:
            #          return
            #      if "273542369297563649" in message.author.id:  # Intel
            #          return
            #      else:
            #          await self.bot.send_message(message.channel, "<@213733978446888960>")
            if "trichon" or "y98" in message.channel.name.lower():
                # was (?i)\shaha.?$
                r = re.search(r'(?i)\shaha[\.\!\@\#\$\%\^\&\*\-\+\=\?\~\`]?$', message.content, re.I)
                if r is not None:
                    for e in message.server.emojis:
                        if "smoak" in e.name:
                            #await asyncio.sleep(randint(1, 20))
                            await self.bot.add_reaction(message, e)
            revil = re.search(r'(?i)\shaha(ha)+.?$', message.content, re.I)
            if revil is not None:
                for e in message.server.emojis:
                    if "smoak" in e.name:
                        await self.bot.add_reaction(message, e)
                        await self.bot.add_reaction(message, '\U0001f608')
            q = re.search(r'^[Kk][\.!?]?$', message.content, re.I)
            if q is not None:
                k = '\U0001F1F0'
                await self.bot.add_reaction(message, k)
            popcorn = '\U0001F37F'
            if popcorn in message.content:
                for m in message.server.emojis:
                    if "butter" in m.name:
                        await self.bot.add_reaction(message, m)
                    if "salt" in m.name:
                        await self.bot.add_reaction(message, m)
            eyes = "\U0001f440"
            if "258379772093005824" in str(message.author.id) and message.content == eyes:
                await self.bot.add_reaction(message, eyes)
            '''
            if "239758162528436234" in str(message.author.id):
                if message.mentions is not None:
                    # if random.randint(0, 100) < 10:
                    chans = ["206104904786378752", "206096638320574464", "206097134754332673", "304021829331451904", "206097134754332673", "257366323326222336", "323565756145205249", "248132345868058624", "253060389657378816", "327869638870564867", "293876581372395521", "322174396145991680", "324520794161938432", "278628990535729152", "303599160513265665", "293790915745546240", "300357478129074187", "184856613151178752", "181243681951449088"]
                    randomchan = random.choice(chans)
                    while randomchan == str(message.channel.id):
                        randomchan = choice(chans)
                    orionping = "<@239758162528436234>"
                    msgtoorion = await self.bot.send_message(self.bot.get_channel(randomchan), orionping)
                    await asyncio.sleep(1)
                    await self.bot.delete_message(msgtoorion)
            '''
            if message.content.lower() is "rip":
                await self.bot.add_reaction(message, "\U0001f480")
                await self.bot.add_reaction(message, "\U0001f47b")
            if "319680206665154560" in message.channel.id:
                # Leadership announcement channel
                await self.bot.add_reaction(message, "\U00002705")
            if "268535621797019648" in message.channel.id:
                # change-requests
                for r in reactmtg:
                    await self.bot.add_reaction(message, r)

def check_folder():
    if not os.path.exists('data/modlogset'):
        print('Creating data/modlogset folder...')
        os.makedirs('data/modlogset')


def check_file():
    f = 'data/modlogset/settings.json'
    if not fileIO(f, 'check'):
        print('Creating default settings.json...')
        fileIO(f, 'save', {})


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(ModLog(bot))
