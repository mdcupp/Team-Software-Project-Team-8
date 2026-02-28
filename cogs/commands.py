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
        await ctx.send("""
        **Command List**:
        !helpMe - List Commands
        !ping - Test Command
        !messageTotal <username> - Prints message count recorded from user
        !resetMessageTable - Clear message table
        !displayData <username> - Get public data of a user (Doesn't pull real data yet)
        !activityList <username> - Get activity list of a user (Doesn't pull real data yet) 
    """)

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
    async def messageTotal(self, ctx, *username):
        if (len(username) == 0):
            await ctx.send("Usage: !messageTotal <username>")
            return
        
        try:
            member = await commands.MemberConverter().convert(ctx, username[0])
        except commands.errors.MemberNotFound:
            await ctx.send(f"**{username[0]}** could not be found in this server.")
            return

        count = self.db.getMessageCount(member.id)
        
        await ctx.send(f"**{member.name}** has sent {count} messages.")


    # Display public data of a given user
    @commands.command()
    async def displayData(self, ctx, *username):
        # Check if arguments received
        if (len(username) == 0):
            await ctx.send("Usage: !displayData <username>")
            return
        image = discord.File('placeholder.png')

        await ctx.send(file = image, content = f"\n**Username:** {username[0]}\n**User ID:**\n**Account Created:**")

    # View activity list of a given user
    @commands.command()
    async def activityList(self, ctx, *username):
        # Check if arguments received
        if (len(username) == 0):
            await ctx.send("Usage: !activityList <username>")
            return
        
        # Dummy list, but should be formatted how it would be if this data was pulled from a table
        list = [('activity1', '12'), ('activity22', '14')]

        printable_list = ""
        for activity, time in list:
            printable_list = printable_list + f"{activity:16s}{time:5s}\n"

        print(printable_list)

        await ctx.send(f"Recorded activities for **{username[0]}**:\n```{printable_list}```")