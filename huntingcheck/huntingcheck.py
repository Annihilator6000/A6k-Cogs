import discord
import os, re
import asyncio
import datetime
import time
import random
from random import randint
from discord.ext import commands
from .utils import checks
from .utils.dataIO import dataIO
from __main__ import send_cmd_help

class HuntingCheck:

    def __init__(self, bot):
        self.bot = bot
        self.dir = "data/hunting"
        self.settingsfile = self.dir + "/settings.json"  # hunt_interval_minimum and maximum, wait_for_bang_timeout
        self.subfile = self.dir + "/subscriptions.json"  # subscriptions in server : channel format
        self.scorefile = self.dir + "/scores.json"  # scores in the format:
            # server id
                # user id
                    # author_name : user's name
                    # score :
                        # chicken : 1
                        # duck : 3
                        # penguin : 7
                        # pigeon : 2
                    # total : 13
        self.loopsleep = 900  # 900 seconds = 15 minutes
        self.pm = False  # set to true to PM the bot owner if hunting is reloaded
                         # set to false to send a message to the console instead
        self.reloadchannel = '260933604706615296'  # bot-testing
        try:
            self.huntingcog = self.bot.get_cog('Hunting')
        except:
            self.huntingcog = None

    @commands.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def messuphunting(self, ctx):
        """Messes up the hunting cog 'next' value for testing."""
        if self.huntingcog:
            print("Old hunting next: {}".format(self.huntingcog.next))
            self.huntingcog.next = datetime.datetime.fromtimestamp(int(time.mktime(datetime.datetime.utcnow().timetuple())) + 2400)
            print("New hunting next: {}".format(self.huntingcog.next))

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions()
    async def huntinginfo(self, ctx):
        """Displays info for the hunting cog."""
        if self.huntingcog:
            hsettings = self.huntingcog.settings
            broken = False
            msg = "Hunting settings:\nMin time: {}\nMax time: {}\nTimeout: {}".format(self.huntingcog.settings['hunt_interval_minimum'],
                                                                                      self.huntingcog.settings['hunt_interval_maximum'],
                                                                                      self.huntingcog.settings['wait_for_bang_timeout'])
            msg += "\nHunting active in this server: {}".format("Yes" if ctx.message.server.id in self.huntingcog.subscriptions else "No")
            next_time = abs(datetime.datetime.utcnow() - self.huntingcog.next)
            total_seconds = int(next_time.total_seconds())
            maxtime = self.huntingcog.settings['hunt_interval_maximum']
            if total_seconds > maxtime:
                broken = True
            msg += "\nSeconds left until next hunt: {}".format(total_seconds)
            msg += "\nHunting is{} currently broken".format("" if broken else " not")
            if broken:
                msg += " and I will reload it within {} seconds.".format(self.loopsleep)
            else:
                msg += "."
            await self.bot.say(msg)
        else:
            await self.bot.say("I couldn't find the hunting cog ¯\\_(ツ)_/¯")
    
    async def huntingcheck(self):
        while self == self.bot.get_cog('HuntingCheck'):
            if self.huntingcog is not None:
                if self.huntingcog.next:
                    next_time = abs(datetime.datetime.utcnow() - self.huntingcog.next)
                    total_seconds = int(next_time.total_seconds())
                    maxtime = self.huntingcog.settings['hunt_interval_maximum']
                    if maxtime > self.loopsleep:
                        self.loopsleep = maxtime + 300  # set loop check wait for max hunt interval + 5 mins
                    if total_seconds > maxtime:
                        wait_time = random.randrange(self.huntingcog.settings['hunt_interval_minimum'], self.huntingcog.settings['hunt_interval_maximum'])
                        self.huntingcog.next = datetime.datetime.fromtimestamp(int(time.mktime(datetime.datetime.utcnow().timetuple())) + wait_time)
                        self.reloadhunting()
                        next_time = abs(datetime.datetime.utcnow() - self.huntingcog.next)
                        total_seconds_fixed = int(next_time.total_seconds())
                        msg = "The hunting cog was broken and has been reloaded. Previous next: {} Fixed next: {}".format(total_seconds, total_seconds_fixed)
                        if self.pm:
                            target = discord.utils.get(self.bot.get_all_members(), id=self.bot.settings.owner)
                            await self.bot.send_message(target, "{}".format(msg))
                        else:
                            print("[{}] huntingcheck.py: {}".format(datetime.datetime.utcnow(), msg))
            else:
                # maybe have a start/stop feature for the event/loop and stop it here instead
                return
            
            await asyncio.sleep(self.loopsleep)  # 15 minutes, or max + 5 minutes if max > 15 minutes

    def reloadhunting(self):
        channel = self.bot.get_channel(self.reloadchannel)
        data = {}
        data['timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.gmtime())
        data['id'] = randint(10**(17), (10**18) - 1)
        data['channel'] = self.bot.get_channel(self.reloadchannel)
        data['author'] = {'id': self.bot.settings.owner}
        data['nonce'] = randint(-2**32, (2**32) -1)
        data['channel_id'] = self.reloadchannel
        data['reactions'] = []
        data['content'] = "{}reload hunting".format(self.bot.settings.prefixes[0])
        fake_message = discord.Message(**data)
        self.bot.dispatch('message', fake_message)

def setup(bot):
    n = HuntingCheck(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.huntingcheck())
    bot.add_cog(n)