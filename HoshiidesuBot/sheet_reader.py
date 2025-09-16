import gspread
from discord.ext import commands

class GSheetReader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = gspread.service_account(filename="sheet-reader.json")

    @commands.Cog.listener()
    async def on_message(self, message):
        webhook_id = getattr(self.bot, "webhook_id", None)
        spreadsheet_url = getattr(self.bot, "spreadsheet_url", None)

        if webhook_id is None or spreadsheet_url is None:
            await message.channel.send("WebhookID及びスプレッドシートURLを設定してください.")
            return

        if message.webhook_id != webhook_id:
            return
    
        lines = message.content.splitlines()

        if len(lines) < 2:
            return 

        round_type = lines[0].strip()
        terrors = lines[1].split()

        if round_type == "ブラッドバス":
            terror_count = 3

        else:
            terror_count = 1

        if round_type == "ミッドナイト":
            tmp = terrors[0]
            terrors[0] = terrors[2] #オルタ枠を1番目に
            terrors[2] = tmp

        try:
            sh = self.client.open_by_url(spreadsheet_url)
            worksheet = sh.worksheet(round_type)
            
            all_rows = worksheet.get_all_values()
            target_value = []

            for terror_num in range(terror_count):
                for row in all_rows:
                    if row[0] == terrors[terror_num]:
                        target_value.append(row[1])
                        break

            if not target_value:
                await message.channel.send("スキップ")
                return
            
        except Exception as e:
            return

        target_value_str = " ".join(target_value)
        await message.channel.send(f"{round_type} : {target_value_str}")

async def setup(bot):
    await bot.add_cog(GSheetReader(bot))