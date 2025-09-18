import gspread
import discord
from discord.ext import commands

class GSheetReader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = gspread.service_account(filename="sheet-reader.json")
        self.guild_configs = {}
        self.FFMPEG_PATH = r"C:\Users\cresc\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe"

    @commands.Cog.listener()
    async def on_message(self, message):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)
        if voice_client is None:
            return
        
        guild_id = message.guild.id
        webhook_id = self.bot.webhook_ids.get(guild_id)

        if message.webhook_id != webhook_id or message.webhook_id is None:
            return
        
        lines = message.content.splitlines()

        if len(lines) < 2:
            return 

        round_type = lines[0].strip()
        terrors = lines[1].split()

        channel = self.bot.text_channels.get(message.guild.id)
        guild_choices = self.bot.round_choices.get(guild_id, {})
        choice = guild_choices.get(round_type, None) #1・・・スキップ、2・・・既定枠、3・・・希望枠、4・・・全続行

        if choice is None:
            if guild_choices.get("オルタネイト", {}).get(round_type) is None:
                await channel.send("設定完了が押されていません")
            return

        if choice == 1: #スキップ選択されていれば何もしない
            return 
        
        if round_type == "ブラッドバス":
            terror_count = 3

        else:
            terror_count = 1

        if round_type == "ミッドナイト":
            tmp = terrors[0]
            terrors[0] = terrors[2] #オルタ枠を1番目に
            terrors[2] = tmp
        
        

        try:
            spreadsheet_key = self.bot.spreadsheet_keys.get(guild_id)
            sh = self.client.open_by_key(spreadsheet_key)
            worksheet = sh.worksheet(round_type)
        except gspread.WorksheetNotFound:
            return
            
        all_rows = worksheet.get_all_values()
        names = all_rows[0]
        ids = all_rows[1]
        rows = all_rows[2:]
        requesters = set()
        isContinue = True if choice == 4 else False

        def play_audio(file_name):
            source = discord.FFmpegPCMAudio(executable=self.FFMPEG_PATH, source=fr"audio\{file_name}")
            voice_client.play(source)

        for terror_num in range(terror_count):
            for row in rows:
                if row[0] != terrors[terror_num]:
                    continue

                for col, cell_value in enumerate(row):
                    if cell_value != "TRUE":
                        continue
                    
                    if ids[col].strip().lower() == "default":
                        if choice in (2, 3):
                            isContinue = True
                        continue

                    if int(ids[col]) in self.bot.active_members.get(guild_id, set()):
                        if choice in (3, 4): #希望を受け付ける設定のときだけ
                            requesters.add(names[col])

        if not requesters:
            if isContinue:
                play_audio("zokkou.wav" if round_type == "ミッドナイト" else "zokkouBut.wav")

            else:
                play_audio("skip.wav")

        else:
            play_audio("hoshiidesu.wav")
            await channel.send(f"希望者 :\n {" ".join(requesters)}")

async def setup(bot):
    await bot.add_cog(GSheetReader(bot))