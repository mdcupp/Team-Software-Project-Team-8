# Imports
import discord
from discord.ext import commands
import os
import asyncio
import sqlite3

# Registers the intents (permissions) that the bot has access to
intents = discord.Intents.default()
intents.message_content = True

#Creates bot with prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

#Connect to the database
con = sqlite3.connect("database.db")
cursor = con.cursor()

#On every message sent
@bot.event
async def on_message(message):
    # Don't scan your own message
    if message.author == bot.user:
        return
    
    author_name = str(message.author)
    content = message.content


    cursor.execute("INSERT INTO messages VALUES(?, ?);", (author_name, content))
    con.commit()  

    # Go check commands after    
    await bot.process_commands(message)

#Commands
# Test command to make sure bot is running
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Command to print other commands
@bot.command()
async def helpMe(ctx):
    await ctx.send("!helpMe - List Commands")
    await ctx.send("!ping - Test Command")
    await ctx.send("!createTable - Deletes and Creates Messages Table")
    await ctx.send("!getMessageCount - Prints message count recorded from user")

# Removes table from database, then creates a new one
@bot.command()
async def createTable(ctx):
    cursor.execute("DROP TABLE IF EXISTS messages;")
    cursor.execute("CREATE TABLE IF NOT EXISTS messages(author, message);")
    await ctx.send("Table Created")


# Prints message count from user
@bot.command()
async def getMessageCount(ctx):
    author_name = str(ctx.author)
    result = cursor.execute("SELECT COUNT(*) FROM messages WHERE author = ?;", (author_name,))
    result = cursor.fetchone() 
    
    count = result[0] if result else 0
    
    await ctx.send(f"{author_name} has recorded {count} messages.")

#Main Function
async def main():
    async with bot:
        await bot.start("DISCORD API KEY - DO NOT COMMIT")

asyncio.run(main())
