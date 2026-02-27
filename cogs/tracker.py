import discord
from discord.ext import commands

class Tracker(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    #On every message sent
    @commands.Cog.listener()
    async def on_message(self, message):
        # Don't scan your own message or system messages
        if message.author == self.bot.user or message.is_system():
            return

        author_name = str(message.author)
        content = str(message.content)

        #Track not commands
        if not content.startswith('!'):
            self.db.insertMessage(author_name, content)