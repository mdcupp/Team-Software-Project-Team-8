# Imports
import discord
from discord.ext import commands
import asyncio
from database.database import Database

# Registers the intents (permissions) that the bot has access to
intents = discord.Intents.default()
intents.message_content = True

# Creates bot with prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Connect to the database
db = Database()

# Load in all the cog files
async def loadExtensions():
    from cogs.commands import Commands
    await bot.add_cog(Commands(bot, db))

    from cogs.tracker import Tracker
    await bot.add_cog(Tracker(bot, db))

# Main Function
async def main():
    async with bot:
        await loadExtensions()
        await bot.start("INSERT API KEY")

# Run the main functino
asyncio.run(main())
