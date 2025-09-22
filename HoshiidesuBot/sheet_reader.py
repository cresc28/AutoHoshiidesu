import gspread
import discord
import os
import json
from discord.ext import commands
from discord import app_commands

class GSheetReader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_configs = {}
        sa_json_str = os.getenv("GOOGLE_SA_JSON")
        sa_info = json.loads(sa_json_str)
        self.client = gspread.service_account_from_dict(sa_info)

    async def get_sheet_rows(self, guild_id, round_type, spreadsheet_key):
        if guild_id in self.bot.sheet_cache and round_type in self.bot.sheet_cache[guild_id]:
            return self.bot.sheet_cache[guild_id][round_type]

        sh = self.client.open_by_key(spreadsheet_key)
        worksheet = sh.worksheet(round_type)
        all_rows = worksheet.get_all_values()

        if guild_id not in self.bot.sheet_cache:
            self.bot.sheet_cache[guild_id] = {}
        self.bot.sheet_cache[guild_id][round_type] = all_rows
        return all_rows

    @app_commands.command(name="update", description="キャッシュを更新")
    async def update_cache(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        spreadsheet_key = self.bot.spreadsheet_keys.get(guild_id)

        if not spreadsheet_key:
            await interaction.response.send_message("スプレッドシートキーが設定されていません", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        if guild_id not in self.bot.sheet_cache or not self.bot.sheet_cache[guild_id]:
            await interaction.followup.send(f"更新完了")
            return
    
        try:
            sh = self.client.open_by_key(spreadsheet_key)
            updated_sheets = []

            #キャッシュ更新
            for round_type in self.bot.sheet_cache[guild_id].keys():
                worksheet = sh.worksheet(round_type)
                all_rows = worksheet.get_all_values()
                self.bot.sheet_cache[guild_id][round_type] = all_rows
                updated_sheets.append(round_type)

            #ルール更新
            worksheet = sh.worksheet("設定")
            all_values = worksheet.get_all_values()
            guild_data = {}
            messages = []

            for row_index in range(1, 12):
                row = all_values[row_index]
                round = row[0]
                choice_col = None
                count = 0

                for col_index in range(1, 5):
                    if row[col_index].upper() == "TRUE":
                        choice_col = col_index #1・・・スキップ、2・・・既定枠、3・・・希望枠、4・・・全続行
                        count += 1

                if choice_col is None:
                    choice_col = 3
                choice = all_values[0][choice_col]

                old_choice = self.bot.round_choices.get(guild_id, {}).get(round)
                if old_choice != choice_col:
                    if count == 0:
                        messages.append(f'{round}: {choice} (未設定のためデフォルト)')
                    elif count > 1:
                        messages.append(f'{round}: {choice} (複数列にチェックが入っています)')
                    else:
                        messages.append(f'{round}: {choice}')

                guild_data[round] = choice_col

            self.bot.round_choices[guild_id] = guild_data

            if messages:
                 await interaction.channel.send("周回ルール:\n" + "\n".join(messages))

            await interaction.followup.send(f"更新完了")

        except Exception as e:
            await interaction.followup.send(f"更新に失敗しました", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        print("テスト1")
        voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)
        if voice_client is None:
            return
        
        guild_id = message.guild.id
        webhook_id = self.bot.webhook_ids.get(guild_id)
        print("テスト2")

        if message.webhook_id != webhook_id or message.webhook_id is None:
            return
        
        lines = message.content.splitlines()
        print("テスト3")

        if len(lines) < 2:
            return 

        round_type = lines[0].strip()
        terrors = lines[1].split()

        print("テスト4")

        channel = self.bot.text_channels.get(message.guild.id)
        guild_choices = self.bot.round_choices.get(guild_id, {})
        choice = guild_choices.get(round_type, None) #1・・・スキップ、2・・・既定枠、3・・・希望枠、4・・・全続行
        ALTERNATE_TERRORS_COUNT = 36

        print("テスト5")
        if choice is None:
            if guild_choices.get("オルタネイト", {}).get(round_type) is None:
                await channel.send("設定完了が押されていません")
            return

        if choice == 1: #スキップ選択されていれば何もしない
            return 
        
        if round_type == "ブラッドバス" or round_type == "ミッドナイト":
            terror_count = 3

        else:
            terror_count = 1

        if round_type == "ミッドナイト":
            tmp = terrors[0]
            terrors[0] = terrors[2] #オルタ枠を1番目に
            terrors[2] = tmp
            terrors[1] = str(int(terrors[1]) + ALTERNATE_TERRORS_COUNT)
            terrors[2] = str(int(terrors[2]) + ALTERNATE_TERRORS_COUNT)
        
        print("テスト6")
        try:
            spreadsheet_key = self.bot.spreadsheet_keys.get(guild_id)
            all_rows = await self.get_sheet_rows(guild_id, round_type, spreadsheet_key)
        except gspread.WorksheetNotFound:
            return
            
        names = all_rows[0]
        ids = all_rows[1]
        rows = all_rows[2:]
        requesters = set()
        requesters_midClassic = set()
        isContinue = True if choice == 4 else False

        def play_audio(file_name):
            source = discord.FFmpegPCMAudio(executable="ffmpeg", source=fr"audio/{file_name}")
            voice_client.play(source)

        print("テスト7")

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
                        if choice not in (3, 4):
                            continue #希望を受け付ける設定のときだけ

                        if round_type == "ミッドナイト":
                            (requesters if terror_num == 0 else requesters_midClassic).add(names[col])
                            
                        else:
                            requesters.add(names[col])
        
        print("テスト8")

        if not requesters and not requesters_midClassic:
            if isContinue:
                play_audio("zokkou.wav")

            else:
                play_audio("skip.wav")

        else:
            play_audio("hoshiidesu.wav")
            if round_type == "ミッドナイト":
                msg = []
                if requesters:
                    msg.append(f"オルタ枠希望者:\n{' '.join(requesters)}")
                if requesters_midClassic:
                    msg.append(f"クラシック枠希望者:\n{' '.join(requesters_midClassic)}")

                await channel.send('\n'.join(msg))

            else:
                await channel.send(f"希望者 :\n {" ".join(requesters)}")

async def setup(bot):
    await bot.add_cog(GSheetReader(bot))