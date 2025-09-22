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
        print("テスト1")
        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        print("テスト1.1")

        if vc:
            if vc.channel == channel:
                await interaction.response.send_message("すでに接続済みです")
                return
            else:
                await vc.move_to(channel)
        else:
            await channel.connect()

        print("テスト1.2")
        members = self.bot.active_members.setdefault(interaction.guild.id, set())
        print("テスト1.3")
        for member in channel.members:
            if not member.bot:
                members.add(member.id)
        print("テスト2")
        self.bot.text_channels[interaction.guild.id] = interaction.channel
        view = ConfigPage1(self.bot, interaction.guild.id)
        print("テスト3")
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
