import discord
import re
from discord import Interaction
from save_config import save_config, load_config

#discordのGUIよくわからん
class ConfigPage1(discord.ui.View):
    def __init__(self, bot, guild_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id

        load_config(self.bot, guild_id)

        self.embed = discord.Embed(title="設定")
        self.embed.add_field(
            name="Webhook ID(TerrorLogger出力先)",
            value=str(self.bot.webhook_ids.get(guild_id, "未設定")),
            inline=False
        )
        self.embed.add_field(
            name="スプレッドシートKey",
            value=self.bot.spreadsheet_keys.get(guild_id, "未設定"),
            inline=False
        )

    @discord.ui.button(label="TerrorLogger出力先のWebhookURL", style=discord.ButtonStyle.primary)
    async def webhook_button(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetWebhookModal(self.bot, self.guild_id))

    @discord.ui.button(label="スプレッドシートURL", style=discord.ButtonStyle.primary)
    async def sheet_button(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetSpreadsheetModal(self.bot, self.guild_id))

    @discord.ui.button(label="完了", style=discord.ButtonStyle.success)
    async def finish(self, interaction: Interaction, button: discord.ui.Button):
        guild_id = self.guild_id
        if self.bot.webhook_ids.get(guild_id) is None or self.bot.spreadsheet_keys.get(guild_id) is None:
            await interaction.response.send_message("WebhookURLまたはスプレッドシートURLが未設定です", ephemeral=True)
            return
        
        save_config(self.bot, guild_id)
        
        try:
            await interaction.message.delete()
        except Exception as e:
            pass
        
        await interaction.response.send_message("設定完了", ephemeral=True)
        await self.load_round_settings(guild_id, interaction.channel)
        
        self.stop()

    async def load_round_settings(self, guild_id: int, channel: discord.TextChannel):
        key = self.bot.spreadsheet_keys.get(guild_id)

        if key is None:
            return

        import gspread
        client = gspread.service_account(filename="sheet-reader.json")
        try:
            sh = client.open_by_key(key)
            worksheet = sh.worksheet("設定")
            all_values = worksheet.get_all_values()
            guild_data = {}
            messages = []
            round_types_to_load = []

            for row_index in range(1,12):
                row = all_values[row_index]
                round_type = row[0]
                count = 0
                choice_col = None #1・・・スキップ、2・・・既定枠、3・・・希望枠、4・・・全続行

                for col_index in range(1,5):
                    if row[col_index].upper() == "TRUE":
                        choice_col = col_index
                        count+=1

                if choice_col is None:
                    choice_col = 3

                choice = all_values[0][choice_col]
                guild_data[round_type] = choice_col

                if choice_col != 1:
                    round_types_to_load.append(round_type)  # 後で読み込む

                if count == 0:
                    messages.append(f'{round_type}: {choice} (未設定のためデフォルト)')
                elif count > 1:
                    messages.append(f'{round_type}: {choice} (複数列にチェックが入っています)')
                else:
                    messages.append(f'{round_type}: {choice}')

            self.bot.round_choices[guild_id] = guild_data
            await channel.send("周回ルール:\n" + "\n".join(messages))

            for round_type in round_types_to_load:
                try:
                    round_ws = sh.worksheet(round_type)
                    all_rows = round_ws.get_all_values()
                    if guild_id not in self.bot.sheet_cache:
                        self.bot.sheet_cache[guild_id] = {}
                    self.bot.sheet_cache[guild_id][round_type] = all_rows
                except gspread.WorksheetNotFound:
                    pass
            
        except Exception as e:
            print(f"シート読み込みに失敗:", e)

class SetWebhookModal(discord.ui.Modal, title="WebhookIDを設定"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
        self.webhook_input = discord.ui.TextInput(
            label="TerrorLogger出力先のWebhookURL",
            placeholder="WebhookURLを入力",
            required=True
        )
        self.add_item(self.webhook_input)

    async def on_submit(self, interaction: Interaction):
        import re
        raw = self.webhook_input.value
        match = re.search(r'/(\d+)/', raw)
        if match:
            self.bot.webhook_ids[self.guild_id] = int(match.group(1))
        else:
            self.bot.webhook_ids[self.guild_id] = int(raw)
        await interaction.response.send_message(f"WebhookID: {self.bot.webhook_ids[self.guild_id]}",ephemeral=True)


class SetSpreadsheetModal(discord.ui.Modal, title="スプレッドシートURL"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
        self.sheet_input = discord.ui.TextInput(
            label="スプレッドシートURL",
            placeholder="URLを入力",
            required=True
        )
        self.add_item(self.sheet_input)

    async def on_submit(self, interaction: Interaction):
        url = self.sheet_input.value
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if not match:
            await interaction.response.send_message("無効なURLです", ephemeral=True)
            return
        
        key = match.group(1)
        self.bot.spreadsheet_keys[self.guild_id] = key

        await interaction.response.send_message(f"スプレッドシートID: {self.bot.spreadsheet_keys[self.guild_id]}", ephemeral=True)