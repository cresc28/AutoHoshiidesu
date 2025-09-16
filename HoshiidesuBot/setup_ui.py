import discord
from discord import Interaction

class ConfigPage1(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="WebhookIDまたはURLを入力", style=discord.ButtonStyle.primary)
    async def webhook_button(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetWebhookModal(self.bot))

    @discord.ui.button(label="スプレッドシートURLを入力", style=discord.ButtonStyle.primary)
    async def sheet_button(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetSpreadsheetModal(self.bot))

    @discord.ui.button(label="完了", style=discord.ButtonStyle.success)
    async def finish(self, interaction: Interaction, button: discord.ui.Button):
        if getattr(self.bot, "webhook_id", None) is None or getattr(self.bot, "spreadsheet_url", None) is None:
            await interaction.response.send_message("WebhookIDまたはスプレッドシートURLが未設定です", ephemeral=True)
            return

        await interaction.response.send_message(f"設定完了", ephemeral=True)
        self.stop()

class SetWebhookModal(discord.ui.Modal, title="WebhookIDを設定"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.webhook_input = discord.ui.TextInput(label="WebhookIDまたはURL", placeholder="WebhookIDまたはURLを入力", required=True)
        self.add_item(self.webhook_input)

    async def on_submit(self, interaction: Interaction):
        import re
        raw = self.webhook_input.value
        match = re.search(r'/(\d+)/', raw)
        if match:
            self.bot.webhook_id = int(match.group(1))
        else:
            self.bot.webhook_id = int(raw)
        await interaction.response.send_message(f"WebhookIDを`{self.bot.webhook_id}`に設定しました", ephemeral=True)


class SetSpreadsheetModal(discord.ui.Modal, title="スプレッドシートURLを設定"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.sheet_input = discord.ui.TextInput(label="スプレッドシートURL", placeholder="URLを入力", required=True)
        self.add_item(self.sheet_input)

    async def on_submit(self, interaction: Interaction):
        url = self.sheet_input.value
        if "/edit" in url:
            base_url = url.split("/edit")[0] + "/edit"
        else:
            base_url = url
        self.bot.spreadsheet_url = base_url
        await interaction.response.send_message(f"スプレッドシートURLを設定しました: {self.bot.spreadsheet_url}", ephemeral=True)