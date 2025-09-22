import discord
from discord.ext import commands
import os
import sys
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

bot.webhook_ids = {} 
bot.spreadsheet_keys = {}
bot.active_members = {}
bot.round_choices = {}
bot.text_channels = {}
bot.sheet_cache = {}  # {guild_id: {round_type: all_rows}}

async def restart_checker():
    JST = ZoneInfo("Asia/Tokyo")
    while True:
        now = datetime.now(JST)
        next_restart = datetime.combine(now.date(), time(3, 0), tzinfo=JST)
        if now >= next_restart:
            next_restart += timedelta(days=1)
        wait_seconds = (next_restart - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        sys.exit(1)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

async def load_extensions():
    await bot.load_extension("sheet_reader")
    await bot.load_extension("member_manager")
    await bot.load_extension("vc_commands")

async def main():
    async with bot:
        await load_extensions()
        asyncio.create_task(restart_checker())
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())