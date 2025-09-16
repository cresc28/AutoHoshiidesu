import discord
from discord import app_commands, Interaction
from discord.ext import commands
from setup_ui import ConfigPage1

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="config", description="ボット設定画面を開く")
    async def config(self, interaction: Interaction):
        embed = discord.Embed(
            title="設定ページ 1/2",
            description="WebhookID と スプレッドシートURL を入力してください"
        )
        view = ConfigPage1(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="join", description="VCに接続")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice is None:
            await interaction.response.send_message("VC接続後に入力してください")
            return

        channel = interaction.user.voice.channel

        if interaction.guild.voice_client is not None:
            if interaction.guild.voice_client.channel == channel:
                await interaction.response.send_message("すでに接続済みです")
                return
            else:
                await interaction.guild.voice_client.move_to(channel)
                await interaction.response.send_message(f"{channel}に接続しました")
        else:
            await channel.connect()
            await interaction.response.send_message(f"{channel}に接続しました")

    @app_commands.command(name="leave", description="VCから切断")
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            await interaction.response.send_message("VCに接続されていません")
            return
        else:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("切断しました")

    @app_commands.command(name="add", description="メンバー追加")
    async def add_member(self, interaction: discord.Interaction, user: discord.Member):
        manager = self.bot.get_cog("MemberManager")
        if manager is None:
            return

        manager.active_members.add(user.id)
        await interaction.response.send_message(f"{user.display_name}を登録しました")

    @app_commands.command(name="remove", description="メンバー削除")
    async def remove_member(self, interaction: discord.Interaction, user: discord.Member):
        manager = self.bot.get_cog("MemberManager")
        if manager is None:
            return

        if user.id in manager.active_members:
            manager.active_members.discard(user.id)
            await interaction.response.send_message(f"{user.display_name}を削除しました")
        else:
            await interaction.response.send_message(f"{user.display_name}は登録されていません")

    @app_commands.command(name="list", description="登録メンバー表示")
    async def list(self, interaction: discord.Interaction):
        manager = self.bot.get_cog("MemberManager")

        if manager is None:
            return
        
        members = manager.get_members()

        if not members:
            await interaction.response.send_message("現在メンバーは登録されていません")
            return

        else:
            names = []
            for member_id in members:
                member = interaction.guild.get_member(member_id)
                if member:
                    names.append(member.display_name)
            await interaction.response.send_message(f"登録メンバー: {', '.join(names)}")
            return

async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
