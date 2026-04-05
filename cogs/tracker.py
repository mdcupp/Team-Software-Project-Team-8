import discord
from discord.ext import commands
from datetime import datetime
import time

class Tracker(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    # On every message sent
    @commands.Cog.listener()
    async def on_message(self, message):
        # Don't scan your own message or system messages
        if message.author == self.bot.user or message.is_system():
            return

        content = str(message.content)

        #Track not commands
        if not content.startswith('!'):
            self.db.insertMessage(message.author, content)

    # On every reaction sent
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Ignore bot reactions
        if user.bot:
            return

        emoji = str(reaction.emoji)

        sender_id = user.id
        receiver_id = reaction.message.author.id
        message_id = reaction.message.id

        self.db.insertReaction(emoji, sender_id, receiver_id, message_id)
    
    # On status or activity updates
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        
        beforeActivityList = before.activities
        afterActivityList = after.activities

        # Iterate through tuple of activities until one that should be tracked is found
        i = 0
        for act in beforeActivityList:
            if act.type == discord.ActivityType.playing:
                break
            i = i + 1

        # If a valid activity was not found, return
        if i == len(beforeActivityList):
            return
        
        # Iterate through new activity list to check if the old one was closed
        for act in afterActivityList:
            # If activity is still open, then return
            if act.type == discord.ActivityType.playing and act.application_id == beforeActivityList[i].application_id:
                return

        activity = beforeActivityList[i]

        # Valid activity that was open has now been closed, time spent is tracked as seconds
        time_spent = int(time.time()) - int(activity.timestamps['start'] / 1000)
        print(f"LOG user - {after.name} activity - {activity.name} time - {time_spent}")

        self.db.insertActivity(after.name, activity.name, time_spent)

    # When a user joins the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"LOG: {member.name} joined the server")
 
        # store in DB
        self.db.insertJoin(member.id, member.name)
        if (not self.db.isUserTracked(member.id)):
            self.db.insertUser(member.id, member.name, member.display_name, datetime.now().timestamp())

        # output message
        channel = member.guild.system_channel
        if channel:
           await channel.send(f"**{member.name}** joined the server")
 
    # When a user leaves the server
    @commands.Cog.listener()
    async def on_member_remove(self, member):
       print(f"LOG: {member.name} left the server")

       # store in DB
       self.db.insertLeave(member.id, member.name)

       # output message
       channel = member.guild.system_channel
       if channel:
          await channel.send(f"**{member.name}** left the server")

    # When a user deletes a message
    @commands.Cog.listener()
    async def on_message_delete(self, message):     
        content = str(message.content)
        if not content:
           content = '<no text>'

        # Choose channel to output to
        channel = message.author.guild.system_channel
        if not channel:
            channel = message.channel

        # Get string of attachments
        attachString = ""
        for attachment in message.attachments:
            attachString += attachment.url + " "

        print(f"LOG: Message '{message.author}: {content} {attachString}' was deleted")
        await channel.send(f"**Deleted message:** '{message.author}: {content} {attachString}'")

    #Whenever the bot starts up
    @commands.Cog.listener()
    async def on_ready(self):
        for server in self.bot.guilds:
            for member in server.members:
                if (not self.db.isUserTracked(member.id)):
                    self.db.insertUser(member.id, member.name, member.display_name, "Unknown")
            