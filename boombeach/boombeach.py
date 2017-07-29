import discord
import os, re
import asyncio
#import datetime
from datetime import datetime, timedelta
from discord.ext import commands
from discord.utils import find
from cogs.utils import checks
from copy import deepcopy
from cogs.utils.chat_formatting import *
from cogs.utils.dataIO import dataIO
from random import sample

planty_file = "data/boombeach/planty.json"
tfdata_file = "data/boombeach/tfdata.json"
approve_file = "data/boombeach/approve.json"
queue_file = "data/boombeach/queue.json"
msgdel = []

class BoomBeach:

    def __init__(self, bot):
        self.bot = bot
        self.queueduration = timedelta(days=2)
        self.queueping = "340269179737210890" # recruitmentqueue channel to ping in
        self.bbserver = "181243681951449088"
        self.queuechannel = "340269179737210890" # rq-testing channel temporarily
        self.rqobj = dataIO.load_json(queue_file)

    @commands.command(pass_context=True, no_pm=True)
    async def planty(self, ctx):
        """Displays a planty and logs it"""
        # {
        #     "started" : "Month 0Day, Year"
        #     "planties" : 0
        # }
        plantyimg = "http://i.imgur.com/SLqibkU.png"
        plantydata = dataIO.load_json(planty_file)
        plantydata["planties"] = plantydata["planties"] + 1
        await self.bot.say("**{}** {} occurred since I started keeping track on {}!\n{}".format(plantydata["planties"], 
                                                                     "Planty has" if plantydata["planties"] == 1 else "Planties have", 
                                                                     plantydata["started"], 
                                                                     plantyimg))
        dataIO.save_json(planty_file, plantydata)

    @commands.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def plantyreset(self, ctx):
        """Resets the planty data file"""
        curdate = datetime.datetime.now().strftime("%B %d, %Y")
        plantydefault = {"started" : curdate, "planties" : 0}
        print("Resetting planty.json...")
        dataIO.save_json(planty_file, plantydefault)
        await self.bot.say("Planty data file reset.")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions()
    async def alltf(self, ctx):
        if "181243681951449088" in ctx.message.server.id:
            server = ctx.message.author.server
            roleid = '256679833239552001' # All-TF-Chats id
            roles = server.roles
            role = discord.utils.get(roles, id=roleid)
            userroles = ctx.message.author.roles
            if role in userroles: # They have it, so remove it
                await self.bot.remove_roles(ctx.message.author, role)
            else: # They don't have it, so add it
                await self.bot.add_roles(ctx.message.author, role)
            await self.bot.delete_message(ctx.message)
    
    @commands.command(pass_context=True, no_pm=True)
    async def getchannelsback(self, ctx):
        """This command will cycle one of a user's current roles to get their rooms back. Rooms tied to roles sometimes disappear on iOS."""
        if "181243681951449088" in ctx.message.server.id: # BB server
            user = ctx.message.author
            roles = user.roles
            dontuse = ["Admin", "Moderators", "Guest-Mod", "SC Staff", "Global Operators", "Green", "@everyone", "everyone"]
            
            new_msg = deepcopy(ctx.message)
            new_msg.author = ctx.message.server.get_member('189169374060478464') # using myself for this command (Annihilator6000)
            
            command = None
            
            # ..addrole <rolename> [user]
            for r in roles:
                if r.name in dontuse:
                    continue
                else:
                    command = "addrole \"{}\" {}".format(r.name, user.mention)
                    print("getchannelsback used by {}, role used: {}".format(user.nick if user.nick else user.name, r.name))
                    break
                        
            if command is not None:
                new_msg.content = self.bot.settings.get_prefixes(new_msg.server)[0] + command
                await self.bot.process_commands(new_msg)
    
    '''
        new_msg = deepcopy(ctx.message)
        new_msg.author = user
        new_msg.content = self.bot.settings.get_prefixes(new_msg.server)[0] \
            + command
        await self.bot.process_commands(new_msg)
    '''
    
    @commands.command(pass_context=True, no_pm=True)
    async def reset(self, ctx):
        """Displays the time remaining until intel reset. The reset is a 30 minute window between 00:00 and 00:30 GMT for all TFs."""
        currenttime = datetime.utcnow()
        until = {
            "Sun" : 7,
            "Mon" : 6,
            "Tue" : 5,
            "Wed" : 4,
            "Thu" : 3,
            "Fri" : 2,
            "Sat" : 1
        }
        td = timedelta(days=until[currenttime.ctime().split()[0]])
        tdextra = timedelta(minutes=15)
        nextreset = currenttime + td
        datestring = "%m/%d/%Y"
        futurestring = "{}/{}/{}".format(nextreset.month, nextreset.day, nextreset.year)
        futuredate = datetime.strptime(futurestring, datestring)
        futureobj = futuredate - currenttime
        tribesobj = futureobj + timedelta(days=1)
        tribesstart = datetime.fromtimestamp(1499644800) # July 10th 00:00 UTC
        calctribes = futuredate - tribesstart
        if (int(calctribes.days) / 7) % 2 is not 0:
            tribesobj = tribesobj + timedelta(days=7) # tribes reset every 2 weeks, if it the current datettime is on week 1 add a week
        futureobj = futureobj + tdextra

        d = divmod(futureobj.seconds, 86400)
        h = divmod(d[1], 3600)
        m = divmod(h[1], 60)
        
        td = divmod(tribesobj.seconds, 86400)
        th = divmod(td[1], 3600)
        tm = divmod(th[1], 60)
        
        await self.bot.say("Intel reset is in {} days {} hours {} minutes  +/- 15 minutes\n\n**Note:** Intel reset times are different for every TF, but they **all** occur between 00:00 GMT and 00:30 GMT on Sundays. The time above is standardized to 00:15 GMT, and is why +/- 15 minutes is shown.\n\nTribes reset is in {} days {} hours {} minutes.".format(futureobj.days, h[0], m[0], tribesobj.days, th[0], tm[0]))
    '''
    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions()
    async def shopkeeper(self, ctx, skrole):
        """Sets a shopkeeper role, to notify shopkeepers of purchases."""
        # temp return
        return
    '''
    @commands.group(pass_context=True, no_pm=True)
    async def rqueue(self, ctx):
        """Recruitment queue commands"""
        if ctx.invoked_subcommand is None:
            #await send_cmd_help(ctx)
            #print("queue function")
            if self.bbserver != ctx.message.server.id:
                return
            if self.queuechannel != ctx.message.channel.id: # recruitmentqueue channel
                return
            # queue needs subcommands: add, remove, reset (maybe?), and it also needs a loop to handle pinging people to post/queue cleanup
            # maybe after people get pinged for their post have an acknowledgement answer for them to use. If they ack, then remove their ping/comments after post time
            
            queuemessage = "The following `{0}rqueue` subcommands are available:\n\n```\nadd       - adds the specified TF to the queue\nremove    - removes the specified TF from the queue\nlisttfs   - lists valid TFs\nviolation - adds a violation to the specified TF\npost      - posts the current queue\nrules     - posts the recruitment queue rules\n```\n\nThis message and your `{0}rqueue` message will be deleted after 60 seconds.".format(ctx.prefix)
            #chan = '260933604706615296' #bot-testing channel
            #chan = '232939832849072130' #recruitmentqueue channel
            #sentmessage = await self.bot.send_message(chan, queuemessage)
            sentmessage = await self.bot.send_message(self.bot.get_channel(self.queuechannel), queuemessage)
            await asyncio.sleep(60)
            msgdel.append(ctx.message)
            msgdel.append(sentmessage)
            await self._delnewmembermsgs()
            
            # trichon council room for @here ping - 206092939112349697
            #
            # queue queue format: (this will be in "queue" : {})
            # "1" : {
            #     "position" : 1
            #     "TF" : "Bootcamp"
            #     "addedby" : "01234567890123"
            #     "ack" : True/False
            #     "ackpost" : null/"1234567890123"
            #     "added" : utc now timestamp
            #     "posttime" : timestamp of 00:00 of the day allowed to post - earliest posting time
            #     "pingtime" : timestamp that's posttime - 4 hours for the purpose of pinging members of the TF of the upcoming recruitment post
            # }
    
    @rqueue.command(no_pm=True, pass_context=True, name="add")
    async def queue_add(self, ctx, *, tf):
        """Adds a TF to the next available slot in the recruitment queue."""
        #if "181243681951449088" not in ctx.message.server.id:
        #    return
        
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id: # recruitmentqueue channel
            return
        
        msgdel.append(ctx.message)
        tflist = ", ".join(self.rqobj["TFs"].keys())
        if tf is None:
            #tflist = ", ".join(qf["TFs"].keys())
            addmessage = await self.bot.say("You didn't specify a TF to add. Please specify your TF from the list and use `{}queue add <TF>`: \n```\n{}\n```".format(tflist, ctx.prefix))
            await asyncio.sleep(30)
            msgdel.append(addmessage)
            await self._delnewmembermsgs()
        else:
            if tf.lower() in tflist.lower():
                # check to see if the tf is already on the queue
                if self.rqobj["queue"] is not None:
                    for entry in self.rqobj["queue"]:
                        if tf.lower() in entry["TF"]:
                            addmessage = await self.bot.say("{} is already in the queue and can not be added more than once. Please wait until {} is off the queue and try again.".format(tf, tf))
                            await asyncio.sleep(30)
                            msgdel.append(addmessage)
                            await self._delnewmembermsgs()
                admin = False
                adminroles = ["Moderators", "Global Operators"]
                userroles = ", ".join(r.name for r in ctx.message.author.roles)
                for ar in adminroles:
                    if ar in userroles:
                        admin = True
                if admin is True or tf.lower() in userroles.lower():
                    position = len(self.rqobj["queue"]) + 1
                    self.rqobj["queue"][str(position)]["position"] = position
                    self.rqobj["queue"][str(position)]["TF"] = tf
                    self.rqobj["queue"][str(position)]["addedby"] = ctx.message.author.id
                    self.rqobj["queue"][str(position)]["ack"] = False
                    self.rqobj["queue"][str(position)]["ackpost"] = None
                    added = datetime.utcnow()
                    self.rqobj["queue"][str(position)]["added"] = added

                    if position is 1:
                        # starting a new queue, so set the queue start time/date
                        gettomorrow = added + timedelta(days=1)
                        tomorrowutc = datetime.datetime(gettomorrow.year, gettomorrow.month, gettomorrow.day)
                        self.rqobj["settings"]["queuebegin"] = tomorrowutc 
                        self.rqobj["queue"][str(position)]["posttime"] = tomorrowutc
                        self.rqobj["queue"][str(position)]["pingtime"] = tomorrowutc - timedelta(hours=4) # ping 4 hours before post is to go up
                    else:
                        getpostday = self.rqobj["queue"][str(position - 1)]["posttime"] + timedelta(days=2)
                        postdayutc = datetime.datetime(getpostday.year, getpostday.month, getpostday.day)
                        self.rqobj["queue"][str(position)]["posttime"] = postdayutc
                        self.rqobj["queue"][str(position)]["pingtime"] = postdayutc - timedelta(hours=4) # ping 4 hours before post is to go up
                    dataIO.save_json(queue_file, self.rqobj)
                    await self._queue_post()
                    addedmsg = await self.bot.say("{} has been added to the queue.".format(tf))
                    await asyncio.sleep(30)
                    msgdel.append(addedmsg)
                    await self._delnewmembermsgs()
                else:
                    norole = await self.bot.say("You can't add an entry for a TF that you're not a member of. If you need assistance with this please contact a GO.")
                    await asyncio.sleep(30)
                    msgdel.append(norole)
                    await self._delnewmembermsgs()
            else:
                notvalid = self.bot.say("That's not a valid TF value. Please see the list using `{}queue listtfs`. If there is an issue with the list please contact Annihilator6000 (`@Annihilator6000#2526`).".format(ctx.prefix))
                await asyncio.sleep(30)
                msgdel.append(notvalid)
                await self._delnewmembermsgs()
    
    @rqueue.command(no_pm=True, pass_context=True, name="remove")
    async def queue_remove(self, ctx, *, tf):
        """Removes a TF from their slot in the recruitment queue."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id: # recruitmentqueue channel
            return
        msgdel.append(ctx.message)
        admin = False
        adminroles = ["Moderators", "Global Operators"]
        userroles = ", ".join(r.name for r in ctx.message.author.roles)
        for ar in adminroles:
            if ar in userroles:
                admin = True
        if admin is False and tf.lower() not in userroles.lower():
            errormsg = await self.bot.say("You're not allowed to remove a TF that you don't have roles for. Please contact a GO if you need assistance with this.")
            asyncio.sleep(30)
            msgdel.append(errormsg)
            await self._delnewmembermsgs()
        tflist = ", ".join(self.rqobj["TFs"].keys())
        if tf.lower() not in tflist.lower():
            errormsg = await self.bot.say("That TF isn't in my list. Please check `{}queue listtfs` for valid names and try again. If this message is in error please contact Annihilator6000 (`@Annihilator6000#2526`)".format(ctx.prefix))
            asyncio.sleep(30)
            msgdel.append(errormsg)
            await self._delnewmembermsgs()
        # self.rqobj["queue"] {
        # "1" : {
        #     "position" : 1
        #     "TF" : "Bootcamp"
        #     "addedby" : "01234567890123"
        #     "ack" : True/False
        #     "ackpost" : null/"1234567890123"
        #     "added" : utc now timestamp
        #     "posttime" : timestamp of 00:00 of the day allowed to post - earliest posting time
        #     "pingtime" : timestamp that's posttime - 4 hours for the purpose of pinging members of the TF of the upcoming recruitment post
        
        removednumber = None
        savedtimestamp = None # don't know if I'll need this yet
        for key in self.rqobj["queue"]:
            if tf.lower() == self.rqobj["queue"][key]["TF"].lower():
                removednumber = self.rqobj["queue"][key]["position"]
                savedtimestamp = self.rqobj["queue"][key]["added"]
                break
        if removednumber is None:
            removemsg = await self.bot.say("The specified TF wasn't found in the queue, or there might have been an error.")
            await asyncio.sleep(30)
            msgdel.append(removemsg)
            await self._delnewmembermsgs()
        else:
            count = removednumber
            while count < len(self.rqobj["queue"]):
                curposttime = self.rqobj["queue"][str(count)]["posttime"]
                curpingtime = self.rqobj["queue"][str(count)]["pingtime"]
                self.rqobj["queue"][str(count)] = self.rqobj["queue"][str(count+1)]
                self.rqobj["queue"][str(count)]["position"] = count
                # preserve original post time of previos TF
                self.rqobj["queue"][str(count)]["posttime"] = curposttime
                self.rqobj["queue"][str(count)]["pingtime"] = curpingtime
                count += 1
            del self.rqobj["queue"][str(len(self.rqobj["queue"]))]
            dataIO.save_json(queue_file, self.rqobj)
            await self._queue_post() # update the queue on discord
            removemsg = await self.bot.say("{} has been removed from the queue. Have a nice day.".format(tf))
            await asyncio.sleep(30)
            msgdel.append(removemsg)
            await self._delnewmembermsgs()
        
    @rqueue.command(no_pm=True, pass_context=True, name="listtfs")
    async def queue_listtfs(self, ctx):
        """Displays a list of valid TFs to add to the queue."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id: # recruitmentqueue channel
            return
        msgdel.append(ctx.message)
        tflist = ", ".join(sorted(list(self.rqobj["TFs"])))

        listmessage = await self.bot.say("The following TFs/TF families can be added to the queue:\n\n```\n{}\n```\n\nIf there is an issue with the list please contact Annihilator6000 (`@Annihilator6000#2526`).".format(tflist))
        await asyncio.sleep(60)
        msgdel.append(listmessage)
        await self._delnewmembermsgs()
    
    @rqueue.command(no_pm=True, pass_context=True, name="move")
    async def queue_move(self, ctx, *, direction:str=None, tf):
        """Moves a TF up or down the queue one position at a time. Syntax: queue move down/up TF"""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id: # recruitmentqueue channel
            return
        msgdel.append(ctx.message)
        direction = direction.lower()
        admin = False
        adminroles = ["Moderators", "Global Operators"]
        userroles = ", ".join(r.name for r in ctx.message.author.roles)
        for ar in adminroles:
            if ar in userroles:
                admin = True
        # check TF against valid TFs
        tflist = ", ".join(self.rqobj["TFs"].keys())
        if tf.lower() not in tflist.lower():
            notifymsg = await self.bot.say("That is not a valid TF. Please select one from `{}queue listtfs` and try again. If you require assistance please contact a GO.".format(ctx.prefix))
            asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs()
            return
        if admin is False and tf not in userroles:
            notifymsg = await self.bot.say("You don't have a role for {}. You are only able to move your own TF. If you require assistance please contact a GO.".format(tf))
            asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs()
            return
        if admin is False and direction.lower() == "up":
            notifymsg = await self.bot.say("You are not allowed to move your TF up the queue. You may only move it down. If you require assistance please contact a GO.")
            asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs()
            return
        if direction.lower() not in ["up", "down"]:
            notifymsg = await self.bot.say("`direction` can only be `up` or `down`. Only GOs can use `up`. Please try again.".format(tf))
            asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs()
            return
        # find the TF
        currentposition = None
        for key in self.rqobj["queue"]:
            if tf.lower() == tflist.lower():
                currentposition = self.rqobj["queue"][key]["position"]
                break
        # check if currentposition is still None. If so, then a match was not found in the queue. Warn user.
        if currentposition is None:
            notifymsg = await self.bot.say("{} not found in the queue. If this is an error please contact Annihilator6000 (`@Annihilator6000#2526`)".format(tf))
            asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs()
            return
        # check if it's the first or last element and being moved the wrong way - dict error will ensue
        if (currentposition == 0 and direction == "up") or (currentposition == len(self.rqobj["queue"]) and direction == "down"):
            notifymsg = await self.bot.say("I can't move {} {}, because they are currently at the {} of the queue.".format(tf, direction, "begining" if direction == "up" else "end"))
            asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs()
            return

        newpos = None
        if direction == "up":
            newpos = currentposition - 1
        else:
            newpos = currentposition + 1
        
        tempdata = self.rqobj["queue"][str(newpos)]
        newposposttime = self.rqobj["queue"][str(newpos)]["posttime"]
        newpospingtime = self.rqobj["queue"][str(newpos)]["pingtime"]
        curpostposttime = self.rqobj["queue"][str(currentposition)]["posttime"]
        curpostpingtime = self.rqobj["queue"][str(currentposition)]["pingtime"]
        self.rqobj["queue"][str(newpos)] = self.rqobj["queue"][str(currentposition)] # 3 to 2
        self.rqobj["queue"][str(newpos)]["position"] = newpos
        # newposition needs currentposition's post/ping times
        self.rqobj["queue"][str(newpos)]["posttime"] = curpostposttime
        self.rqobj["queue"][str(newpos)]["pingtime"] = curpostpingtime
        self.rqobj["queue"][str(currentposition)] = tempdata # temp to 3
        self.rqobj["queue"][str(currentposition)]["position"] = currentposition
        # currentposition needs newposition's post/ping times
        self.rqobj["queue"][str(currentposition)]["posttime"] = newposposttime
        self.rqobj["queue"][str(currentposition)]["pingtime"] = newpospingtime
        dataIO.save_json(queue_file, self.rqobj)
        await self._queue_post() # update Discord post
        notifymessage = await self.bot.say("{} has been successfully moved 1 position {} the queue.".format(tf, direction))
        asyncio.sleep(30)
        msgdel.append(notifymessage)
        await self._delnewmembermsgs()
    '''
    @queue.command(no_pm=True, pass_context=True, name="ack")
    async def queue_ack(self, ctx):
        """Acknowledges the reminder ping"""
        # The queue ack concept might get tossed
        # need to check the roles of the member using this to see if it matches up with the TF that's next
        return
    '''
    @rqueue.command(no_pm=True, pass_context=True, name="violation")
    async def queue_violation(self, ctx, *, tf, reason):
        """Adds a queue violation. If the TF has a space in the name it must be enclosed in quotes."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id: # recruitmentqueue channel
            return
        msgdel.append(ctx.message)
        # check tf here against list...
        # self.rqobj["violations"]
        # in violations it will have the TF name and time added (as a unix time string)
        #
        # If you violate the rules, 
        # your TF cannot be in the queue for 1 month (1st time), 
        # 3 months (2nd time), 
        # indefinite suspension/deverification vote (3rd time)
        #
        # add 1 month/3 months to the first/second vios and add that as a unix timestamp to self.rqobj["violations"][tf]["time"] and increment their violation count
        #
        # "Whisky" : {
        #    "count" : 1,
        #    "time" : null,
        #    "indefinate" : false
        #    "reason" : null
        # }
        
        admin = False
        adminroles = ["Moderators", "Global Operators"]
        userroles = ", ".join(r.name for r in ctx.message.author.roles)
        for ar in adminroles:
            if ar in userroles:
                admin = True
        if admin is False:
            notifymsg = await self.bot.say("This is a GO command. If someone is in violation of the rules please contact a GO.")
            asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs()
            return
        tflist = ", ".join(self.rqobj["TFs"].keys())
        if tf.lower() not in tflist.lower():
            # might be able to use proper case, or whatever it's called
            notifymsg = await self.bot.say("That is not a valid TF. Please select one from `{}queue listtfs` and try again. If you require assistance please contact a GO.".format(ctx.prefix))
            asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs()
            return
        if tf.lower() in tflist.lower(): # probably not going to work.
            if self.rqobj["violations"][tf]["count"] == 3:
                # already at the max
                notifymsg = await self.bot.say("{} already has 3 queue violations, and is indefinately suspended from the queue.".format(tf))
                asyncio.sleep(30)
                msgdel.append(notifymsg)
                await self._delnewmembermsgs()
                return
            self.rqobj["violations"][tf]["count"] += 1
            timeout = datetime.utcnow()
            #timeoutfuture = None
            if self.rqobj["violations"][tf]["count"] == 2:
                timeout += timedelta(days=90)
            if self.rqobj["violations"][tf]["count"] == 3:
                #indefinate
                timeout = datetime.max()
                self.rqobj["violations"][tf]["indefinate"] = True
            self.rqobj["violations"][tf]["time"] = timeout
            self.rqobj["violations"][tf]["reason"] = reason
        else:
            # TF not in the vio list, add them as a first vio
            self.rqobj["violations"][tf]["count"] = 1
            self.rqobj["violations"][tf]["time"] = datetime.utcnow() + timedelta(days=30)
            self.rqobj["violations"][tf]["indefinate"] = False
            self.rqobj["violations"][tf]["reason"] = reason
        
        violationtext = { 1 : "for 30 days", 2 : "for 90 days", 3 : "indefinately"}
        viomessage = self.bot.say("{}'s violation has been added with reason \"{}\" and will not be able to request {}.".format(tf, reason, violationtext[self.rqobj["violations"][tf]["count"]]))
        asyncio.sleep(30)
        msgdel.append(viomessage)
        await self._delnewmembermsgs()
        
    @rqueue.command(no_pm=True, pass_context=True, name="post")
    async def queue_post(self, ctx):
        """Posts or updates the current queue. Handy for if it accidentally gets deleted."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id: # recruitmentqueue channel
            return
        self._queue_post()
        await self.bot.delete_message(ctx.message)
    
    @rqueue.command(no_pm=True, pass_context=True, name="rules")
    async def queue_rules(self, ctx):
        """Posts the recruitment queue rules. Handy for if it accidentally gets deleted."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id: # recruitmentqueue channel
            return
        
        #If you want to recruit in redditbb, please post here. 
        #
        #***RULES***
        #```md
        #1. Post on time 
        #2. If your TF is full, take yourself off the queue. 
        #3. Include The Recruitment Form Link: 
        #```
        #<https://docs.google.com/forms/d/e/1FAIpQLScVYQtm-sINS6TnBewiGS0ac9jOL0e2cZT3TFtJKd71aXC1aw/viewform?c=0&w=1>
        #
        #***VIOLATIONS***
        #```
        #If you violate the rules, 
        #your TF cannot be in the queue for 1 month (1st time), 
        #3 months (2nd time), 
        #indefinite suspension/deverification vote (3rd time)
        #```
        
        chan = '260933604706615296' #bot-testing channel
        #chan = '232939832849072130' #recruitmentqueue channel
        rules = "If you want to recruit in redditbb, please post here.\n\n***RULES***\n```md\n1. Post on time\n2. If your TF is full, take yourself off the queue.\n3. Include The Recruitment Form Link:\n```\n<https://docs.google.com/forms/d/e/1FAIpQLScVYQtm-sINS6TnBewiGS0ac9jOL0e2cZT3TFtJKd71aXC1aw/viewform?c=0&w=1>\n\n***VIOLATIONS***\n```\nIf you violate the rules:\nyour TF cannot be in the queue for 1 month (1st time),\n3 months (2nd time),\nindefinite suspension/deverification vote (3rd time)\n```"
        rulespost = await self.bot.send_message(chan, rules)
        self.rqobj["settings"]["rulespost"] = str(rulespost.id)
        await self.bot.delete_message(ctx.message)
    
    def queue_get(self):
        if len(self.rqobj["queue"]) < 1:
            return "Empty"
        else:
            # timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
            queueobj = []
            count = 1
            length = len(self.rqobj["queue"])
            if length == 0:
                return ""
            while count <= length:
                tf = self.rqobj["queue"][str(count)]["TF"]
                if "Bootcamp" in tf or "Smoke" in tf:
                    tf = "BC/Smoke"
                tf = tf + ":"
                posttime = datetime.utcfromtimestamp(self.rqobj["queue"][str(count)]["posttime"])
                postend += timedelta(days=1) # end day is the day after
                queuestring = "{:<9} {}-{}".format(tf, posttime.strftime("%b %d"), postend.strftime("%b %d"))
                queueobj.append(queuestring)
                count += 1
            return "\n".join(queueobj)
    
    async def _queue_post(self):
        # posts or updates the current queue
        queuedata = self.queue_get()
        if self.rqobj["settings"]["violations"] is not None:
            queuevio = self.queue_violatation() # get vio data from data file and add it here
        else:
            queuevio = ""
        queuepost = "__Recruitment Queue__\nFirst date is the changeover, when the TF's post can be swapped in. Earliest posting time is 00:00 UTC on that date. <https://time.is/UTC>\n" + queuevio + "\n```md\nCurrent Queue\n=============\n\n" + queuedata + "\n```"
        chan = '260933604706615296' #bot-testing channel
        #chan = '232939832849072130' #recruitmentqueue channel
        if self.rqobj["settings"]["queuepost"] is not None:
            # have the bot edit the post instead of post a new one
            currentmsg = await self.bot.get_message(self.bot.get_channel(chan), self.rqobj["settings"]["queuepost"])
            await self.bot.edit_message(currentmsg, queuepost)
        else:
            # if there isn't a post (deleted, first run, etc) then make a new one
            newqueue = await self.bot.send_message(chan, queuepost)
            self.rqobj["settings"]["queuepost"] = str(newqueue.id)
        dataIO.save_json(queue_file, self.rqobj)
    
    async def queue_violatation(self):
        # get queue violation data here and return it formatted

        #   violations
        #       "TF"
        #           "count" : #
        #           "time" : unixtime/null
        #           "indefinite" : True/False
        violist = None
        for tf in self.rqobj["violations"]:
            if self.rqobj["violations"][tf]["time"] is not None:
                # valid vio
                viodate = date.fromtimestamp(self.rqobj["violations"][tf]["time"])
                vio = "{} {} and can not be on the queue until {}".format(tf, self.rqobj["violations"][tf]["reason"], viodate.ctime().split()[1] + " " + viodate.ctime().split()[2])
                violist.append()
        if violist is not None:
            return "\n" + "\n".join(violist) + "\n"
        else:
            return ""
    
    async def queue_remove(self, tf):
        # internal function for the bot to remove a tf from the queue from the queue loop
        removednumber = None
        savedtimestamp = None # don't know if I'll need this yet
        tflist = ", ".join(self.rqobj["TFs"].keys())
        for key in self.rqobj["queue"]:
            if tf.lower() == tflist.lower():
                #match
                removednumber = self.rqobj["queue"][key]["position"]
                savedtimestamp = self.rqobj["queue"][key]["added"]
                break
        if removednumber is None:
            print("boombeach.py: There was an internal failure while attempting to remove {} from the queue".format(tf))
        else:
            # then "move" the other entries "up" the list
            count = removednumber
            while count <= len(self.rqobj["queue"]) and count > 1:
                curposttime = self.rqobj["queue"][str(count)]["posttime"]
                curpingtime = self.rqobj["queue"][str(count)]["pingtime"]
                self.rqobj["queue"][str(count)] = self.rqobj["queue"][str(count+1)]
                self.rqobj["queue"][str(count)]["posttime"] = curposttime
                self.rqobj["queue"][str(count)]["pingtime"] = curpingtime
                self.rqobj["queue"][str(count)]["position"] = count
                count += 1
            del self.rqobj["queue"][str(len(self.rqobj["queue"]))]
            dataIO.save_json(queue_file, self.rqobj)
            await self._queue_post() # update the queue on discord
    
    #async def _queue_ping(self):
    #    
    
    async def queue_loop(self):
        while self == self.bot.get_cog('BoomBeach'):
            # example data:
            # "1" : {
            #   "position" : 1,
            #   "TF" : "Bootcamp",
            #   "addedby" : "01234567890123",
            #   "ack" : false,
            #   "ackpost" : null,
            #   "added" : 1501065656 ### July 26, 2017, 10:40 am
            #   "posttime" : 1501113600 ### July 27, 2017, 12:00 am # allowed to post any time after this
            #   "pingtime" : 1501099200 ### July 26, 2017, 8:00 pm # ping at this time
            # }   
            # "2" : {
            #   "position" : 2,
            #   "TF" : "Trichon",
            #   "addedby" : "01234567890123",
            #   "ack" : false,
            #   "ackpost" : null, # None
            #   "added" : 1501124400 ### July 27, 2017, 3:00 am
            #   "posttime" : 1501286400 ### July 29, 2017, 12:00 am # Eastern time will be 8 pm
            #   "pingtime" : 1501272000 ### July 28, 2017, 8:00 pm # Eastern time will be 4 pm
            # }
            
            if len(self.rqobj["queue"]) > 0:
                now = datetime.utcnow()
                print("queue loop - @ {}, queue length: {}".format(now, len(self.rqobj["queue"])))
                # make sure there's something in the queue before trying to access stuff
                if now > self.rqobj["queue"]["1"]["posttime"] + self.queueduration:
                    # if it's been more than 2 days that the post has been able to be up then delete it, along with the ackpost (ping)
                    if self.rqobj["queue"]["1"]["ackpost"] is not None:
                        await self._delnewmembermsgs(self.rqobj["queue"]["1"]["ackpost"])
                    await self.queue_remove(self.rqobj["queue"]["1"]["TF"])
                if now < self.rqobj["queue"]["1"]["posttime"] and now > self.rqobj["queue"]["1"]["pingtime"] and self.rqobj["queue"]["1"]["ackpost"] is None:
                    # if it's before the time to post, after the time to ping, and a ping hasn't been sent...
                    pingpeople = self.rqobj["TFs"][self.rqobj["queue"]["1"]["TF"]]
                    if len(pingpeople) > 2:
                        # only get 2 choices from the possible members to ping if there's more than 2
                        pingpeople = sample(pingpeople, k=2)
                    pinglist = []
                    for pingperson in pingpeople:
                        pinglist.append("<@" + pingperson + ">")
                    pingmsg = await self.bot.send_message(self.bot.get_channel(self.queueping), "{} - **Reminder**, you will be able to put up your recruitment post for {} in just under 4 hours.".format(" ".join(pinglist), self.rqobj["queue"]["1"]["TF"]))
                    self.rqobj["queue"]["1"]["ackpost"] = pingmsg.id
                # check if #1 is past ping time and #2 is within their ping window
                if len(self.rqobj["queue"]) > 1:
                    if now < self.rqobj["queue"]["2"]["posttime"] and now > self.rqobj["queue"]["2"]["pingtime"] and self.rqobj["queue"]["2"]["ackpost"] is None:
                        pingpeople = self.rqobj["TFs"][self.rqobj["queue"]["2"]["TF"]]
                        if len(pingpeople) > 2:
                            # only get 2 choices from the possible members to ping if there's more than 2
                            pingpeople = sample(pingpeople, k=2)
                        pinglist = []
                        for pingperson in pingpeople:
                            pinglist.append("<@" + pingperson + ">")
                        pingmsg = await self.bot.send_message(self.bot.get_channel(self.queueping), "{} - **Reminder**, you will be able to put up your recruitment post for {} in just under 4 hours.".format(" ".join(pinglist), self.rqobj["queue"]["2"]["TF"]))
                        self.rqobj["queue"]["2"]["ackpost"] = pingmsg.id
            await asyncio.sleep(300)
    
    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role('Moderators', 'Global Operators', 'TFC Leaders', 'TFC Co-Leaders', 'Affiliate Leaders')
    async def addmember(self, ctx, user: discord.Member=None, tf: str=None, rank: str=None):
        """Automatically adds roles and renames members.
        
        Proper format is: ..addmember @user TF rank
        To get a list of valid TF values use: ..listtfs
        Rank* can be: member, officer, co / co-leader / coleader, leader
        
        If no arguments are given (user, tf, and rank) interactive mode is started.
        
        *you can only assign rank lower than the highest role you currently have
            i.e. If you're a coleader you can only assign the officer role
            Note: If you try to assign an equal or higher rank it will add a lower rank to the member and notify leadership or GOs that it needs to be changed."""
        
        if "181243681951449088" not in ctx.message.server.id: # BB server
            return
        
        author = ctx.message.author
        server = ctx.message.author.server
        mocl = rank
        #msgdel = []
        msgdel.append(ctx.message)
        isvalid = None
        tfdata = dataIO.load_json(tfdata_file)
        approvedata = dataIO.load_json(approve_file)
        validmocl = ["member", "officer", "co", "coleader", "co-leader", "leader"]
        yescheck = ["yes", "Yes", "yes.", "Yes.", "Ye", "ye", "Y", "y"]
        tfcroles = {
                "member" : "TFC Members",
                "officer" : "TFC Officers",
                "coleader" : "TFC Co-Leaders",
                "leader" : "TFC Leaders"
            }
        interactive = False
        
        if user is None and tf is None and mocl is None:
            # interactive mode if ..addmember is used without any arguments
            
            # Start user selection
            interactive = True
            usermessage = await self.bot.say("Add member interactive mode started.\n\nEnter the member (as a mention: `@user#1234`)")
            msgdel.append(usermessage)
            isvalid = await self.bot.wait_for_message(timeout=30, author=ctx.message.author, channel=ctx.message.channel)
            if isvalid is not None:
                msgdel.append(isvalid)
                m = discord.utils.get(ctx.message.server.members, mention=isvalid.content)
                if m is None:
                    notvalidmember = await self.bot.say("Not a valid member. Cancelling addmember setup and cleaning up this mess.")
                    msgdel.append(notvalidmember)
                    await asyncio.sleep(5)
                    await self._delnewmembermsgs()
                    return
                else:
                    user = m
            else:
                timeoutmsg = await self.bot.say("You took too long to respond. Cancelling addmember setup and cleaning up this mess.")
                msgdel.append(timeoutmsg)
                await asyncio.sleep(5)
                await self._delnewmembermsgs()
                return
            
            # Start TF selection
            isvalid = None
            usermessage = await self.bot.say("Enter the TF that the member is in. Valid responses are:\n```\n{}\n```".format(", ".join(sorted(tfdata.keys()))))
            msgdel.append(usermessage)
            isvalid = await self.bot.wait_for_message(timeout=30, author=ctx.message.author, channel=ctx.message.channel)
            if isvalid is not None:
                msgdel.append(isvalid)
                if isvalid.content.lower() in tfdata.keys():
                    tf = isvalid.content.lower()
                else:
                    notvalidtf = await self.bot.say("That is not a valid TF choice. Please look at the valid choices using `{}listtfs` and try again. Cancelling addmember setup and cleaning up this mess.".format(ctx.prefix))
                    msgdel.append(notvalidtf)
                    await asyncio.sleep(5)
                    await self._delnewmembermsgs()
                    return
            else:
                timeoutmsg = await self.bot.say("You took too long to respond. Cancelling addmember setup and cleaning up this mess.")
                msgdel.append(timeoutmsg)
                await asyncio.sleep(5)
                await self._delnewmembermsgs()
                return
            
            # Start MOCL selection
            isvalid = None
            usermessage = await self.bot.say("Enter what rank the member is in the TF. Valid responses are:\n```\nmember\nofficer\nco / co-leader / coleader\nleader\n```")
            msgdel.append(usermessage)
            isvalid = await self.bot.wait_for_message(timeout=20, author=ctx.message.author, channel=ctx.message.channel)
            if isvalid is not None:
                msgdel.append(isvalid)
                newmemberrole = isvalid.content.lower()
                if newmemberrole in ["co", "co-leader"]:
                    newmemberrole = "coleader"
                if newmemberrole in validmocl:
                    mocl = newmemberrole
                else:
                    notvalidrank = await self.bot.say("That is not a valid rank. Please look at the valid rank choices in `{}listtfs` and try again. Cancelling addmember setup and cleaning up this mess.".format(ctx.prefix))
                    msgdel.append(notvalidrank)
                    await asyncio.sleep(5)
                    await self._delnewmembermsgs()
                    return
            else:
                timeoutmsg = await self.bot.say("You took too long to respond. Cancelling addmember setup and cleaning up this mess.")
                msgdel.append(timeoutmsg)
                await asyncio.sleep(5)
                await self._delnewmembermsgs()
                return
        
        if not interactive:
            if user not in ctx.message.server.members or user is None:
                notvalidmember = await self.bot.say("Not a valid member. Cancelling addmember setup and cleaning up this mess.")
                msgdel.append(notvalidmember)
                await asyncio.sleep(15)
                await self._delnewmembermsgs()
                return
            if tf is None:
                notvalidtf = await self.bot.say("I need a TF name from the list in `{0}listtfs` to be able to assign a TF and Roles. The syntax for this command is `{0}addmember @user#1234 taskforce rank`".format(ctx.prefix))
                msgdel.append(notvalidtf)
                await asyncio.sleep(15)
                await self._delnewmembermsgs()
                return
            tf = tf.lower()
            if tf not in tfdata.keys():
                notvalidtf = await self.bot.say("That is not a valid TF choice. Please look at the valid choices using `{}listtfs` and try again. Cancelling addmember setup and cleaning up this mess.".format(ctx.prefix))
                msgdel.append(notvalidtf)
                await asyncio.sleep(15)
                await self._delnewmembermsgs()
                return
            if mocl is None:
                notvalidrank = await self.bot.say("I need a rank from the list in `{0}listtfs` to be able to assign a TF and Roles. They syntax for this command is `{0}addmember @user#1234 taskforce rank`".format(ctx.prefix))
                msgdel.append(notvalidrank)
                await asyncio.sleep(15)
                await self._delnewmembermsgs()
                return
            mocl = mocl.lower()
            if mocl not in validmocl:
                notvalidrank = await self.bot.say("That is not a valid rank. Please look at the valid rank choices in `{}listtfs` and try again. Cancelling addmember setup and cleaning up this mess.".format(ctx.prefix))
                msgdel.append(notvalidrank)
                await asyncio.sleep(15)
                await self._delnewmembermsgs()
                return

        if mocl in ["co", "co-leader"]:
            # standardize co / co-leader / coleader to just "coleader" for subsequent use
            mocl = "coleader"
            
        # check to see what the highest role that the user can give - notify them if they can't assign a role 
        toprank = {"Moderators" : ["member", "coleader", "leader"],
                   "Global Operators" : ["member", "coleader", "leader"],
                   "TFC Leaders" : ["member", "coleader"],
                   "TFC Co-Leaders" : ["member"],
                   "Affiliate Leaders" : ["member"]}
        toprole = None
        
        uroles = ", ".join(r.name for r in ctx.message.author.roles)
        if "TFC Co-Leaders" in uroles:
            toprole = "TFC Co-Leaders"
        if "TFC Leaders" in uroles:
            toprole = "TFC Leaders"
        if "Moderators" in uroles or "Global Operators" in uroles:
            toprole = "Global Operators"
        if "Affiliate Leaders" in uroles:
            toprole = "Affiliate Leaders"

        limitrank = None
        
        skipnext = False
        if "TFC Co-Leaders" in toprole: # colead giving colead
            if "coleader" in mocl:
                skipnext = True
                # Cos can't give lead or Co roles
                # if the user choses yes, send a message to the Leadership channel (without a ping)
                rolewarning = await self.bot.say("You're not allowed to give a role that's the same or higher than your highest role. Would you like me to give **{}** the **TFC Officers** role for now, and notify the **Leaders/GOs** that it needs to be changed to **TFC Co-Leaders**?".format(user.nick if user.nick else user.name))
                msgdel.append(rolewarning)
                rwresponse = await self.bot.wait_for_message(timeout=20, author=ctx.message.author, channel=ctx.message.channel)
                if rwresponse is not None:
                    msgdel.append(rwresponse)
                    if rwresponse.content in yescheck:
                        # leadership channel id - 184858226691538945
                        limitrank = "officer"
                        casenum = len(approvedata) + 1
                        notifymessage = await self.bot.send_message(self.bot.get_channel('184858226691538945'), "{0} used my `{1}addmember` command on **{2}#{3}**, to try to give them the **TFC Co-Leaders** role. Because {0} is a Co-Leader, they can't assign Co-Leader to another member. Could a Leader or GO please look into assigning Co-Leader to **{2}#{3}**?\n\nI have assigned approval case **{4}** for this. An approver can use:\n\n`{1}approve {4} yes`\n\nto approve this case and assign the role automatically. This message will be automatically deleted after the case is approved or denied.".format(author.nick if author.nick else author.name, ctx.prefix, user.name, user.discriminator, casenum))
                        await self._add_approve(ctx.message.author, user, "TFC Co-Leaders", "TFC Officers", notifymessage)
                    else:
                        invalid = await self.bot.say("Ok then. I'll cancel addmember setup and clean up this mess.")
                        msgdel.append(invalid)
                        await asyncio.sleep(10)
                        await self._delnewmembermsgs()
                        return
                else:
                    #timeout or not "yes"
                    noans = await self.bot.say("You took too long. Cancelling new member setup and cleaning up this mess.")
                    msgdel.append(noans)
                    await asyncio.sleep(10)
                    await self._delnewmembermsgs()
                    return

        if "TFC Co-Leaders" in toprole and skipnext is False: # colead giving lead
            if "leader" in mocl:
                # Cos can't give lead
                # If the user chooses yes, send a message to the GO channel (without a ping)
                rolewarning = await self.bot.say("You're not allowed to give a role that's the same or higher than your highest role. Would you like me to give **{}** the **TFC Officers** role for now, and notify the **GOs** that it needs to be changed to **TFC Leaders**?".format(user.nick if user.nick else user.name))
                msgdel.append(rolewarning)
                rwresponse = await self.bot.wait_for_message(timeout=20, author=ctx.message.author, channel=ctx.message.channel)
                if rwresponse is not None:
                    msgdel.append(rwresponse)
                    if rwresponse.content in yescheck:
                        # OP channel id - 184858803412533249
                        limitrank = "officer"
                        casenum = len(approvedata) + 1
                        notifymessage = await self.bot.send_message(self.bot.get_channel('184858803412533249'), "{0} used my `{1}addmember` command on **{2}#{3}**, to try to give them the **TFC Leaders** role. Because {0} is a Co-Leader, they can't assign Leader to another member. Could a GO please look into assigning Leader to **{2}#{3}**?\n\nI have assigned approval case **{4}** for this. An approver can use:\n\n`{1}approve {4} yes`\n\nto approve this case and assign the role automatically. This message will be automatically deleted after the case is approved or denied.".format(author.nick if author.nick else author.name, ctx.prefix, user.name, user.discriminator, casenum))
                        await self._add_approve(ctx.message.author, user, "TFC Leaders", "TFC Officers", notifymessage)
                    else:
                        invalid = await self.bot.say("Ok then. I'll cancel addmember setup and clean up this mess.")
                        msgdel.append(invalid)
                        await asyncio.sleep(10)
                        await self._delnewmembermsgs()
                        return
                else:
                    #timeout or not "yes"
                    noans = await self.bot.say("You took too long. Cancelling addmember setup and cleaning up this mess.")
                    msgdel.append(noans)
                    await asyncio.sleep(10)
                    await self._delnewmembermsgs()
                    return
        
        if "TFC Leaders" in toprole and not "TFC Co-Leaders" in toprole: # lead giving lead
            if "leader" in mocl:
                # leads can't give lead role
                # if the user choses yes, send a message to the GO channel (without a ping)
                rolewarning = await self.bot.say("You're not allowed to give a role that's the same or higher than your highest role. Would you like me to give **{}** the **TFC Co-Leaders** role for now, and notify the **GOs** that it needs to be changed to **TFC Leaders**?".format(user.nick if user.nick else user.name))
                msgdel.append(rolewarning)
                rwresponse = await self.bot.wait_for_message(timeout=20, author=ctx.message.author, channel=ctx.message.channel)
                if rwresponse is not None:
                    msgdel.append(rwresponse)
                    if rwresponse.content in yescheck:
                        # OP channel id - 184858803412533249
                        limitrank = "coleader"
                        casenum = len(approvedata) + 1
                        notifymessage = await self.bot.send_message(self.bot.get_channel('184858803412533249'), "{0} used my `{1}addmember` command on **{2}#{3}**, to try to give them the **TFC Leaders** role. Because {0} is a Leader, they can't assign Leader to another member. Could a GO please look into assigning Leader to **{2}#{3}**?\n\nI have assigned approval case **{4}** for this. An approver can use:\n\n`{1}approve {4} yes`\n\nto approve this case and assign the role automatically. This message will be automatically deleted after the case is approved or denied.".format(author.nick if author.nick else author.name, ctx.prefix, user.name, user.discriminator, casenum))
                        await self._add_approve(ctx.message.author, user, "TFC Leaders", "TFC Co-Leaders", notifymessage)
                    else:
                        invalid = await self.bot.say("Ok then. I'll cancel addmember setup and clean up this mess.")
                        msgdel.append(invalid)
                        await asyncio.sleep(10)
                        await self._delnewmembermsgs()
                        return
                else:
                    #timeout or not "yes"
                    noans = await self.bot.say("You took too long. Cancelling new member setup and cleaning up this mess.")
                    msgdel.append(noans)
                    await asyncio.sleep(10)
                    await self._delnewmembermsgs()
                    return
        
        if "Affiliate Leaders" in toprole:
            if "leader" in mocl:
                rolewarning = await self.bot.say("You're not allowed to give a role that's the same or higher than your highest role. Would you like me to give **{}** the **Affiliate** role for now, and notify the **Leadership Channel** that it needs to be changed to **Affiliate Leaders**?".format(user.nick if user.nick else user.name))
                msgdel.append(rolewarning)
                rwresponse = await self.bot.wait_for_message(timeout=20, author=ctx.message.author, channel=ctx.message.channel)
                if rwresponse is not None:
                    msgdel.append(rwresponse)
                    if rwresponse.content in yescheck:
                        # Leadership channel id - 184858226691538945
                        casenum = len(approvedata) + 1
                        notifymessage = await self.bot.send_message(self.bot.get_channel('184858226691538945'), "{0} used my `{1}addmember` command on **{2}#{3}**, to try to give them the **Affiliate Leaders** role. Because {0} is an Affiliate Leader, they can't assign that role to another member. Could a Leader or GO please look into assigning Affiliate Leader to **{2}#{3}**?\n\nI have assigned approval case **{4}** for this. An approver can use:\n\n`{1}approve {4} yes`\n\nto approve this case and assign the role automatically. This message will be automatically deleted after the case is approved or denied.".format(author.nick if author.nick else author.name, ctx.prefix, user.name, user.discriminator, casenum))
                        await self._add_approve(ctx.message.author, user, "Affiliate Leaders", "Affiliate", notifymessage)
                    else:
                        invalid = await self.bot.say("Ok then. I'll cancel addmember setup and clean up this mess.")
                        msgdel.append(invalid)
                        await asyncio.sleep(10)
                        await self._delnewmembermsgs()
                        return
                else:
                    #timeout or not "yes"
                    noans = await self.bot.say("You took too long. Cancelling new member setup and cleaning up this mess.")
                    msgdel.append(noans)
                    await asyncio.sleep(10)
                    await self._delnewmembermsgs()
                    return

        rolestoadd = []
        if "Affiliate" not in tfdata[tf]["member"]: # This prevents Affiliates from getting TFC roles
            rolestoadd.append(tfcroles[limitrank if limitrank is not None else mocl])
        
        #
        # TODO: add a check for tfdata[tf]["leadroom"] (= True/False) (also, I don't know if this is actually needed... look into it more)
        #       Maybe change "leadroomroles" to "leadroles" also. That makes the leadroom/leadroles split more apparent. Will have to code for that.
        #
        if mocl in tfdata[tf]["leadroomroles"]:
            for val in tfdata[tf]["lead"]:
                rolestoadd.append(val)
        else:
            for val in tfdata[tf]["member"]:
                rolestoadd.append(val)
        roleobjs = []
        roles = server.roles
        rolesadded = []
        for singlerole in rolestoadd:
            roleobjs.append(discord.utils.get(roles, name=singlerole))
            rolesadded.append(singlerole)

        rolemessage = await self.bot.say("Adding roles to {}".format(user.nick if user.nick else user.name))
        msgdel.append(rolemessage)
        await self.bot.add_roles(user, *roleobjs) # needs the * for list unpacking
        
        previousnick = user.nick if user.nick else user.name
        renameto = user.nick if user.nick else user.name
        renametemp = ""
        if "|" in renameto:
            renamesplit = renameto.split('|')
            renameto = renamesplit[0]

        if "fire" in tf:
            tfdata[tf]["rename"] = tfdata[tf]["rename"].replace("replacewithfireemoji", "\U0001f525")
        renametemp = renameto + " | " + tfdata[tf]["rename"]
        
        " ".join(renametemp.split())
        renameto = renametemp
        print("Length of renameto for fire with emojis: {}".format(len(renameto)))
        if len(renameto) > 32:
            renamemessage = await self.bot.say("{}'s formatted nick will be too long with adding {} to the end of their nick. I'll leave their name unchanged for now.".format(user.nick if user.nick else user.name, tfdata[tf]["rename"]))
            msgdel.append(renamemessage)
        else:
            #rename here
            try:
                await self.bot.change_nickname(user, renameto)
                renmessage = await self.bot.say("{}'s nick has been changed to: {}".format(previousnick, renameto))
                msgdel.append(renmessage)
            except discord.Forbidden:
                renameerror = await self.bot.say("There was a problem changing {}'s nickname.".format(previousnick))
                msgdel.append(renameerror)
        
        rolestring = " ".join(rolesadded)
        logmsg = "My __addmember__ command was used. Here's the details:\n```\nUsed by: {}\n     ID: {}\nUsed on: {}\n     ID: {}\nNickname before: {}\nNickname after: {}\nRoles assigned: {}\n```".format(ctx.message.author.name + "#" + ctx.message.author.discriminator, ctx.message.author.id, user.name + "#" + user.discriminator, user.id, previousnick, renameto, rolesadded)
        mlchan = self.bot.get_channel('284786888957624320') # mod log channel
        await self.bot.send_message(mlchan, logmsg)
        
        notifychan = self.bot.get_channel(tfdata[tf]["notify"])
        await self.bot.send_message(notifychan, "{}, You now have roles for **{}** and your nickname has been changed accordingly. Here is your TF room.".format(user.mention, tfdata[tf]["rename"]))
        
        donemessage = await self.bot.say("I'm exhausted after all of that work. I'll clean up our mess after a 60 second break.")
        msgdel.append(donemessage)
        await asyncio.sleep(60)
        await self._delnewmembermsgs()

    @commands.command(no_pm=True, pass_context=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def approve(self, ctx, case, answer):
        """Approve or deny a pending leadership role that was created in addmember
        
        If answer is yes it will approve the role
        If answer is no it will deny the role"""
        if "181243681951449088" not in ctx.message.server.id: # BB server
            return

        try:
            case = int(case)
            if not answer:
                await send_cmd_help(ctx)
                return
        except:
            await send_cmd_help(ctx)
            return
        
        yesanswer = ["yes", "Yes", "yes.", "Yes.", "Ye", "ye", "Y", "y"]
        noanswer = ["no", "No", "no.", "No", "n", "N"]
        if answer not in yesanswer and answer not in noanswer:
            await self.bot.say("That's not a valid answer. It needs to be `yes` or `no`.")
            return
        
        approvedata = dataIO.load_json(approve_file)
        approvecase = None
        
        try:
            approvecase = approvedata[str(case)]
        except KeyError:
            await self.bot.say("That is not a valid case number.")
            return
        
        uroles = ", ".join(r.name for r in ctx.message.author.roles)
        toprole = None
        if "TFC Leaders" in uroles:
            toprole = "TFC Leaders"
        if "Moderators" in uroles or "Global Operators" in uroles:
            toprole = "Global Operators"
        
        if toprole is None or toprole in approvecase["role"]:
            await self.bot.say("You don't have a high enough role to approve the {} role.".format(approvecase["role"]))
            return
        
        authorname = ctx.message.author.nick if ctx.message.author.nick else ctx.message.author.name
        user = discord.utils.get(ctx.message.server.members, id=approvecase["member"])
        
        if answer in noanswer:
            # deny
            approvecase["approved"] = False
            await self.bot.say("{} role denied by {} and not added to {}".format(approvecase["role"], authorname, user.name + "#" + user.discriminator))
        
        if answer in yesanswer:
            # approve
            approvecase["approved"] = True
            roletoadd = discord.utils.get(ctx.message.author.server.roles, name=approvecase["role"])
            roletoremove = discord.utils.get(ctx.message.author.server.roles, name=approvecase["temprole"])
            await self.bot.add_roles(user, roletoadd)
            await asyncio.sleep(1)
            await self.bot.remove_roles(user, roletoremove)
            await self.bot.say("{} role approved by {} and added to {}".format(roletoadd.name, authorname, user.name + "#" + user.discriminator))
            
        approvecase["approver"] = ctx.message.author.nick
        approvecase["approverid"] = ctx.message.author.id
        approvedata[str(case)] = approvecase
        dataIO.save_json(approve_file, approvedata)
        notifymsg = await self.bot.get_message(self.bot.get_channel(approvecase["notifychan"]), approvecase["notifymsg"])
        await self._delnewmembermsgs([ctx.message, notifymsg])
        
    async def _add_approve(self, author, member, role, temprole, notifymsg):
        approvedata = dataIO.load_json(approve_file)
        case = len(approvedata) + 1
        casedata = {
            "approved"   : None,
            "approver"   : None,
            "approverid" : None,
            "author"     : author.name + "#" + author.discriminator,
            "case"       : case,
            "member"     : member.id,
            "membername" : member.nick if member.nick else member.name,
            "notifychan" : notifymsg.channel.id,
            "notifymsg"  : notifymsg.id,
            "role"       : role,
            "temprole"   : temprole
        }
        approvedata[str(case)] = casedata
        dataIO.save_json(approve_file, approvedata)
    
    @commands.command(no_pm=True, pass_context=True, name="listtfs")
    @checks.mod_or_permissions(manage_roles=True)
    async def addmember_listtfs(self, ctx):
        """Produces a list of valid TF names and ranks to use with the addmember command"""
        if "181243681951449088" not in ctx.message.server.id: # BB server
            return
            
        tfdata = dataIO.load_json(tfdata_file)
        toprank = {"Moderators" : ["member", "officer", "coleader", "leader"],
                   "Global Operators" : ["member", "officer", "coleader", "leader"],
                   "TFC Leaders" : ["member", "officer", "coleader"],
                   "TFC Co-Leaders" : ["member", "officer"],
                   "Affiliate Leaders" : ["member"]}
        toprole = None
        rankkeys = iter(toprank.keys())
        roles = ctx.message.author.roles
        
        uroles = ", ".join(r.name for r in ctx.message.author.roles)
        if "TFC Co-Leaders" in uroles:
            toprole = "TFC Co-Leaders"
        if "TFC Leaders" in uroles:
            toprole = "TFC Leaders"
        if "Moderators" in roles or "Global Operators" in uroles:
            toprole = "Global Operators"
        if "Affiliate Leaders" in uroles:
            toprole = "Affiliate Leaders"

        validmocl = ["member", "officer", "co", "coleader", "co-leader", "leader"]
        listmsg = await self.bot.say("Valid TF values to use in the `{}newmember` command:\n```\n{}\n```\n\nValid ranks for you to apply are:\n```\n{}\n```\nThis message and your `{}listtfs` command will be automatically deleted after 60 seconds.".format(ctx.prefix, ", ".join(sorted(tfdata.keys())), ", ".join(toprank[toprole]), ctx.prefix))
        await asyncio.sleep(60)
        await self.bot.delete_message(ctx.message)
        await self.bot.delete_message(listmsg)
    
    '''
    async def _delnewmembermsgs(self, msgs):
        if len(msgs) < 2:
            await self.bot.delete_message(msgs)
        if len(msgs) >= 2:
            await self.bot.delete_messages(msgs)
    '''
    
    async def _delnewmembermsgs(self):
        if len(msgdel) < 2:
            await self.bot.delete_message(msgdel)
        if len(msgdel) >= 2:
            await self.bot.delete_messages(msgdel)
        self.msgdel = [] #reset
    
    @commands.command(no_pm=True, pass_context=True)
    @checks.is_owner()
    async def resetme(self, ctx):
        """Resets my nick/roles on my test account"""
        me = ctx.message.server.get_member('264224570213531648')
        await self.bot.change_nickname(me, None)
        await self.bot.remove_roles(me, *me.roles)
    
def check_folders():
    if not os.path.exists("data/boombeach"):
        print("Creating boombeach folder...")
        os.makedirs("data/boombeach")

def check_files():
    if not dataIO.is_valid_json(planty_file):
        curdate = datetime.datetime.now().strftime("%B %d, %Y")
        plantydefault = {"started" : curdate, "planties" : 0}
        print("Creating empty planty.json...")
        dataIO.save_json(planty_file, plantydefault)

def setup(bot):
    check_folders()
    check_files()
    n = BoomBeach(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.queue_loop())
