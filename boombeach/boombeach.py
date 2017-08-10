import discord
import os, re
import asyncio
# import datetime
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
# msgdel = []


class BoomBeach:

    def __init__(self, bot):
        self.bot = bot
        self.queueduration = timedelta(days=2)
        # self.queueping = "340269179737210890"  # rq-testing channel to ping in
        self.queueping = "232939832849072130"  # recruitmentqueue channel to ping in
        self.bbserver = "181243681951449088"
        # self.queuechannel = "340269179737210890"  # rq-testing channel temporarily
        self.queuechannel = "232939832849072130"  # recruitmentqueue channel
        # self.opchannel = "340269179737210890"  # 184858803412533249 <- real OP channel, change after testing is complete
        self.opchannel = "184858803412533249"  # 184858803412533249 <- real OP channel, change after testing is complete
        self.modlogchannel = "284786888957624320"
        self.rqobj = dataIO.load_json(queue_file)
        self.testingmode = False
        self.testingcount = 0
        self.testingnow = None
        self.testinghours = 0

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
        plantydefault = {"started": curdate, "planties": 0}
        print("Resetting planty.json...")
        dataIO.save_json(planty_file, plantydefault)
        await self.bot.say("Planty data file reset.")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions()
    async def alltf(self, ctx):
        if "181243681951449088" in ctx.message.server.id:
            server = ctx.message.author.server
            roleid = '256679833239552001'  # All-TF-Chats id
            roles = server.roles
            role = discord.utils.get(roles, id=roleid)
            userroles = ctx.message.author.roles
            if role in userroles:  # They have it, so remove it
                await self.bot.remove_roles(ctx.message.author, role)
            else:  # They don't have it, so add it
                await self.bot.add_roles(ctx.message.author, role)
            await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, no_pm=True)
    async def getchannelsback(self, ctx):
        """This command will cycle one of a user's current roles to get their rooms back. Rooms tied to roles sometimes disappear on iOS."""
        if "181243681951449088" in ctx.message.server.id:  # BB server
            user = ctx.message.author
            roles = user.roles
            dontuse = ["Admin", "Moderators", "Guest-Mod", "SC Staff", "Global Operators", "Green", "@everyone", "everyone"]

            new_msg = deepcopy(ctx.message)
            new_msg.author = ctx.message.server.get_member('189169374060478464')  # using myself for this command (Annihilator6000)

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
            "Sun": 7,
            "Mon": 6,
            "Tue": 5,
            "Wed": 4,
            "Thu": 3,
            "Fri": 2,
            "Sat": 1
        }
        td = timedelta(days=until[currenttime.ctime().split()[0]])
        tdextra = timedelta(minutes=15)
        nextreset = currenttime + td
        datestring = "%m/%d/%Y"
        futurestring = "{}/{}/{}".format(nextreset.month, nextreset.day, nextreset.year)
        futuredate = datetime.strptime(futurestring, datestring)
        futureobj = futuredate - currenttime
        futureobj = futureobj + tdextra

        d = divmod(futureobj.seconds, 86400)
        h = divmod(d[1], 3600)
        m = divmod(h[1], 60)

        tribetime = datetime.utcnow()
        tribedate = datetime.utcfromtimestamp(1499644800)  # July 10th 00:00 UTC
        while tribedate < tribetime:
            tribedate += timedelta(days=14)
        tribedifference = tribedate - tribetime
        tribed = divmod(tribedifference.seconds, 86400)
        tribeh = divmod(tribed[1], 3600)
        tribem = divmod(tribeh[1], 60)
        await self.bot.say("Intel reset is in {} days {} hours {} minutes  +/- 15 minutes\n\n**Note:** Intel reset times are different for every TF, but they **all** occur between 00:00 GMT and 00:30 GMT on Sundays. The time above is standardized to 00:15 GMT, and is why +/- 15 minutes is shown.\n\nTribal boost reset is in {} days {} hours {} minutes.".format(futureobj.days, h[0], m[0], tribedifference.days, tribeh[0], tribem[0]))
    '''
    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions()
    async def shopkeeper(self, ctx, skrole):
        """Sets a shopkeeper role, to notify shopkeepers of purchases."""
        # temp return
        return
    '''
    @commands.group(pass_context=True, no_pm=True)
    async def rq(self, ctx):
        """Recruitment queue commands"""
        if ctx.invoked_subcommand is None:
            # await send_cmd_help(ctx)
            # print("queue function")
            if self.bbserver != ctx.message.server.id:
                return
            if self.queuechannel != ctx.message.channel.id: # recruitmentqueue channel
                return
            msgdel = []
            # queue needs subcommands: add, remove, reset (maybe?), and it also needs a loop to handle pinging people to post/queue cleanup
            # maybe after people get pinged for their post have an acknowledgement answer for them to use. If they ack, then remove their ping/comments after post time

            queuemessage = "The following `{0}rq` subcommands are available:\n```\nadd       - adds the specified TF to the queue\nmove      - moves the specified TF down or up the queue\nremove    - removes the specified TF from the queue\nlisttfs   - lists valid TFs\nviolation - adds a violation to the specified TF\npost      - posts the current queue\nrules     - posts the recruitment queue rules\n```\nThis message and your `{0}rq` message will be deleted after 60 seconds.".format(ctx.prefix)
            sentmessage = await self.bot.send_message(self.bot.get_channel(self.queuechannel), queuemessage)
            await asyncio.sleep(60)
            msgdel.append(ctx.message)
            msgdel.append(sentmessage)
            await self._delnewmembermsgs(msgdel)

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

    @rq.command(no_pm=True, pass_context=True, name="add")
    async def queue_add(self, ctx, *, tf):
        """Adds a TF to the next available slot in the recruitment queue."""
        # if "181243681951449088" not in ctx.message.server.id:
        #    return

        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id:  # recruitmentqueue channel
            return
        msgdel = []
        msgdel.append(ctx.message)
        tflist = ", ".join(self.rqobj["TFs"].keys())
        if tf is None:
            # tflist = ", ".join(qf["TFs"].keys())
            addmessage = await self.bot.say("You didn't specify a TF to add. Please specify your TF from the list and use `{}queue add <TF>`: \n```\n{}\n```".format(tflist, ctx.prefix))
            msgdel.append(addmessage)
            await asyncio.sleep(30)
            await self._delnewmembermsgs(msgdel)
        else:
            tf = tf.title()
            if tf.lower() == "bc/smoke":
                tf = "BC/Smoke"
            if tf.lower() in tflist.lower():
                # check to see if the tf is already on the queue
                if len(self.rqobj["queue"]) > 0:
                    for entry in self.rqobj["queue"]:
                        if tf.lower() in self.rqobj["queue"][entry]["TF"].lower(): #entry["TF"]:
                            addmessage = await self.bot.say("{} is already in the queue and can not be added more than once. Please wait until {} is off the queue and try again.".format(tf, tf))
                            msgdel.append(addmessage)
                            await asyncio.sleep(30)
                            await self._delnewmembermsgs(msgdel)
                            return
                violist = ", ".join(self.rqobj["violations"].keys())
                if tf.lower() in violist.lower():
                    if self.rqobj["violations"][tf]["time"] is not None:
                        if datetime.utcnow().timestamp() < self.rqobj["violations"][tf]["time"]:
                            addmessage = await self.bot.say("{} is unable to be added to the queue due to a current violation.".format(tf))
                            msgdel.append(addmessage)
                            await asyncio.sleep(30)
                            await self._delnewmembermsgs(msgdel)
                            return
                admin = False
                adminroles = ["Moderators", "Global Operators"]
                userroles = ", ".join(r.name for r in ctx.message.author.roles)
                for ar in adminroles:
                    if ar in userroles:
                        admin = True

                bcs = self.bcsmokecheck(ctx)

                if admin is True or (tf.lower() in userroles.lower()) or (bcs is True and tf.lower() == "bc/smoke"):
                    await self.backupqdata(ctx.message.author.nick, ctx.message.content, "queue")
                    position = len(self.rqobj["queue"]) + 1
                    self.rqobj["queue"][str(position)] = {}
                    self.rqobj["queue"][str(position)]["position"] = position
                    self.rqobj["queue"][str(position)]["TF"] = tf
                    self.rqobj["queue"][str(position)]["addedby"] = ctx.message.author.id
                    self.rqobj["queue"][str(position)]["ack"] = False
                    self.rqobj["queue"][str(position)]["ackpost"] = None
                    added = datetime.utcnow()
                    self.rqobj["queue"][str(position)]["added"] = added.timestamp()
                    '''
                    added = datetime.utcnow()
                    tempqobj = {
                        str(position) : {
                            "position" : position,
                            "TF" : tf,
                            "addedby" : ctx.message.author.id,
                            "ack" : False,
                            "ackpost" : None,
                            "added" : added.timestamp(),
                            "posttime" : None,
                            "pingtime" : None
                        }
                    }
                    '''

                    if position is 1:
                        # starting a new queue, so set the queue start time/date
                        gettomorrow = added + timedelta(days=1)
                        tomorrowutc = datetime(gettomorrow.year, gettomorrow.month, gettomorrow.day)
                        self.rqobj["settings"]["queuebegin"] = tomorrowutc.timestamp()
                        self.rqobj["queue"][str(position)]["posttime"] = tomorrowutc.timestamp()
                        # tempqobj[str(position)]["posttime"] = tomorrowutc.timestamp()
                        minusfourhours = tomorrowutc - timedelta(hours=4)
                        self.rqobj["queue"][str(position)]["pingtime"] = minusfourhours.timestamp() # ping 4 hours before post is to go up
                        # tempqobj[str(position)]["pingtime"] = minusfourhours.timestamp()
                    else:
                        getpostday = datetime.fromtimestamp(self.rqobj["queue"][str(position - 1)]["posttime"]) + timedelta(days=2)
                        postdayutc = datetime(getpostday.year, getpostday.month, getpostday.day)
                        self.rqobj["queue"][str(position)]["posttime"] = postdayutc.timestamp()
                        # tempqobj[str(position)]["posttime"] = tomorrowutc.timestamp()
                        minusfourhours = postdayutc - timedelta(hours=4)
                        self.rqobj["queue"][str(position)]["pingtime"] = minusfourhours.timestamp() # ping 4 hours before post is to go up
                        # tempqobj[str(position)]["pingtime"] = minusfourhours.timestamp()
                    # self.rqobj["queue"].append(tempqobj)
                    dataIO.save_json(queue_file, self.rqobj)
                    await self._queue_post()
                    addedmsg = await self.bot.say("{} has been added to the queue. \U0001f389".format(tf))
                    msgdel.append(addedmsg)
                    await asyncio.sleep(30)
                    await self._delnewmembermsgs(msgdel)
                else:
                    norole = await self.bot.say("You can't add an entry for a TF that you're not a member of. If you need assistance with this please contact a GO.")
                    msgdel.append(norole)
                    await asyncio.sleep(30)
                    await self._delnewmembermsgs(msgdel)
            else:
                notvalid = await self.bot.say("That's not a valid TF value. Please see the list using `{}queue listtfs`. If there is an issue with the list please contact Annihilator6000 (`@Annihilator6000#2526`).".format(ctx.prefix))
                msgdel.append(notvalid)
                await asyncio.sleep(30)
                await self._delnewmembermsgs(msgdel)

    @rq.command(no_pm=True, pass_context=True, name="remove")
    async def rq_remove(self, ctx, *, tf):
        """Removes a TF from their slot in the recruitment queue."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id:  # recruitmentqueue channel
            return
        msgdel = []
        msgdel.append(ctx.message)
        tf = tf.title()
        if tf.lower() == "bc/smoke":
            tf = "BC/Smoke"
        bcs = self.bcsmokecheck(ctx)
        admin = False
        adminroles = ["Moderators", "Global Operators"]
        userroles = ", ".join(r.name for r in ctx.message.author.roles)
        tflist = ", ".join(self.rqobj["TFs"].keys())
        if tf.lower() not in tflist.lower():
            errormsg = await self.bot.say("That TF isn't in my list. Please check `{}queue listtfs` for valid names and try again. If this message is in error please contact Annihilator6000 (`@Annihilator6000#2526`)".format(ctx.prefix))
            await asyncio.sleep(30)
            msgdel.append(errormsg)
            await self._delnewmembermsgs(msgdel)
            return
        for ar in adminroles:
            if ar in userroles:
                admin = True
        if admin is False and (tf.lower() not in userroles.lower()) and (bcs is True and tf.lower() != "bc/smoke"):
            errormsg = await self.bot.say("You're not allowed to remove a TF that you don't have roles for. Please contact a GO if you need assistance with this.")
            await asyncio.sleep(30)
            msgdel.append(errormsg)
            await self._delnewmembermsgs(msgdel)
            return

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

        # queue backup is performed in self.queue_remove
        check_remove = await self.queue_remove(tf, ctx.message.author.nick, ctx.message.content, False)
        if check_remove == False:
            removemsg = await self.bot.say("The specified TF wasn't found in the queue, or there might have been an error.")
            await asyncio.sleep(30)
            msgdel.append(removemsg)
            await self._delnewmembermsgs(msgdel)
        else:
            removemsg = await self.bot.say("{} has been removed from the queue. Have a nice day.".format(tf))
            await asyncio.sleep(30)
            msgdel.append(removemsg)
            await self._delnewmembermsgs(msgdel)

    def bcsmokecheck(self, c):
        # do a check for Bootcamp or Smoke roles on the user and return
        # true if they have either role
        bcsmokecheck = False
        userroles = ", ".join(r.name for r in c.message.author.roles)
        for bcs in ["Bootcamp", "Smoke"]:
            if bcs.lower() in userroles.lower():
                bcsmokecheck = True
                break
        return bcsmokecheck

    async def backupqdata(self, author, cmdcontent, whattobackup):
        # c is ctx - need ctx.message.author.nick and ctx.message.content from it
        if self.testingmode is True or self.queuechannel != "232939832849072130":
            return
        backupmsg = "The recruitment queue is being modified by `{}`.\nCommand: `{}`.\nCurrent date/time: {}.\nHere's a snapshot of it before the new data gets saved:".format(author, cmdcontent, datetime.utcnow())
        # backupmsg += "Queue:\n```\n{}\n```\nViolations:\n```\n{}\n```".format(self.rqobj["queue"], self.rqobj["violations"])
        if whattobackup.lower() == "queue" or whattobackup.lower() == "all":
            backupmsg += "\nQueue:\n```\n{}\n```".format(self.rqobj["queue"])
        if whattobackup.lower() == "violations" or whattobackup.lower() == "all":
            backupmsg += "\nViolations:\n```\n{}\n```".format(self.rqobj["violations"])
        await self.bot.send_message(self.bot.get_channel(self.modlogchannel), backupmsg)

    @rq.command(no_pm=True, pass_context=True, name="listtfs")
    async def queue_listtfs(self, ctx):
        """Displays a list of valid TFs to add to the queue."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id:  # recruitmentqueue channel
            return
        msgdel = []
        msgdel.append(ctx.message)
        tflist = ", ".join(sorted(list(self.rqobj["TFs"])))

        listmessage = await self.bot.say("The following TFs/TF families can be added to the queue:\n```\n{}\n```\nIf there is an issue with the list please contact Annihilator6000 (`@Annihilator6000#2526`).".format(tflist))
        await asyncio.sleep(60)
        msgdel.append(listmessage)
        await self._delnewmembermsgs(msgdel)

    @rq.command(no_pm=True, pass_context=True, name="move")
    async def queue_move(self, ctx, tf, direction):
        """Moves a TF up or down the queue one position at a time.

        Syntax: queue move TF down/up
        If there are spaces in the TF name it must be enclosed in quotes."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id:  # recruitmentqueue channel
            return
        msgdel = []
        msgdel.append(ctx.message)
        tf = tf.title()
        if tf.lower() == "bc/smoke":
            tf = "BC/Smoke"
        bcs = self.bcsmokecheck(ctx)
        if direction is None or direction is "":
            notifymsg = await self.bot.say("You must specify a direction. If you're not a GO you can only move *your* TF `down` the queue. Valid direction values: `up` or `down`.")
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return
        direction = direction.lower()
        directioncheck = ["up", "u", "down", "d"]
        if direction not in directioncheck:
            notifymsg = await self.bot.say("That is not a valid direction. Valid direction values are: `down` and `up`. Only GOs can use `up`.")
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return
        if direction == "u":
            direction = "up"
        if direction == "d":
            direction = "down"
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
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return
        if admin is False and tf not in userroles and (bcs == True and tf.lower() != "bc/smoke"):
            notifymsg = await self.bot.say("You don't have a role for {}. You are only able to move your own TF. If you require assistance please contact a GO.".format(tf))
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return
        if admin is False and direction.lower() == "up":
            notifymsg = await self.bot.say("You are not allowed to move your TF up the queue. You may only move it down. If you require assistance please contact a GO.")
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return
        if direction.lower() not in ["up", "down"]:
            notifymsg = await self.bot.say("`direction` can only be `up` or `down`. Only GOs can use `up`. Please try again.".format(tf))
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return
        # find the TF
        currentposition = None
        count = 1
        while count <= len(self.rqobj["queue"]):
            if tf.lower() == self.rqobj["queue"][str(count)]["TF"].lower():
                currentposition = self.rqobj["queue"][str(count)]["position"]
                # break
            count += 1
        # check if currentposition is still None. If so, then a match was not found in the queue. Warn user.
        if currentposition is None:
            notifymsg = await self.bot.say("{} not found in the queue. If this is an error please contact Annihilator6000 (`@Annihilator6000#2526`).".format(tf))
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return
        # check if it's the first or last element and being moved the wrong way - dict error will ensue
        if (currentposition == 1 and direction == "up") or (currentposition == len(self.rqobj["queue"]) and direction == "down"):
            notifymsg = await self.bot.say("I can't move {} {}, because they are currently at the {} of the queue.".format(tf, direction, "begining" if direction == "up" else "end"))
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return

        await self.backupqdata(ctx.message.author.nick, ctx.message.content, "queue")

        newpos = None
        if direction == "up":
            newpos = currentposition - 1
        else:
            newpos = currentposition + 1

        # check if #1 is moving down and is within 5 hours of posting
        # if they are then a GO needs to check and move them
        if currentposition == 1 and direction == "down" and admin is False and datetime.utcnow().timestamp() > (self.rqobj["queue"]["1"]["posttime"] - timedelta(hours=5).total_seconds()):
            notifymsg = await self.bot.say("{} is within 5 hours of posting. Because of this a GO needs to check that {} has enough time to get a post together. A notification is being sent to the GOs.".format(self.rqobj["queue"]["1"]["TF"], self.rqobj["queue"]["2"]["TF"]))
            await self.bot.send_message(self.bot.get_channel(self.opchannel), "{0} would like to move {1} down the queue in #recruitmentqueue. A GO needs to check that {2} has enough time to get a post together, and move {1}.".format(ctx.message.author.nick, self.rqobj["queue"]["1"]["TF"], self.rqobj["queue"]["2"]["TF"]))
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return

        if (currentposition == 1 and direction == "down") or (currentposition == 2 and direction == "up"):
            # add ping check removal here - self.rqobj["queue"]["1"]["ackpost"]
            self.rqobj["queue"]["1"]["ackpost"] = None

        newposdata = self.rqobj["queue"][str(newpos)]
        newposposttime = self.rqobj["queue"][str(newpos)]["posttime"]
        newpospingtime = self.rqobj["queue"][str(newpos)]["pingtime"]
        curposposttime = self.rqobj["queue"][str(currentposition)]["posttime"]
        curpospingtime = self.rqobj["queue"][str(currentposition)]["pingtime"]
        self.rqobj["queue"][str(newpos)] = self.rqobj["queue"][str(currentposition)]
        self.rqobj["queue"][str(newpos)]["position"] = newpos
        self.rqobj["queue"][str(newpos)]["posttime"] = newposposttime
        self.rqobj["queue"][str(newpos)]["pingtime"] = newpospingtime
        self.rqobj["queue"][str(currentposition)] = newposdata
        self.rqobj["queue"][str(currentposition)]["position"] = currentposition
        self.rqobj["queue"][str(currentposition)]["posttime"] = curposposttime
        self.rqobj["queue"][str(currentposition)]["pingtime"] = curpospingtime
        dataIO.save_json(queue_file, self.rqobj)
        await self._queue_post()  # update Discord post
        notifymessage = await self.bot.say("{} has been successfully moved 1 position {} the queue.".format(tf, direction))
        await asyncio.sleep(30)
        msgdel.append(notifymessage)
        await self._delnewmembermsgs(msgdel)
    '''
    @queue.command(no_pm=True, pass_context=True, name="ack")
    async def queue_ack(self, ctx):
        """Acknowledges the reminder ping"""
        # The queue ack concept might get tossed
        # need to check the roles of the member using this to see if it matches up with the TF that's next
        return
    '''
    @rq.command(no_pm=True, pass_context=True, name="violation")
    async def queue_violation(self, ctx, tf, *, reason: str):
        """Adds a queue violation. If the TF has a space in the name it must be enclosed in quotes."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id:  # recruitmentqueue channel
            return
        msgdel = []
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
        #    "indefinite" : false
        #    "reason" : null
        # }

        tf = tf.title()
        if tf.lower() == "bc/smoke":
            tf = "BC/Smoke"
        # bcs = self.bcsmokecheck(ctx)
        admin = False
        adminroles = ["Moderators", "Global Operators"]
        userroles = ", ".join(r.name for r in ctx.message.author.roles)
        for ar in adminroles:
            if ar in userroles:
                admin = True
        if admin is False:
            notifymsg = await self.bot.say("This is a GO command. If someone is in violation of the rules please contact a GO.")
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return
        tflist = ", ".join(self.rqobj["TFs"].keys())
        if tf.lower() not in tflist.lower():
            # might be able to use proper case, or whatever it's called
            notifymsg = await self.bot.say("That is not a valid TF. Please select one from `{}queue listtfs` and try again. If you require assistance please contact Annihilator6000 (`@Annihilator6000#2526`).".format(ctx.prefix))
            await asyncio.sleep(30)
            msgdel.append(notifymsg)
            await self._delnewmembermsgs(msgdel)
            return
        violist = ", ".join(self.rqobj["violations"])
        if tf.lower() in violist.lower():
            if self.rqobj["violations"][tf]["count"] == 3:
                # already at the max
                notifymsg = await self.bot.say("{} already has 3 queue violations, and is indefinitely suspended from the queue.".format(tf))
                await asyncio.sleep(30)
                msgdel.append(notifymsg)
                await self._delnewmembermsgs(msgdel)
                return
            await self.backupqdata(ctx.message.author.nick, ctx.message.content, "violations")
            self.rqobj["violations"][tf]["count"] += 1
            timeout = datetime.utcnow()
            # timeoutfuture = None
            if self.rqobj["violations"][tf]["count"] == 2:
                timeout += timedelta(days=90)
                self.rqobj["settings"]["violations"] = True
            if self.rqobj["violations"][tf]["count"] == 3:
                # indefinite
                timeout += timedelta(days=36500)
                self.rqobj["violations"][tf]["indefinite"] = True
            self.rqobj["violations"][tf]["time"] = timeout.timestamp()
            self.rqobj["violations"][tf]["reason"] = reason
        else:
            # TF not in the vio list, add them as a first vio
            await self.backupqdata(ctx.message.author.nick, ctx.message.content, "violations")
            self.rqobj["violations"][tf] = {}
            self.rqobj["violations"][tf]["count"] = 1
            ts = datetime.utcnow() + timedelta(days=30)
            self.rqobj["violations"][tf]["time"] = ts.timestamp()
            self.rqobj["violations"][tf]["indefinite"] = False
            self.rqobj["violations"][tf]["reason"] = reason
            self.rqobj["settings"]["violations"] = True

        dataIO.save_json(queue_file, self.rqobj)
        await self._queue_post()
        violationtext = { 1: "for 30 days", 2: "for 90 days", 3: "indefinitely"}
        viomessage = await self.bot.say("{}'s violation has been added with reason \"{}\" and will not be able to request {}.".format(tf, reason, violationtext[self.rqobj["violations"][tf]["count"]]))
        await asyncio.sleep(30)
        msgdel.append(viomessage)
        await self._delnewmembermsgs(msgdel)

    @rq.command(no_pm=True, pass_context=True, name="post")
    @checks.mod()
    async def queue_post(self, ctx):
        """Posts or updates the current queue. Handy for if it accidentally gets deleted."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id:  # recruitmentqueue channel
            return
        await self._queue_post()
        await self.bot.delete_message(ctx.message)

    @rq.command(no_pm=True, pass_context=True, name="timestamps")
    @checks.is_owner()
    async def queue_times(self, ctx):
        """Displays queue times for debugging."""
        timedata = []
        count = 1
        while count <= len(self.rqobj["queue"]):
            posttime = datetime.fromtimestamp(self.rqobj["queue"][str(count)]["posttime"])
            pingtime = datetime.fromtimestamp(self.rqobj["queue"][str(count)]["pingtime"])
            datastring = "Entry {} for {}:\n    Post Time: {}\n    Ping Time: {}".format(
                self.rqobj["queue"][str(count)]["position"], self.rqobj["queue"][str(count)]["TF"], posttime, pingtime
            )
            timedata.append(datastring)
            count += 1
        await self.bot.say("```\n{}\n```".format("\n".join(timedata)))

    @rq.command(no_pm=True, pass_context=True, name="checkts")
    @checks.is_owner()
    async def queue_checkts(self, ctx):
        """Compares UTC time to current system time."""
        utcnow = datetime.utcnow()
        utcnowts = utcnow.timestamp()
        utcfromts = datetime.fromtimestamp(utcnowts)
        utcfromtsts = utcfromts.timestamp()
        fromts = datetime.fromtimestamp(utcnowts, tz=None)
        fromtsts = fromts.timestamp()
        await self.bot.say("```\n{:<26} - {:<26}\n{} - {}\n{:<26} - {:<26}\n```".format("utcnow()", "utcfromtimestamp()", utcnow, utcfromts, utcnowts, utcfromtsts))
        await self.bot.say("```\n{:<26} - {:<26}\n{} - {}\n{:<26} - {:<26}\n```".format("utcnow()", "fromtimestamp()", utcnow, fromts, utcnowts, fromtsts))

    @rq.command(no_pm=True, pass_context=True, name="cleardata")
    @checks.is_owner()
    async def rq_clear(self, ctx):
        """Clears all data from the queue. For testing purposes."""
        self.rqobj["queue"] = {}
        self.rqobj["settings"]["queuebegin"] = None
        self.rqobj["settings"]["queuepost"] = None
        self.rqobj["settings"]["rulespost"] = None
        self.rqobj["violations"] = {"Whisky": {"count": 1, "indefinite": False, "reason": None, "time": None}}
        dataIO.save_json(queue_file, self.rqobj)
        await self.bot.say("Queue data cleared.")

    @rq.command(no_pm=True, pass_context=True, name="settonow")
    @checks.is_owner()
    async def rq_settonow(self, ctx):
        """Sets the first entry's timestamp to now. For testing purposes."""
        # oneday = timedelta(days=1)
        ping = datetime.utcnow()
        post = ping + timedelta(hours=4)
        count = 1
        while count <= len(self.rqobj["queue"]):
            if count != 1:
                ping += timedelta(days=2)
                post += timedelta(days=2)
            self.rqobj["queue"][str(count)]["posttime"] = post.timestamp()
            self.rqobj["queue"][str(count)]["pingtime"] = ping.timestamp()
            count += 1
        dataIO.save_json(queue_file, self.rqobj)
        await self._queue_post()

    @rq.command(no_pm=True, pass_context=True, name="settoday")
    @checks.mod()
    async def rq_settoday(self, ctx):
        """Sets the first entry's timestamp to today. This allows a TF to post \"today\" if the queue is empty."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id:  # recruitmentqueue channel
            return
        msgdel = []
        msgdel.append(ctx.message)
        # oneday = timedelta(days=1)
        now = datetime.utcnow()
        post = datetime(now.year, now.month, now.day)
        # ping = nowadjusted
        ping = post - timedelta(hours=4)
        count = 1
        while count <= len(self.rqobj["queue"]):
            if count != 1:
                ping += timedelta(days=2)
                post += timedelta(days=2)
            self.rqobj["queue"][str(count)]["posttime"] = post.timestamp()
            self.rqobj["queue"][str(count)]["pingtime"] = ping.timestamp()
            count += 1
        await self.backupqdata(ctx.message.author.nick, ctx.message.content, "queue")
        dataIO.save_json(queue_file, self.rqobj)
        await self._queue_post()
        setmsg = await self.bot.say("The first entry in the queue has been set to today, and any subsequent ones have been adjusted accordingly.")
        await asyncio.sleep(30)
        msgdel.append(setmsg)
        await self._delnewmembermsgs(msgdel)

    @rq.command(no_pm=True, pass_context=True, name="rules")
    @checks.mod()
    async def queue_rules(self, ctx):
        """Posts the recruitment queue rules. Handy for if it accidentally gets deleted."""
        if self.bbserver != ctx.message.server.id:
            return
        if self.queuechannel != ctx.message.channel.id:  # recruitmentqueue channel
            return
        msgdel = []
        msgdel.append(ctx.message)
        # If you want to recruit in redditbb, please post here.
        #
        # ***RULES***
        # ```md
        # 1. Post on time
        # 2. If your TF is full, take yourself off the queue.
        # 3. Include The Recruitment Form Link:
        # ```
        # <https://docs.google.com/forms/d/e/1FAIpQLScVYQtm-sINS6TnBewiGS0ac9jOL0e2cZT3TFtJKd71aXC1aw/viewform?c=0&w=1>
        #
        # ***VIOLATIONS***
        # ```
        # If you violate the rules,
        # your TF cannot be in the queue for 1 month (1st time),
        # 3 months (2nd time),
        # indefinite suspension/deverification vote (3rd time)
        # ```

        if self.rqobj["settings"]["rulespost"] is not None:
            try:
                oldrules = await self.bot.get_message(self.bot.get_channel(self.queuechannel), self.rqobj["settings"]["rulespost"])
                oldrulesnotify = await self.bot.say("The rules are already posted. Would you like to replace them?")
                msgdel.append(oldrulesnotify)
                isvalid = await self.bot.wait_for_message(timeout=30, author=ctx.message.author, channel=ctx.message.channel)
                if isvalid is not None:
                    yescheck = ["yes", "Yes", "yes.", "Yes.", "Ye", "ye", "Y", "y"]
                    msgdel.append(isvalid)
                    if isvalid.content in yescheck:
                        msgdel.append(oldrules)
                    else:
                        await self._delnewmembermsgs(msgdel)
                        return
            except:
                pass
        rules = "If you want to recruit in the /r/BoomBeach subreddit, please post here.\n\n***RULES***\n```md\n1. Post on time\n2. If your TF is full, take yourself off the queue.\n3. Include The Recruitment Form Link:\n```\n<https://docs.google.com/forms/d/e/1FAIpQLScVYQtm-sINS6TnBewiGS0ac9jOL0e2cZT3TFtJKd71aXC1aw/viewform?c=0&w=1>\n\n"
        rules += "***VIOLATIONS***\n```\nIf you violate the rules:\n1st offense - your TF cannot be in the queue for 1 month\n2nd offense - your TF cannot be in the queue for 3 months\n3rd offense - indefinite suspension/deverification vote\n```\n\n***COMMANDS***\n```\nadd, move, remove, listtfs, violation, post, rules\n```\nThese are subcommands, and need to be proceeded by `..rq`. Some queue commands may be GO only commands."
        # rules += "\n:forcepoint: :forcepoint: :forcepoint: :forcepoint: :forcepoint: :forcepoint: :forcepoint: :forcepoint: :forcepoint: :forcepoint: :forcepoint: :forcepoint: :forcepoint: :forcepoint: "
        forcepoint = None
        for e in ctx.message.server.emojis:
            if "forcepoint" in e.name:
                forcepoint = e
                break
        if forcepoint != None:
            rules += "\n\n{0} {0} {0} {0} {0} {0} {0} {0} {0} {0} {0} {0} {0} {0}".format(forcepoint)
        rulespost = await self.bot.send_message(self.bot.get_channel(self.queuechannel), rules)
        self.rqobj["settings"]["rulespost"] = str(rulespost.id)
        dataIO.save_json(queue_file, self.rqobj)
        await self.bot.delete_message(ctx.message)
        # await self._delnewmembermsgs(msgdel)

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
                # if "Bootcamp" in tf or "Smoke" in tf:
                #     tf = "BC/Smoke"
                tf = tf + ":"
                posttime = None
                posttime = datetime.fromtimestamp(self.rqobj["queue"][str(count)]["posttime"])
                postend = None
                postend = posttime + timedelta(days=1)  # end day is the day after
                queuestring = "{:<9} {}-{}".format(tf, posttime.strftime("%b %d"), postend.strftime("%b %d"))
                queueobj.append(queuestring)
                count += 1
            return "\n".join(queueobj)

    async def _queue_post(self):
        # posts or updates the current queue
        queuedata = self.queue_get()
        queuevio = ""
        if len(self.rqobj["violations"]) > 0:
            queuevio = self.queue_violatation()  # get vio data from data file and add it here
        queuepost = "**__Recruitment Queue__**\nFirst date is the changeover, when the TF's post can be swapped in. Earliest posting time is 00:00 UTC on that date. <https://time.is/UTC>\n"
        queuepost += "{}".format(queuevio)
        queuepost += "\n```md\nCurrent Queue\n=============\n\n"
        queuepost += queuedata
        queuepost += "\n```"

        if self.testingmode == True:
            '''
            if len(self.rqobj["queue"]) > 1:
                queuepost += "\nTesting mode active. Current UTC time: {}\n  Post time of #1 TF: {}\n  Post time of #2 TF: {}".format(datetime.utcnow(), datetime.fromtimestamp(self.rqobj["queue"]["1"]["posttime"]), datetime.fromtimestamp(self.rqobj["queue"]["2"]["posttime"]))
            elif len(self.rqobj["queue"]) > 0:
                queuepost += "\nTesting mode active. Current UTC time: {}\n  Post time of #1 TF: {}\n  Post time of #2 TF: ---".format(datetime.utcnow(), datetime.fromtimestamp(self.rqobj["queue"]["1"]["posttime"]))
            else:
                queuepost += "\nTesting mode active. Current UTC time: {}\n  Post time of #1 TF: ---\n  Post time of #2 TF: ---".format(datetime.utcnow())
            '''
            if len(self.rqobj["queue"]) > 1:
                queuepost += "\nTesting mode active. Current UTC time: {}\n  Post time of #1 TF: {}\n  Post time of #2 TF: {}".format(datetime.fromtimestamp(self.testingnow), datetime.fromtimestamp(self.rqobj["queue"]["1"]["posttime"]), datetime.fromtimestamp(self.rqobj["queue"]["2"]["posttime"]))
            elif len(self.rqobj["queue"]) > 0:
                queuepost += "\nTesting mode active. Current UTC time: {}\n  Post time of #1 TF: {}\n  Post time of #2 TF: ---".format(datetime.fromtimestamp(self.testingnow), datetime.fromtimestamp(self.rqobj["queue"]["1"]["posttime"]))
            else:
                queuepost += "\nTesting mode active. Current UTC time: {}\n  Post time of #1 TF: ---\n  Post time of #2 TF: ---".format(datetime.fromtimestamp(self.testingnow))

        if self.rqobj["settings"]["queuepost"] is not None:
            # have the bot edit the post instead of post a new one
            currentmsg = None
            try:
                currentmsg = await self.bot.get_message(self.bot.get_channel(self.queuechannel), self.rqobj["settings"]["queuepost"])
                await self.bot.edit_message(currentmsg, queuepost)
            except:
                pass
            if currentmsg is None:
                # the message got deleted by someone - so it needs to be posted new
                newqueue = await self.bot.send_message(self.bot.get_channel(self.queuechannel), queuepost)
                self.rqobj["settings"]["queuepost"] = str(newqueue.id)
        else:
            # if there isn't a post (deleted, first run, etc) then make a new one
            newqueue = await self.bot.send_message(self.bot.get_channel(self.queuechannel), queuepost)
            self.rqobj["settings"]["queuepost"] = str(newqueue.id)
        dataIO.save_json(queue_file, self.rqobj)

    def queue_violatation(self):
        # get queue violation data here and return it formatted

        #   violations
        #       "TF"
        #           "count" : #
        #           "time" : unixtime/null
        #           "indefinite" : True/False
        violist = []
        for tf in self.rqobj["violations"]:
            if self.rqobj["violations"][tf]["time"] is not None:
                # valid vio

                viodate = datetime.fromtimestamp(self.rqobj["violations"][tf]["time"])
                vio = "{} can not be on the queue until {}. Reason: {}.".format(tf, viodate.ctime().split()[1] + " " + viodate.ctime().split()[2] + " " + viodate.ctime().split()[4],  self.rqobj["violations"][tf]["reason"])
                violist.append(vio)
        s = ""
        if len(violist) > 0:
            s = "\n__Violations__\n{}\n".format("\"n\"".join(violist))

        return s

    async def queue_remove(self, tf, author, content, fromloop: bool=False):
        # internal function for the bot to remove a tf from the queue from the queue loop
        removednumber = None
        savedtimestamp = None  # don't know if I'll need this yet
        for key in self.rqobj["queue"]:
            if tf.lower() == self.rqobj["queue"][key]["TF"].lower():
                removednumber = self.rqobj["queue"][key]["position"]
                savedtimestamp = self.rqobj["queue"][key]["added"]
                break
        if removednumber is None:
            return False
        else:
            await self.backupqdata(author, content, "queue")
            count = removednumber
            if self.rqobj["queue"][str(removednumber)]["ackpost"] is not None:
                try:
                    msg = await self.bot.get_message(self.bot.get_channel(self.queuechannel), self.rqobj["queue"][str(removednumber)]["ackpost"])
                    await self.bot.delete_message(msg)
                except:
                    print("boombeach.py queue_remove Message Not Found exception for {}".format(self.rqobj["queue"][str(removednumber)]["TF"]))
            while count < len(self.rqobj["queue"]):
                self.rqobj["queue"][str(count)] = self.rqobj["queue"][str(count+1)]
                # print("{}".format(self.rqobj["queue"][str(count)]))
                self.rqobj["queue"][str(count)]["position"] = count
                count += 1
            del self.rqobj["queue"][str(len(self.rqobj["queue"]))]
            count = removednumber
            while count <= len(self.rqobj["queue"]) and fromloop is False:
                # NEED to add code to check for if it's the first entry being deleted, and that it's past their post window
                # IF it is then the times don't need to be modified.
                curposttime = datetime.fromtimestamp(self.rqobj["queue"][str(count)]["posttime"])
                curpingtime = datetime.fromtimestamp(self.rqobj["queue"][str(count)]["pingtime"])
                curposttime -= self.queueduration
                curpingtime -= self.queueduration
                self.rqobj["queue"][str(count)]["posttime"] = curposttime.timestamp()
                self.rqobj["queue"][str(count)]["pingtime"] = curpingtime.timestamp()
                count += 1
            if fromloop is True and len(self.rqobj["queue"]) > 0:
                self.rqobj["settings"]["queuebegin"] = self.rqobj["queue"]["1"]["posttime"]
            else:
                self.rqobj["settings"]["queuebegin"] = None

            dataIO.save_json(queue_file, self.rqobj)
            await self._queue_post()  # update the queue on discord
            return True

    # async def _queue_ping(self):
    #

    @rq.command(no_pm=True, pass_context=True, name="testingmode")
    @checks.is_owner()
    async def rq_tm(self, ctx):
        """Turns testing mode on or off"""
        if self.testingmode == True:
            self.testingmode = False
        else:
            self.testingmode = True
        self.testingcount = 0
        self.testinghours = 1
        self.testingnow = datetime.utcnow().timestamp()
        #dataIO.save_json(queue_file, self.rqobj)
        await self.bot.say("Queue testing mode is now {}".format("on" if self.testingmode == True else "off"))
        print("Queue testing mode is now {}".format("on" if self.testingmode == True else "off"))
        await self._queue_post()

    def check_violations(self):
        vio = False
        for tfname in self.rqobj["violations"].keys():
            if not self.rqobj["violations"][tfname]["indefinite"] and self.rqobj["violations"][tfname]["time"] is not None:
                vio = True
        self.rqobj["settings"]["violations"] = vio
        dataIO.save_json(queue_file, self.rqobj)

    @rq.group(no_pm=True, pass_context=True, name="pinglist")
    @checks.mod()
    async def rq_pinglist(self, ctx):
        """Displays the current ping list that is used in the queue."""
        # print("channel id: {} - isinstance string: {}".format(ctx.message.channel.id, isinstance(ctx.message.channel.id, str)))
        if (self.queuechannel != ctx.message.channel.id) and (self.opchannel != ctx.message.channel.id) and ('340269179737210890' != ctx.message.channel.id):  # recruitmentqueue, op room, or bot testing
            return
        plist = "Queue ping list:\n```\n"
        for tf in sorted(list(self.rqobj["TFs"].keys())):
            # plist += "{:<9} {}\n".format(str(tf) + ":", ", ".join(self.rqobj["TFs"][tf]))
            plist += "{:<9}".format(str(tf) + ":")
            for mbrid in self.rqobj["TFs"][tf]:
                # plist += " " + str(ctx.message.server.get_member(mbrid).nick) # ", ".join(self.rqobj["TFs"][tf])
                plist += "  " + str(discord.utils.get(ctx.message.server.members, id=mbrid)) # ", ".join(self.rqobj["TFs"][tf])
            plist += "\n"
        plist += "```\nThis message and your `{}rq pinglist` command will be deleted automatically after 60 seconds.".format(ctx.prefix)
        plmsg = await self.bot.say(plist)
        msgdel = []
        msgdel.append(ctx.message)
        msgdel.append(plmsg)
        await asyncio.sleep(60)
        await self._delnewmembermsgs(msgdel)

    # TODO: add functions to add and remove people in the ping list. Possibly have the bot remember who did the
    # ..rq add and use them as a pingee.

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

            if self.rqobj["settings"]["violations"] == True:
                # test if violation times are over
                for tfname in self.rqobj["violations"].keys():
                    if self.rqobj["violations"][tfname]["count"] == 3 or self.rqobj["violations"][tfname]["time"] is None:
                        # skip if it's indefinite or already cleared
                        continue
                    else:
                        if datetime.utcnow().timestamp() > self.rqobj["violations"][tfname]["time"]:
                            await self.backupqdata("Intel", "self.queue_loop() clear violation", "violations") # ctx.message.author.nick, ctx.message.content
                            self.rqobj["violations"][tfname]["time"] = None
                            dataIO.save_json(queue_file, self.rqobj)
                            await self._queue_post()
                        self.check_violations()

            if len(self.rqobj["queue"]) > 0:
                if self.testingmode is False:
                    now = datetime.utcnow()
                else:
                    now = datetime.fromtimestamp(self.testingnow)
                oneposttime = datetime.fromtimestamp(self.rqobj["queue"]["1"]["posttime"])
                onepingtime = datetime.fromtimestamp(self.rqobj["queue"]["1"]["pingtime"])
                if now > oneposttime + self.queueduration:
                    # if it's been more than 2 days that the post has been able to be up then delete it, along with the ackpost (ping)
                    # await self.backupqdata("Intel", "self.queue_loop() delete - past queue duration") # ctx.message.author.nick, ctx.message.content
                    # comment out stuff below - it's handled in queue_remove
                    # if self.rqobj["queue"]["1"]["ackpost"] is not None:
                    #     ackmsg = None
                    #     try:
                    #         ackmsg = await self.bot.get_message(self.bot.get_channel(self.queuechannel), self.rqobj["queue"]["1"]["ackpost"])
                    #     except:
                    #         print("boombeach.py queue_loop ackpost message not found for {}".format(self.rqobj["queue"]["1"]["TF"]))
                    #     if ackmsg is not None:
                    #         await self.bot.delete_message(ackmsg)
                    if await self.queue_remove(self.rqobj["queue"]["1"]["TF"], "Intel", "self.queue_loop() delete - past queue duration", True) == True:
                        print("Deleted the first entry from the queue")
                    else:
                        print("Something went wrong - that TF isn't in the queue.")
                # if now < oneposttime and now > onepingtime and self.rqobj["queue"]["1"]["ackpost"] is None:
                if len(self.rqobj["queue"]) > 0:
                    if now > onepingtime and self.rqobj["queue"]["1"]["ackpost"] is None:
                        # if it's before the time to post, after the time to ping, and a ping hasn't been sent...
                        pingpeople = self.rqobj["TFs"][self.rqobj["queue"]["1"]["TF"]]
                        if len(pingpeople) > 2:
                            # only get 2 choices from the possible members to ping if there's more than 2
                            pingpeople = sample(pingpeople, k=2)
                        pinglist = []
                        for pingperson in pingpeople:
                            if self.testingmode == True:
                                pinglist.append("`<@" + pingperson + ">`")
                            else:
                                pinglist.append("<@" + pingperson + ">")
                        howlong = None
                        if now > oneposttime:
                            howlong = "now"
                        else:
                            howlongtime = oneposttime - now
                            # howlong = "in {} hours and {} minutes".format(howlongtime.hours, howlongtime.minutes)
                            hltd = divmod(howlongtime.seconds, 86400)
                            hlth = divmod(hltd[1], 3600)
                            hltm = divmod(hlth[1], 60)
                            howlong = "in {} hours and {} minutes".format(hlth[0], hltm[0])
                        # pingmsg = await self.bot.send_message(self.bot.get_channel(self.queueping), "{} - **Reminder**, you will be able to put up your recruitment post for {} in just under 4 hours.".format(" ".join(pinglist), self.rqobj["queue"]["1"]["TF"]))
                        pingdata = "{} - **Reminder**, you will be able to put up your recruitment post for {} {}.".format(" ".join(pinglist), self.rqobj["queue"]["1"]["TF"], howlong)
                        pingmsg = await self.bot.send_message(self.bot.get_channel(self.queueping), pingdata)
                        if self.rqobj["queue"]["1"]["TF"] == "Trichon":
                            await self.bot.send_message(self.bot.get_channel("206092939112349697"), pingdata)
                        self.rqobj["queue"]["1"]["ackpost"] = pingmsg.id
                        dataIO.save_json(queue_file, self.rqobj)
                # check if #1 is past ping time and #2 is within their ping window

                if len(self.rqobj["queue"]) > 1:
                    twoposttime = datetime.fromtimestamp(self.rqobj["queue"]["2"]["posttime"])
                    twopingtime = datetime.fromtimestamp(self.rqobj["queue"]["2"]["pingtime"])
                    # print("twoposttime: {}\ntwopingtime: {}".format(twoposttime, twopingtime))
                    if now < twoposttime and now > twopingtime and self.rqobj["queue"]["2"]["ackpost"] is None:
                        pingpeople = self.rqobj["TFs"][self.rqobj["queue"]["2"]["TF"]]
                        if len(pingpeople) > 2:
                            # only get 2 choices from the possible members to ping if there's more than 2
                            pingpeople = sample(pingpeople, k=2)
                        pinglist = []
                        for pingperson in pingpeople:
                            if self.testingmode == True:
                                pinglist.append("`<@" + pingperson + ">`")
                            else:
                                pinglist.append("<@" + pingperson + ">")
                        if now > twoposttime:
                            howlong = "now"
                        else:
                            howlongtime = twoposttime - now
                            hltd = divmod(howlongtime.seconds, 86400)
                            hlth = divmod(hltd[1], 3600)
                            hltm = divmod(hlth[1], 60)
                            howlong = "in {} hours and {} minutes".format(hlth[0], hltm[0])
                        # pingmsg = await self.bot.send_message(self.bot.get_channel(self.queueping), "{} - **Reminder**, you will be able to put up your recruitment post for {} in just under 4 hours.".format(" ".join(pinglist), self.rqobj["queue"]["2"]["TF"]))
                        pingdata = "{} - **Reminder**, you will be able to put up your recruitment post for {} {}.".format(" ".join(pinglist), self.rqobj["queue"]["2"]["TF"], howlong)
                        pingmsg = await self.bot.send_message(self.bot.get_channel(self.queueping), pingdata)
                        if self.rqobj["queue"]["2"]["TF"] == "Trichon":
                            await self.bot.send_message(self.bot.get_channel("206092939112349697"), pingdata)
                        self.rqobj["queue"]["2"]["ackpost"] = pingmsg.id
                        dataIO.save_json(queue_file, self.rqobj)
            # await asyncio.sleep(300)
            if self.testingmode == True:
                # goback = timedelta(hours=1)
                # count = 1
                # while count <= len(self.rqobj["queue"]):
                #     self.rqobj["queue"][str(count)]["posttime"] -= goback.total_seconds()
                #     self.rqobj["queue"][str(count)]["pingtime"] -= goback.total_seconds()
                #     if count == 1:
                #         print("boombeach.py queue_loop: current time: {}\n    #1 post timestamp: {}\n    + 2 days (2nd TF): {}".format(datetime.utcnow(), datetime.fromtimestamp(self.rqobj["queue"]["1"]["posttime"]), datetime.fromtimestamp(self.rqobj["queue"]["1"]["posttime"] + timedelta(days=2).total_seconds())))
                #     count += 1
                # dataIO.save_json(queue_file, self.rqobj)
                print("testingnow: {}\n    1 post: {}\n    2 post: {}".format(datetime.fromtimestamp(self.testingnow), datetime.fromtimestamp(self.rqobj["queue"]["1"]["posttime"]) if len(self.rqobj["queue"]) > 0 else "---", datetime.fromtimestamp(self.rqobj["queue"]["1"]["posttime"] + timedelta(days=2).total_seconds()) if len(self.rqobj["queue"]) > 0 else "---"))
                self.testingcount += 1

                if self.testingcount >= 3:
                    await self._queue_post()
                    self.testingcount = 0
                if self.testingnow == None:
                    self.testingnow = datetime.utcnow().timestamp()
                else:
                    self.testingnow = datetime.utcnow().timestamp() + timedelta(hours=self.testinghours).total_seconds()
                self.testinghours += 1
                await asyncio.sleep(11)
            else:
                await asyncio.sleep(60)  # was 300

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
        msgdel = []
        msgdel.append(ctx.message)
        isvalid = None
        tfdata = dataIO.load_json(tfdata_file)
        approvedata = dataIO.load_json(approve_file)
        validmocl = ["member", "officer", "co", "coleader", "co-leader", "leader"]
        yescheck = ["yes", "Yes", "yes.", "Yes.", "Ye", "ye", "Y", "y"]
        tfcroles = {
                "member": "TFC Members",
                "officer": "TFC Officers",
                "coleader": "TFC Co-Leaders",
                "leader": "TFC Leaders"
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
                    await self._delnewmembermsgs(msgdel)
                    return
                else:
                    user = m
            else:
                timeoutmsg = await self.bot.say("You took too long to respond. Cancelling addmember setup and cleaning up this mess.")
                msgdel.append(timeoutmsg)
                await asyncio.sleep(5)
                await self._delnewmembermsgs(msgdel)
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
                    await self._delnewmembermsgs(msgdel)
                    return
            else:
                timeoutmsg = await self.bot.say("You took too long to respond. Cancelling addmember setup and cleaning up this mess.")
                msgdel.append(timeoutmsg)
                await asyncio.sleep(5)
                await self._delnewmembermsgs(msgdel)
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
                    await self._delnewmembermsgs(msgdel)
                    return
            else:
                timeoutmsg = await self.bot.say("You took too long to respond. Cancelling addmember setup and cleaning up this mess.")
                msgdel.append(timeoutmsg)
                await asyncio.sleep(5)
                await self._delnewmembermsgs(msgdel)
                return

        if not interactive:
            if user not in ctx.message.server.members or user is None:
                notvalidmember = await self.bot.say("Not a valid member. Cancelling addmember setup and cleaning up this mess.")
                msgdel.append(notvalidmember)
                await asyncio.sleep(15)
                await self._delnewmembermsgs(msgdel)
                return
            if tf is None:
                notvalidtf = await self.bot.say("I need a TF name from the list in `{0}listtfs` to be able to assign a TF and Roles. The syntax for this command is `{0}addmember @user#1234 taskforce rank`".format(ctx.prefix))
                msgdel.append(notvalidtf)
                await asyncio.sleep(15)
                await self._delnewmembermsgs(msgdel)
                return
            tf = tf.lower()
            if tf not in tfdata.keys():
                notvalidtf = await self.bot.say("That is not a valid TF choice. Please look at the valid choices using `{}listtfs` and try again. Cancelling addmember setup and cleaning up this mess.".format(ctx.prefix))
                msgdel.append(notvalidtf)
                await asyncio.sleep(15)
                await self._delnewmembermsgs(msgdel)
                return
            if mocl is None:
                notvalidrank = await self.bot.say("I need a rank from the list in `{0}listtfs` to be able to assign a TF and Roles. They syntax for this command is `{0}addmember @user#1234 taskforce rank`".format(ctx.prefix))
                msgdel.append(notvalidrank)
                await asyncio.sleep(15)
                await self._delnewmembermsgs(msgdel)
                return
            mocl = mocl.lower()
            if mocl not in validmocl:
                notvalidrank = await self.bot.say("That is not a valid rank. Please look at the valid rank choices in `{}listtfs` and try again. Cancelling addmember setup and cleaning up this mess.".format(ctx.prefix))
                msgdel.append(notvalidrank)
                await asyncio.sleep(15)
                await self._delnewmembermsgs(msgdel)
                return

        if mocl in ["co", "co-leader"]:
            # standardize co / co-leader / coleader to just "coleader" for subsequent use
            mocl = "coleader"

        # check to see what the highest role that the user can give - notify them if they can't assign a role
        toprank = {"Moderators": ["member", "coleader", "leader"],
                   "Global Operators": ["member", "coleader", "leader"],
                   "TFC Leaders": ["member", "coleader"],
                   "TFC Co-Leaders": ["member"],
                   "Affiliate Leaders": ["member"]}
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
        if "TFC Co-Leaders" in toprole:  # colead giving colead
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
                        await self._delnewmembermsgs(msgdel)
                        return
                else:
                    # timeout or not "yes"
                    noans = await self.bot.say("You took too long. Cancelling new member setup and cleaning up this mess.")
                    msgdel.append(noans)
                    await asyncio.sleep(10)
                    await self._delnewmembermsgs(msgdel)
                    return

        if "TFC Co-Leaders" in toprole and skipnext is False:  # colead giving lead
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
                        await self._delnewmembermsgs(msgdel)
                        return
                else:
                    # timeout or not "yes"
                    noans = await self.bot.say("You took too long. Cancelling addmember setup and cleaning up this mess.")
                    msgdel.append(noans)
                    await asyncio.sleep(10)
                    await self._delnewmembermsgs(msgdel)
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
                        await self._delnewmembermsgs(msgdel)
                        return
                else:
                    # timeout or not "yes"
                    noans = await self.bot.say("You took too long. Cancelling new member setup and cleaning up this mess.")
                    msgdel.append(noans)
                    await asyncio.sleep(10)
                    await self._delnewmembermsgs(msgdel)
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
                        await self._delnewmembermsgs(msgdel)
                        return
                else:
                    # timeout or not "yes"
                    noans = await self.bot.say("You took too long. Cancelling new member setup and cleaning up this mess.")
                    msgdel.append(noans)
                    await asyncio.sleep(10)
                    await self._delnewmembermsgs(msgdel)
                    return

        rolestoadd = []
        if "Affiliate" not in tfdata[tf]["member"]:  # This prevents Affiliates from getting TFC roles
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
        await self.bot.add_roles(user, *roleobjs)  # needs the * for list unpacking

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
            # rename here
            try:
                await self.bot.change_nickname(user, renameto)
                renmessage = await self.bot.say("{}'s nick has been changed to: {}".format(previousnick, renameto))
                msgdel.append(renmessage)
            except discord.Forbidden:
                renameerror = await self.bot.say("There was a problem changing {}'s nickname.".format(previousnick))
                msgdel.append(renameerror)

        rolestring = " ".join(rolesadded)
        logmsg = "My __addmember__ command was used. Here's the details:\n```\nUsed by: {}\n     ID: {}\nUsed on: {}\n     ID: {}\nNickname before: {}\nNickname after: {}\nRoles assigned: {}\n```".format(ctx.message.author.name + "#" + ctx.message.author.discriminator, ctx.message.author.id, user.name + "#" + user.discriminator, user.id, previousnick, renameto, rolesadded)
        mlchan = self.bot.get_channel('284786888957624320')  # mod log channel
        await self.bot.send_message(mlchan, logmsg)

        notifychan = self.bot.get_channel(tfdata[tf]["notify"])
        await self.bot.send_message(notifychan, "{}, You now have roles for **{}** and your nickname has been changed accordingly. Here is your TF room.".format(user.mention, tfdata[tf]["rename"]))

        donemessage = await self.bot.say("I'm exhausted after all of that work. I'll clean up our mess after a 60 second break.")
        msgdel.append(donemessage)
        await asyncio.sleep(60)
        await self._delnewmembermsgs(msgdel)

    @commands.command(no_pm=True, pass_context=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def approve(self, ctx, case, answer):
        """Approve or deny a pending leadership role that was created in addmember

        If answer is yes it will approve the role
        If answer is no it will deny the role"""
        if "181243681951449088" not in ctx.message.server.id:  # BB server
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
            "approved":    None,
            "approver":    None,
            "approverid":  None,
            "author":      author.name + "#" + author.discriminator,
            "case":        case,
            "member":      member.id,
            "membername":  member.nick if member.nick else member.name,
            "notifychan":  notifymsg.channel.id,
            "notifymsg":   notifymsg.id,
            "role":        role,
            "temprole":    temprole
        }
        approvedata[str(case)] = casedata
        dataIO.save_json(approve_file, approvedata)

    @commands.command(no_pm=True, pass_context=True, name="listtfs")
    @checks.mod_or_permissions(manage_roles=True)
    async def addmember_listtfs(self, ctx):
        """Produces a list of valid TF names and ranks to use with the addmember command"""
        if "181243681951449088" not in ctx.message.server.id:  # BB server
            return

        tfdata = dataIO.load_json(tfdata_file)
        toprank = {"Moderators": ["member", "officer", "coleader", "leader"],
                   "Global Operators": ["member", "officer", "coleader", "leader"],
                   "TFC Leaders": ["member", "officer", "coleader"],
                   "TFC Co-Leaders": ["member", "officer"],
                   "Affiliate Leaders": ["member"]}
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

    async def _delnewmembermsgs(self, msgs):
        if len(msgs) < 2:
            await self.bot.delete_message(msgs)
        if len(msgs) >= 2:
            await self.bot.delete_messages(msgs)

    '''
    async def _delnewmembermsgs(self):
        if len(self.msgdel) < 2 and len(self.msgdel) > 0:
            await self.bot.delete_message(self.msgdel)
        if len(self.msgdel) >= 2:
            await self.bot.delete_messages(self.msgdel)
        self.msgdel = [] #reset
    '''

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
        plantydefault = {"started": curdate, "planties": 0}
        print("Creating empty planty.json...")
        dataIO.save_json(planty_file, plantydefault)


def setup(bot):
    check_folders()
    check_files()
    n = BoomBeach(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.queue_loop())
