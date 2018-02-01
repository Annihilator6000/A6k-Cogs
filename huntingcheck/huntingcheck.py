import discord
import os, re
import asyncio
import datetime
import time
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
        self.loopsleep = 900
        self.reloadchannel = '260933604706615296'  # bot-testing
            # server id
                # user id
                    # author_name : user's name
                    # score :
                        # chicken : 1
                        # duck : 3
                        # penguin : 7
                        # pigeon : 2
                    # total : 13
        try:
            self.huntingcog = self.bot.get_cog('Hunting')
        except:
            self.huntingcog = None

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions()
    async def huntinginfo(self, ctx):
        """Displays info for the hunting cog."""
        # next hunting event:
        # huntingcog = get_cog(hunting)
        # huntingcog.next ???
        # in the check loop check the next value. If it's more than hunt_interval_maximum reload the hunting cog
        # from hunting cog:
        # if self.next:
        #    time = abs(datetime.datetime.utcnow() - self.next)
        #    total_seconds = int(time.total_seconds())
        if self.huntingcog:
            # await self.bot.say("Hunting cog settings/info will be displayed here. Eventually...")
            # get stuff here - load it from the hunting cog - self.huntingcog.scores self.huntingcog.settings...
            hsettings = self.huntingcog.settings
            await self.bot.say("Hunting settings:\nMin time: {}\nMax time: {}\nTimeout: {}".format(self.huntingcog.settings['hunt_interval_minimum'],
                                                                                                   self.huntingcog.settings['hunt_interval_maximum'],
                                                                                                   self.huntingcog.settings['wait_for_bang_timeout']))
            await self.bot.say("Hunting active in this server: {}".format("Yes" if ctx.message.server.id in self.huntingcog.subscriptions else "No"))
        else:
            await self.bot.say("I couldn't find the hunting cog ¯\\_(ツ)_/¯")
    
    async def huntingcheck(self):
        # set up loop/task here
        while self == self.bot.get_cog('HuntingCheck'):
            if self.huntingcog is not None:
                # put checks here
                if self.huntingcog.next:
                    # valid 'next' time
                    time = abs(datetime.datetime.utcnow() - self.huntingcog.next)
                    total_seconds = int(time.total_seconds())
                    maxtime = self.huntingcog.settings['hunt_interval_maximum']
                    if maxtime > self.loopsleep:
                        self.loopsleep = maxtime + 300  # set loop check wait for max hunt interval + 5 mins
                    if total_seconds > maxtime:
                        # reload hunting cog here
                        self.reloadhunting()
            else:
                # maybe have a start/stop feature for the event/loop and stop it here instead
                return
            
            await asyncio.sleep(self.loopsleep)  # 15 minutes or max + 5 minutes

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
        data['content'] = "..reload hunting"
        fake_message = discord.Message(**data)
        self.bot.dispatch('message', fake_message)

def setup(bot):
    n = HuntingCheck(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.huntingcheck())
    bot.add_cog(n)