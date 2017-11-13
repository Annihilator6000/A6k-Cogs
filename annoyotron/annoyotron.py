import os
import re
import discord
import asyncio
from discord.ext import commands
from .utils import checks
from .utils.dataIO import dataIO
from __main__ import send_cmd_help

# TODO: Make the bot DM instead of clog up the channels. Or delete the old message and add the new one.
#       Check the DM function for an exception (can't DM - user has it turned off) and send the message to the channel instead.
#       also - maybe have aot clean up after itself after it ends?
#    Need to also check for/remove @everyone and @here in case people start being douchebags


class AnnoyOTron:
    """Annoy members that need to do something until they do that thing!"""
    
    def __init__(self, bot):
        self.bot = bot
        self.data = []
        self.listentochans = []

    # self.data:
    # {
    #     userid: {
    #         "amount": int,
    #         "channel": channel id (int),
    #         "countdown": int,
    #         "message": string,
    #         "users": {"user1", "user2"}
    #     }
    # }

    @commands.group(pass_context=True, no_pm=True, aliases=["aot"])
    @commands.has_any_role('Admin', 'admins', 'Moderators', 'Global Operators', 'TFC Leaders')
    @checks.mod_or_permissions(manage_roles=True)
    async def annoyotron(self, ctx):
        """Need to annoy some users because they need to do something? Then this is the command for you!"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @annoyotron.command(pass_context=True, no_pm=True)
    async def start(self, ctx, amount: int, countdowntimer: int, message: str, *users: discord.Member):
        """This will send 1 annoying message every minute, up to the amount specified (max 30), to the user(s) indicated.
        
        <amount> must be a whole number. <countdowntimer> can take any number. It will add a countdown, in minutes, to the messages. Set it to 0 to disable the countdown.
        If the <message> is more than 1 word it needs to be enclosed in quotes. You can add as many users to the end as you would like to. [users...] must be mentions.
        
        Users that send a message in the same channel that AnnoyOTron is active in will be removed from the ping list."""
        userid = ctx.message.author.id
        if amount < 1:
            await self.bot.say("Let's think about this for a second. Do you really think that I can send a message less than once?")
            await asyncio.sleep(1)
            await self.bot.say("No? Oh, ok. I didn't think so.")
            return
        if message is None or len(message) < 1:
            await self.bot.say("You need to enter a message, silly goose.")
            return
        if re.match(r'^<@[0-9]{4,}>$', message):
            await self.bot.say("You need to enter a message, silly goose.")
            return
        if len(users) < 1:
            await self.bot.say("You forgot to enter some users to annoy. Please RTFM and try again.")
            return
        for user in users:
            if not isinstance(user, discord.Member):
                await self.bot.say("Hmmmmmmm. You seem to have entered some funky data for the users, because they're not all user mentions. Please try again, but this time use user mentions instead of whatever nonsense that was before.")
        if self.data is not None:
            if len(self.data) > 0:
                if userid in self.data.keys():
                    await self.bot.say("You are already annoying at least one person. Wait until I'm finished annoying users for you, or stop your annoy and make a new one.")
                    return
        if amount > 30:
            amount = 30
            await self.bot.say("`amount` can be a maximum of 30. Since you entered more than that I am automatically setting it to 30.")
        ausers = []
        for u in users:
            ping = "<@" + str(u.id) + ">"
            ausers.append(ping)
        if countdowntimer < 0:
            countdowntimer = 0
        self.data = {userid: {"amount": amount, "channel": ctx.message.channel.id, "countdown": countdowntimer, "message": message, "users": ausers}}
        self.listentochans.append(ctx.message.channel.id)
        await self.bot.say("AnnoyOTron started. YAY!!!")
        count = 0
        timermsg = ""
        self.bot.add_listener(self.waitforusers, "on_message")
        while self.data[userid]["amount"] > 0:
            count += 1
            await asyncio.sleep(1)
            # check to see if the user stopped it
            if self.data[userid]["amount"] == 0:
                del self.data[userid]
                break
            if count == 60:
                if self.data[userid]["countdown"] > 0:
                    timermsg = "{} minutes left. ".format(self.data[userid]["countdown"])
                else:
                    timermsg = ""
                await self.bot.say("\U0001f6a8 {}{} {} \U0001f6a8".format(timermsg, self.data[userid]["message"], " ".join(self.data[userid]["users"])))
                self.data[userid]["amount"] -= 1
                count = 0
                if self.data[userid]["countdown"] > 0:
                    self.data[userid]["countdown"] -= 1
        self.bot.remove_listener(self.waitforusers)
        self.listentochans.remove(ctx.message.channel.id)
        await self.bot.say("AnnoyOTron ended \U0001f622")

    @annoyotron.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """This command stops your annoying messages. Duh."""
        userid = ctx.message.author.id
        if self.data is not None:
            if len(self.data) < 1:
                await self.bot.say("You have no annoying messages active at this time.")
                return
        if userid not in self.data.keys():
            await self.bot.say("You have no annoying messages active at this time.")
            return
        if self.data[userid]["amount"] == 0:
            await self.bot.say("You have no annoying messages active at this time.")
        self.data[userid]["amount"] = 0
        await self.bot.say("Your annoying messages have been stopped.")
        
    @annoyotron.command(pass_context=True, no_pm=True)
    async def removeuser(self, ctx, user: discord.Member):
        """Removes a user that is currently being annoyed."""
        await self._removeuser(ctx.message.author.id, user, False)
        '''if user is None:
            await self.bot.say("You need to enter a user to remove from the ones that I'm currently annoying.")
            return
        if not isinstance(user, discord.Member):
            await self.bot.say("You entered something. I'll give you that much. Unfortunately, it's not a user mention. So no we're back to square one. Please try again.")
            return
        # check here to see if the user is in in the annoy list
        userid = ctx.message.author.id
        userping = "<@" + str(user.id) + ">"
        if self.data is not None:
            if len(self.data) > 0:
                if userid not in self.data.keys():
                    await self.bot.say("You have no annoying messages active at this time")
                    return
                if userping not in self.data[userid]["users"]:
                    await self.bot.say("That user is not currently being annoyed.")
                    return
        pingusers = []
        for u in self.data[userid]["users"]:
            if userping not in u:
                pingusers.append(u)
        del self.data[userid]["users"]
        if len(pingusers) > 0:
            self.data[userid]["users"] = pingusers
        else:
            self.data[userid]["amount"] = 0
        await self.bot.say("Ok, fine. I'll stop annoying {}...".format(user.nick if user.nick else user.name))
        '''

    async def _removeuser(self, userid, user, fromlistener):
        # moving this to it's own function because when the listener is added it can be used by the listener and the manual function
        if user is None:
            await self.bot.say("You need to enter a user to remove from the ones that I'm currently annoying.")
            return
        if not isinstance(user, discord.Member):
            await self.bot.say("You entered something. I'll give you that much. Unfortunately, it's not a user mention. So no we're back to square one. Please try again.")
            return
        # check here to see if the user is in in the annoy list
        #userid = ctx.message.author.id
        userping = "<@" + str(user.id) + ">"
        if self.data is not None:
            if len(self.data) > 0:
                if userid not in self.data.keys():
                    await self.bot.say("You have no annoying messages active at this time")
                    return
                if userping not in self.data[userid]["users"]:
                    await self.bot.say("That user is not currently being annoyed.")
                    return
        pingusers = []
        for u in self.data[userid]["users"]:
            if userping not in u:
                pingusers.append(u)
        del self.data[userid]["users"]
        if len(pingusers) > 0:
            self.data[userid]["users"] = pingusers
        else:
            self.data[userid]["amount"] = 0
        if fromlistener:
            # need send_message because of the listener
            await self.bot.send_message(self.bot.get_channel(str(self.data[userid]["channel"])), "Darn it {}, you showed up. I *guess* I'll stop pinging you then... \U0001f612".format(user.nick if user.nick else user.name))
        else:
            await self.bot.say("Ok, fine. I'll stop annoying {}...".format(user.nick if user.nick else user.name))

    async def waitforusers(self, message):
        # listen to see if the user responds in the channel
        server = message.server
        if server is None:
            return
        if message.author.id == self.bot.user.id:
            return
        if message.channel.id not in self.listentochans:
            return
        authorid = message.author.id
        authormention = "<@" + str(authorid) + ">"
        if len(self.data) > 0:
            for uid in self.data:
                if authormention in self.data[uid]["users"] and message.channel.id in self.data[uid]["channel"]:
                    # await self.bot.send_message(message.channel, "Darn, you showed up. I *guess* I'll stop pinging you then... \U0001f612")
                    await self._removeuser(uid, message.author, True)
                    break

def setup(bot):
    n = AnnoyOTron(bot)
    bot.add_cog(n)
