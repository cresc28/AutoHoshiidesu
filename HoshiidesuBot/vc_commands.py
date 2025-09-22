import discord
from discord import app_commands, Interaction
from discord.ext import commands
from setup_ui import ConfigPage1

class VcCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="config", description="設定画面を開く")
    async def config(self, interaction: Interaction):
        view = ConfigPage1(self.bot, interaction.guild.id)
        await interaction.response.send_message(embed=view.embed, view=view, ephemeral=True)
    
    @app_commands.command(name="join", description="VCに接続")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice is None:
            await interaction.response.send_message("VC接続後に入力してください")
            return
        
        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc:
            if vc.channel == channel:
                await interaction.response.send_message("すでに接続済みです")
                return
            else:
                await vc.move_to(channel)
        else:
            try:
                print("VC接続開始", flush=True)
                await channel.connect()
                print("VC接続成功", flush=True)
            except discord.errors.Forbidden as e:
                print("VC接続エラー: 権限不足 (Forbidden)", e, flush=True)
                await interaction.followup.send("VC接続に必要な権限がありません", ephemeral=True)
            except discord.errors.ClientException as e:
                print("VC接続エラー: ClientException", e, flush=True)
                await interaction.followup.send("VC接続に失敗しました (ClientException)", ephemeral=True)
            except Exception as e:
                print("VC接続エラー: その他", e, flush=True)
                await interaction.followup.send(f"VC接続に失敗しました: {e}", ephemeral=True)


        members = self.bot.active_members.setdefault(interaction.guild.id, set())
        for member in channel.members:
            if not member.bot:
                members.add(member.id)
        self.bot.text_channels[interaction.guild.id] = interaction.channel
        view = ConfigPage1(self.bot, interaction.guild.id)
        await interaction.response.send_message(content=f"{channel}に接続しました", embed=view.embed, view=view, ephemeral=True)

    @app_commands.command(name="leave", description="VCから切断")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("VCに接続されていません")
            return
        
        await vc.disconnect()
        await interaction.response.send_message("切断しました")

async def setup(bot):
    await bot.add_cog(VcCommandsCog(bot))
