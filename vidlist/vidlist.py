import discord
import os
import asyncio

from discord.ext import commands
from cogs.utils.dataIO import fileIO
from cogs.utils.chat_formatting import *
from __main__ import send_cmd_help

class Settings(object):
    pass

#   vidlist cog for RedBot
#   version 0.1.0
#   Built upon rss cog for RedBot (https://github.com/tekulvw/Squid-Plugins/blob/master/rss/rss.py)

#   TODO:
#       Add a function to prune dead links
#       Add a search function that will search for a video name in all categories
#       Add a delete category function

class Lists(object):
    def __init__(self):
        self.check_folders()
        # {server:{category:{name:,url:}}}
        self.lists = fileIO("data/vidlist/list.json", "load")
    
    def save_lists(self):
        fileIO("data/vidlist/list.json", "save", self.lists)

    def check_folders(self):
        if not os.path.exists("data/vidlist"):
            print("Creating data/vidlist folder...")
            os.makedirs("data/vidlist")
        self.check_files()

    def check_files(self):
        f = "data/vidlist/list.json"
        if not fileIO(f, "check"):
            print("Creating empty video list.json...")
            fileIO(f, "save", {})

    def add_video(self, ctx, name, url, category):
        name = name.lower()
        server = ctx.message.server.id
        if server not in self.lists:
            self.lists[server] = {}
        if category not in self.lists[server]:
            self.lists[server][category] = {}
        self.lists[server][category][name] = {}
        self.lists[server][category][name]['url'] = url
        self.save_lists()
    
    async def delete_list(self, ctx, category, name):
        name = name.lower()
        server = ctx.message.server.id
        if server not in self.lists:
            return False
        if category not in self.lists[server]:
            return False
        if name not in self.lists[server][category].lower():
            return False
        del self.lists[server][category][name]
        self.save_lists()
        return True
    
    def get_category_names(self, server):
        if isinstance(server, discord.Server):
            server = server.id
        ret = []
        if server in self.lists:
            for server in self.lists:
                ret = ret + sorted(self.lists[server].keys())
        return ret
    
    def get_category_items(self, server, category):
        if isinstance(server, discord.Server):
            server = server.id
        ret = []
        if server in self.lists:
            if category in self.lists[server]:
                ret = sorted(self.lists[server][category].keys())
        return ret

    def get_url(self, server, category, name):
        name = name.lower()
        if isinstance(server, discord.Server):
            server = server.id
        ret = []
        if server in self.lists:
            if category in self.lists[server]:
                if name in self.lists[server][category]:
                    ret = self.lists[server][category][name]['url']
        return ret

class vidlist(object):
    def __init__(self, bot):
        self.bot = bot
        self.settings = Settings()
        self.lists = Lists()
        #self.session = aiohttp.ClientSession()
    
    def __unload(self):
        self.session.close()
    
    @commands.group(pass_context=True)
    async def vidlist(self, ctx):
        """Video list commands"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
    
    @vidlist.command(pass_context=True, name="addvideo")
    async def _list_add(self, ctx, name: str, url: str, category: str="default"):
        """Add a video to <category>. If a category isn't specified "default" will be used.\nIf there is a space in the name it must be encased in quotes."""
        valid_url = False
        if url != "":
            valid_url = True
        if category == "":
            category = "default"
        if valid_url:
            self.lists.add_video(ctx, name, url, category)
            await self.bot.say('Video "{}" added.'.format(name))
        else:
            await self.bot.say('Invalid or unavailable URL.')
    
    @vidlist.command(pass_context=True, name="categories")
    async def _list_categories(self, ctx):
        """Gets a list of the current categories"""
        msg = "Current lists:\n\t"
        msg += "\n\t".join(self.lists.get_category_names(ctx.message.server))
        await self.bot.say(box(msg))

    @vidlist.command(pass_context=True, name="list")
    async def _show_category_list(self, ctx, category: str):
        """Lists the videos in a category"""
        categories = self.lists.get_category_names(ctx.message.server)
        if category in categories:
            msg = "Videos in {}:\n\t".format(category)
            msg += "\n\t".join(self.lists.get_category_items(ctx.message.server, category))
            await self.bot.say(box(msg))
        else:
            await self.bot.say('List not found')
    
    @vidlist.command(pass_context=True, name="video")
    async def _show_videos(self, ctx, name: str, category: str="default"):
        """Displays a video"""
        server = ctx.message.server.id
        categories = self.lists.get_category_names(ctx.message.server)
        if category in categories:
            catlist = self.lists.get_category_items(ctx.message.server, category)
            if name.lower() in catlist:
                url = self.lists.get_url(server, category, name)
                await self.bot.say("{} ({}):\n{}".format(name, category, url))
            else:
                await self.bot.say("Video **{}** not found in category **{}**".format(name, category))
        else:
            await self.bot.say("**{}** is not a valid category".format(category))

    @vidlist.command(pass_context=True, name="remove")
    async def _list_remove(self, ctx, category: str, name: str):
        """Removes a video from a category"""
        success = await self.lists.delete_list(ctx, category, name)
        if success:
            await self.bot.say('Video deleted.')
        else:
            await self.bot.say('Video not found!')

def setup(bot):
    n = vidlist(bot)
    bot.add_cog(n)
