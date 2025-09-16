import discord
from discord import app_commands
from discord.ext import commands

TOKEN = ''

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

async def load_extensions():
    await bot.load_extension("sheet_reader")
    await bot.load_extension("member_manager")
    await bot.load_extension("commands")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())