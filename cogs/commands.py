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
        embed = discord.Embed(
        title = "**Command List:**",
            color = discord.Color.blue()
       )

        embed.add_field(name="", value="""
        !helpMe - List Commands
        !ping - Test Command
        !messageTotal <username> - Prints message count recorded from user
        !messageLeaderboard - Prints leaderboard of total message counts in server
        !resetMessageTable - Clear message table
        !userInfo <username> - Get public data of a user
        !resetUsersTable - Clears the user table
        !activityList <username> - Get activity list of a user
        !reactionUser <reaction> <username> - Get sent/received count of a reaction for a given user
        !reactionLeaderboard <reaction> <sent/received> - See leaderboard of sent/received counts for a given reaction
        !memberHistory <username> - See history of joins and leaves for a given user
        """, inline=False)

        await ctx.send(embed=embed)

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
        
        if (username[0] == 'server'):
            result = self.db.getMessageServerTotal()
            
            await ctx.send(f"Total amount of messages sent in server: {result}")
            return

        try:
            member = await commands.MemberConverter().convert(ctx, username[0])
        except commands.errors.MemberNotFound:
            await ctx.send(f"**{username[0]}** could not be found in this server.")
            return

        count = self.db.getMessageCount(member.id)
        
        await ctx.send(f"**{member.name}** has sent {count} messages.")

    # Prints message leaderboard of server
    @commands.command()
    async def messageLeaderboard(self, ctx):

        list = self.db.getMessageLeaderboard()
        
        printable_list = f"{'Member':<16s} {'Total':<5s}\n"
        for id, number in list:
            stringId = f"{id}"
            member = await commands.MemberConverter().convert(ctx, stringId)
            printable_list = printable_list + f"{member.name:<16s} {number:<5d}\n"

        await ctx.send(f"Top message counts of users:\n```{printable_list}```")

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

        embed = discord.Embed(
            title = f"Recorded Activites for: {username[0]}",
            color = discord.Color.blue()
        )

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
            embed.add_field(name=f"{i+1}. {activity}", value=f"{time}", inline=False)

            # Max of 45 rows can be printed until character limit will be reached
            i = i + 1
            if i == 45:
                break 

                
        embed.set_thumbnail(url=member.display_avatar.url)

        # Print it
        await ctx.send(embed=embed)

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

        embed = discord.Embed(
            title = f"{parameters[0]} counts for: {member.name}",
            color = discord.Color.blue()
        )

        embed.add_field(name=f"Sent:",value=f"{sent}",inline=False)
        embed.add_field(name=f"Received:",value=f"{received}",inline=False)

        embed.set_thumbnail(url=member.display_avatar.url)


        await ctx.send(embed=embed)

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
            return

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
            member = await self.bot.fetch_user(user_id)

        events = self.db.getMemberHistory(user_id)

        if not events:
            await ctx.send("No join/leave data found.")
            return
       
        # make an embed cause it can print image and looks cool
        embed = discord.Embed(
        title = f"History for **{display_name}**",
            color = discord.Color.blue()
       )

        embed.set_thumbnail(url=member.display_avatar.url)

        for event, time in events:
            time_str = str(time)
            time_str = time_str.split(".")[0]

            embed.add_field(name=f"{event[:1].upper() + event[1:]}", value=f"{time_str}", inline=False)

        await ctx.send(embed=embed)

# ---------- User Commands ----------
    # Removes table from database, then creates a new one
    @commands.command()
    async def resetUsersTable(self, ctx):
        self.db.resetUsersTable()
        await ctx.send("Users Table Reset")


    # Prints User Information
    @commands.command()
    async def userInfo(self, ctx, *username):
        if (len(username) == 0):
            await ctx.send("Usage: !messageTotal <username>")
            return
        
        member = ""

        # get member object if it exists
        try:
            member = await commands.MemberConverter().convert(ctx, username[0])
        except commands.errors.MemberNotFound:
            await ctx.send(f"**{username[0]}** could not be found in this server.")
            return

        info = self.db.getUserInfo(username[0])

        # make an embed cause it can print image and looks cool
        embed = discord.Embed(
            title = f"User Info: {info[1]}",
            color = discord.Color.blue()
        )

        embed.add_field(name="ID", value=info[0], inline=False)
        embed.add_field(name="Display Name", value=info[2], inline=False)
        embed.add_field(name="Join Date", value=info[3], inline=False)

        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)
