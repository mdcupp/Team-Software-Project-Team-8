import discord
from discord.ext import commands
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

        # Valid activity that was open has now been closed, time spent is tracked as seconds
        time_spent = int(time.time()) - int(beforeActivityList[i].timestamps['start'] / 1000)
        print(time_spent)
