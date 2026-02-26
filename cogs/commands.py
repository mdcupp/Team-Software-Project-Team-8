import discord
from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    #Commands

    # Command to print other commands
    @commands.command()
    async def helpMe(self, ctx):
        await ctx.send("!helpMe - List Commands")
        await ctx.send("!ping - Test Command")
        await ctx.send("!resetMessageTable - Deletes and Creates Messages Table")
        await ctx.send("!getMessageCount - Prints message count recorded from user")

    # Test command to make sure bot is running
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

    # Removes table from database, then creates a new one
    @commands.command()
    async def resetMessageTable(self, ctx):
        self.db.resetMessageTable()
        await ctx.send("Table Reset")


    # Prints message count from user
    @commands.command()
    async def getMessageCount(self, ctx):
        author_name = str(ctx.author)
        
        count = self.db.getMessageCount(author_name)
        
        await ctx.send(f"{author_name} has recorded {count} messages.")

