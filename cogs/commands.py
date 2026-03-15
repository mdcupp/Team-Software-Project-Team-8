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
        !reactionUser <reaction> <username>
        !reactionLeaderboard <reaction> <number> <sent/received>
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
        
        # Check if user exists
        try:
            member = await commands.MemberConverter().convert(ctx, username[0])
        except commands.errors.MemberNotFound:
            await ctx.send(f"**{username[0]}** could not be found in this server.")
            return

        # Get Activity List
        list = self.db.getActivityTime(username)
        print(list)

        printable_list = f"{'Activity':<16s}{'H:Min:Sec':<9s}\n"
        
        # Turn seconds in Hours, Minutes, Seconds
        for activity, seconds in list:
            minutes = 0
            hours = 0
            while seconds > 60:
                seconds -= 60
                minutes += 1
            while minutes > 60:
                minutes - 60
                hours += 1

            # Format it
            time = f"{hours}:{minutes:02d}:{seconds:02d}"
            printable_list = printable_list + f"{activity:16s}{time:9s}\n"

        # Print it
        await ctx.send(f"Recorded activities for **{username[0]}**:\n```{printable_list}```")

    # View how many times a user has sent a reaction
    @commands.command()
    async def reactionUser(self, ctx, *parameters):
        # Check if arguments received
        if (len(parameters) < 2):
            await ctx.send("Usage: !reactionUser <reaction> <username>")
            return
        
        # Check if user exists
        try:
            member = await commands.MemberConverter().convert(ctx, parameters[1])
        except commands.errors.MemberNotFound:
            await ctx.send(f"**{parameters[1]}** could not be found in this server.")
            return

        # member.id and parameters[0] will need to be sent to table here for reaction count query
        
        # as far as I can tell there is no easy way to check if a given global emoji exists, as emojiConverter and emoji objects are only for custom emojis, 
        # so verification of an emoji's existence should be based on if it is present in the table, make sure table can store both normal and custom

        sent, received = self.db.getReactionCount(member.id, parameters[0])

        await ctx.send(f"{parameters[0]} counts for **{member.name}**:\n"
                       f"Sent: {sent}\n"
                       f"Received: {received}"
                      )

    # View leaderboard for a reaction
    @commands.command()
    async def reactionLeaderboard(self, ctx, *parameters):
        # Check if correct arguments received
        if (len(parameters) < 3 or (parameters[2] != 'sent' and parameters[2] != 'received')):
            await ctx.send("Usage: !reactionLeaderboard <reaction> <number> <sent/received>")
            return
        
        try:
            limit = int(parameters[1])
        except ValueError:
            await ctx.send("Error: Number is invalid")
            return

        # Command has a limit of 50 users to prevent bot from reaching Discord's character limit
        if (limit > 50 or limit < 1):
            await ctx.send("Error: Number must be between 1 and 50")
            return

        # verification of passed emoji existence based on table query still must be added here
        
        # Dummy list, the tuples could be formatted differently depending on how database is designed
        # Should be properly ordered by the query, query will differ based on whether sent/received passed in
        list = [('453639752781135873', 50, 29), ('1477158009447911525', 29, 14)]
        
        printable_list = f"{'Member':<16s}{'Sent':<5s}{'Received'}\n"
        for id, sent, received in list:
            member = await commands.MemberConverter().convert(ctx, id)
            printable_list = printable_list + f"{member.name:<16s}{sent:<5d}{received:<5d}\n"

        await ctx.send(f"Top {limit} users of {parameters[0]} by total {parameters[2]}:\n```{printable_list}```")
    

