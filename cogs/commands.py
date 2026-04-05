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
        !activityList <username> - Get activity list of a user
        !reactionUser <reaction> <username> - Get sent/received count of a reaction for a given user
        !reactionLeaderboard <reaction> <sent/received> - See leaderboard of sent/received counts for a given reaction
        !memberHistory <username> - See history of joins and leaves for a given user
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

    # Remove event table from database and create a new one
    @commands.command()
    async def resetEventTable(self, ctx):
        self.db.resetEventTable()
        await ctx.send("Event Table Reset")

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

        printable_list = f"{'Activity':<32s} {'H:Min:Sec':<9s}\n"
        
        # Turn seconds in Hours, Minutes, Seconds
        i = 0
        for activity, seconds in list:
            minutes = 0
            hours = 0
            while seconds > 60:
                seconds -= 60
                minutes += 1
            while minutes > 60:
                minutes - 60
                hours += 1

            # Cut off activities that are too long
            if len(activity) > 32:
                activity = activity[:29] + "..."

            # Format it
            time = f"{hours}:{minutes:02d}:{seconds:02d}"
            printable_list = printable_list + f"{activity:32s} {time:7s}\n"

            # Max of 45 rows can be printed until character limit will be reached
            i = i + 1
            if i == 45:
                break 

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
        
        sent, received = self.db.getReactionCount(member.id, parameters[0])

        if (sent == 0 and received == 0):
            await ctx.send(f"{parameters[0]} has no associated data.")
            return

        await ctx.send(f"{parameters[0]} counts for **{member.name}**:\n"
                       f"Sent: {sent}\n"
                       f"Received: {received}"
                      )

    # View leaderboard for a reaction
    @commands.command()
    async def reactionLeaderboard(self, ctx, *parameters):
        # Check if correct arguments received
        if (len(parameters) < 2 or (parameters[1] != 'sent' and parameters[1] != 'received')):
            await ctx.send("Usage: !reactionLeaderboard <reaction> <sent/received>")
            return
        
        list = self.db.getReactionLeaderboard(parameters[0], parameters[1])

        if not list:
            await ctx.send(f"{parameters[0]} has no associated data.")

        printable_list = f"{'Member':<16s} {str.capitalize(parameters[1]):<5s}\n"
        for id, number in list:
            stringId = f"{id}"
            member = await commands.MemberConverter().convert(ctx, stringId)
            printable_list = printable_list + f"{member.name:<16s} {number:<5d}\n"

        await ctx.send(f"Top users of {parameters[0]} by total {parameters[1]}:\n```{printable_list}```")
    
    @commands.command()
    async def memberHistory(self, ctx, *username):
       if len(username) == 0:
          await ctx.send("Usage: !memberHistory <username>")
          return
       
       try:
          member = await commands.MemberConverter().convert(ctx, username[0])
          user_id = member.id
          display_name = member.name
       except commands.errors.MemberNotFound:
          result = self.db.cursor.execute(
                   "SELECT user_id, username FROM member_events WHERE username = ? COLLATE NOCASE LIMIT 1;",
                   (username[0],)
          ).fetchone()
          if not result:
             await ctx.send(f"No data found for **{username[0]}**.")
             return
          user_id, display_name = result

       events = self.db.getMemberHistory(user_id)

       if not events:
          await ctx.send("No join/leave data found.")
          return

       output = ""
       for event, time in events:
          time_str = str(time)
          time_str = time_str.split(".")[0]

          output += f"{event:<6} {time_str}\n"

       await ctx.send(f"History for **{display_name}**:\n```{output}```")
