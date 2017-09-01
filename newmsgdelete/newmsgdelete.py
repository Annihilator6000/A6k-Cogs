import discord
from discord.ext import commands
#from .utils.dataIO import fileIO
from .utils.dataIO import dataIO
import os
import asyncio
import time
#import logging

delete_time = 10800 # KEEP THIS 30+ SECONDS!!!!
# 10800 is 3 hours
# BB Discord welcome channel - 296453860246159360
#
# do not use the monitor_channels below until I know that this works for sure!!!!!!!
monitor_channels = ["296453860246159360"]
#monitor_channels = ["293449067671977984"] # #mobile-stuff on my test server - use this while testing!!

#class MSGDeleteDelay:
class NewMsgDelete:
    """Automatically delete new messages in a channel after a certain time period."""

    def __init__(self, bot):
        self.bot = bot
        self.messagedata = dataIO.load_json("data/newmsgdelete/newmsgdelete.json")
        #self.units = {"minute" : 60, "hour" : 3600, "day" : 86400, "week": 604800, "month": 2592000}

    @commands.command(pass_context=True)
    @commands.has_any_role('Admin', 'Moderators', 'Global Operators')
    async def welcomereset(self, ctx):
        """Resets the newmsgdelete json file so that newly added welcome messages aren't removed."""
        if "296453860246159360" not in ctx.message.channel.id:
            return
        welcomemsg = await self.bot.say("newmsgdelete data file reset. Any messages above this one will not be automatically deleted. This message will be automatically deleted in 20 seconds.")
        dataIO.save_json(f, [])
        await asyncio.sleep(20)
        await self.bot.delete_message(welcomemsg)

    async def check_messages(self):
        while self is self.bot.get_cog("NewMsgDelete"):
            to_remove = []
            for msgdata in self.messagedata:
                if msgdata["FUTURE"] <= int(time.time()):
                    try:
                        #print("Channel: "+msgdata["channel"])
                        #print("Message ID:"+msgdata["messageid"])
                        #print("Future Time: "+str(msgdata["FUTURE"])
                        #await self.bot.delete_message(self.bot.get_message(self.bot.get_channel(msgdata["channel"]), msgdata["messageid"]))
                        chan = self.bot.get_channel(msgdata["channel"])
                        #print(chan.name)
                        message = await self.bot.get_message(chan, msgdata["messageid"])
                        #print(message.id)
                        await self.bot.delete_message(message)
                    except (discord.errors.Forbidden, discord.errors.NotFound):
                        to_remove.append(msgdata)
                    except discord.errors.HTTPException:
                        pass
                    else:
                        to_remove.append(msgdata)
            for msgdata in to_remove:
                self.messagedata.remove(msgdata)
            if to_remove:
                dataIO.save_json("data/newmsgdelete/newmsgdelete.json", self.messagedata)
            await asyncio.sleep(5) # try 30 to start with - at 3 hours this doesn't need to be super accurate
    
    async def onmessage(self, message):
        # triggers when a message is posted
        # add a check to see if the message is in a delete channel
        #
        # need to get the message data first
        if message.channel.id in monitor_channels:
            # log the message so that check_messages can monitor it
            #print(message.channel)
            self.messagedata.append({"channel" : message.channel.id, "messageid" : message.id, "FUTURE" : int(time.time()+delete_time)})
            dataIO.save_json("data/newmsgdelete/newmsgdelete.json", self.messagedata)
            #print("messageid " + message.channel.id + " added to data file")
            print("message " + message.id + " added for auto deletion in " + str(delete_time) + " at " + str(int(time.time())))

def check_folders():
    if not os.path.exists("data/newmsgdelete"):
        print("Creating newmsgdelete folder...")
        os.makedirs("data/newmsgdelete")

def check_files():
    f = "data/newmsgdelete/newmsgdelete.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty newmsgdelete.json...")
        dataIO.save_json(f, [])

def setup(bot):
    #global logger
    check_folders()
    check_files()
    #logger = logging.getLogger("remindme")
    #if logger.level == 0: # Prevents the logger from being loaded again in case of module reload
    #    logger.setLevel(logging.INFO)
    #    handler = logging.FileHandler(filename='data/remindme/reminders.log', encoding='utf-8', mode='a')
    #    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
    #    logger.addHandler(handler)
    #n = MSGDeleteDelay(bot)
    n = NewMsgDelete(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.check_messages())
    bot.add_listener(n.onmessage, "on_message")
    bot.add_cog(n)
