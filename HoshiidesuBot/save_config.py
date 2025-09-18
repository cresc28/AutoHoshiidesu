import json
import os

CONFIG_FILE = "config.json"

def save_config(bot, guild_id):
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
    
    data[str(guild_id)] = {
        "webhook_id": bot.webhook_ids.get(guild_id),
        "spreadsheet_key": bot.spreadsheet_keys.get(guild_id)
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_config(bot, guild_id):
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            guild_data = data.get(str(guild_id), {})
            bot.webhook_ids[guild_id] = guild_data.get("webhook_id")
            bot.spreadsheet_keys[guild_id] = guild_data.get("spreadsheet_key")
