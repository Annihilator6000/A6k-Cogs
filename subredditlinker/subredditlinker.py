import os
import re
import discord
from discord.ext import commands
from .utils import checks
from .utils.dataIO import dataIO
from __main__ import send_cmd_help

class SubredditLinker:
    """Creates links for subreddits found in comments."""
    
    def __init__(self, bot):
        self.bot = bot
        self.datafile = "data/subredditlinker/subredditlinker.json"
        self.ignores = dataIO.load_json(self.datafile)

    @commands.group(pass_context=True, aliases=["srl"])
    @checks.mod_or_permissions(manage_roles=True)
    async def subredditlinker(self, ctx):
        """Hmmm, what does this button do? NO! NOT THAT ONE..."""
        if ctx.invoked_subcommand is None:
            await self.bot.say("SubredditLinker creates usable links from textual representations of subreddits that I find in comments.")
            await send_cmd_help(ctx)
    
    @subredditlinker.command(pass_context=True)
    async def ignore(self, ctx, channel):
        """Sets channels to be ignored by SubredditLinker."""
        if "<#" in channel:
            channel = str.replace(channel, "<#", "")
            channel = str.replace(channel, ">", "")
            try:
                channel = self.bot.get_channel(channel)
            except:
                await self.bot.say("That doesn't appear to be a valid channel.")
                return
        if isinstance(channel, discord.Channel):
            if channel.server.id not in self.ignores.keys():
                self.ignores[channel.server.id] = [channel.id]
                await self.bot.say("**{}** has been added to the ignore list.".format(channel.name))
            else:
                if channel.id not in self.ignores[channel.server.id]:
                    self.ignores[channel.server.id].append(channel.id)
                    await self.bot.say("**{}** has been added to the ignore list.".format(channel.name))
                else:
                    await self.bot.say("I already have that channel in my ignore list.")
                    return
            dataIO.save_json(self.datafile, self.ignores)
    
    @subredditlinker.command(pass_context=True)
    async def unignore(self, ctx, channel):
        """Removes an ignored channel."""
        if "<#" in channel:
            channel = str.replace(channel, "<#", "")
            channel = str.replace(channel, ">", "")
            try:
                channel = self.bot.get_channel(channel)
            except:
                await self.bot.say("That doesn't appear to be a valid channel.")
                return
        if isinstance(channel, discord.Channel):
            if channel.server.id not in self.ignores.keys():
                await self.bot.say("This server doesn't have any ignored channels.")
                return
            else:
                if channel.id in self.ignores[channel.server.id]:
                    self.ignores[channel.server.id].remove(channel.id)
                else:
                    await self.bot.say("That channel is not in my ignore list.")
                    return
            dataIO.save_json(self.datafile, self.ignores)
            await self.bot.say("**{}** has been removed from my ignore list.".format(channel.name))
    
    @subredditlinker.command(pass_context=True)
    async def ignorelist(self, ctx):
        """Displays ignored channels."""
        ilist = None
        try:
            chanlist = []
            for chanid in self.ignores[ctx.message.server.id]:
                chanlist.append(discord.utils.get(ctx.message.server.channels, id=chanid).name)
            ilist = "\n".join(chanlist)
        except:
            ilist = ""
        await self.bot.say("SubredditLinker is ignoring the following channels:\n```\n{}\n```".format(ilist))

    async def message_listener(self, message):
        # try:
        #     if message.channel.id in self.ignores[message.server.id]:
        #         return
        # except:
        #     pass
        server = message.server
        if server is None:
            return
        if message.author == self.bot.user:
            return
        if server.id in self.ignores.keys():
            if message.channel.id in self.ignores[server.id]:
                return
        # subcheck = re.compile(r'\s\/[rR]\/[a-zA-Z0-9_]{3,21}\s', re.IGNORECASE)
        # subcheck = re.compile(r'(?<!\S)\/r\/[a-zA-Z0-9_]{3,21}(?:\/)?(?!\S)', re.IGNORECASE)
        subcheck = re.compile(r'(/[rR]/[a-zA-Z0-9_]{3,21}(?:/))', re.IGNORECASE)
        subs = subcheck.findall(message.content)
        if len(subs) > 0:
            slembed = discord.Embed(description="SubredditLinker", colour=discord.Color.magenta())
            sublinks = None
            flinks = []
            for s in subs:
                flinks.append("[{}]({})".format(s, "https://www.reddit.com" + s + "/"))
            sublinks = "\n".join(flinks)
            embedname = "Link:" if len(subs) == 1 else "Links:"
            slembed.add_field(name=embedname, value=sublinks, inline=False)
            slembed.set_footer(text="I create usable links for textual representations of subreddits that I find in comments. You can click a link above to visit the subs that I find.")
            await self.bot.send_message(message.server.get_channel(message.channel.id), embed=slembed)


def check_folders():
    if not os.path.exists("data/subredditlinker"):
        print("Creating data/subredditlinker folder...")
        os.makedirs("data/subredditlinker")


def check_files():
    f = "data/subredditlinker/subredditlinker.json"
    if not dataIO.is_valid_json(f):
        print("Creating default raffle/subredditlinker.json...")
        dataIO.save_json(f, {})

def setup(bot):
    check_folders()
    check_files()
    n = SubredditLinker(bot)
    bot.add_cog(n)
    bot.add_listener(n.message_listener, "on_message")
