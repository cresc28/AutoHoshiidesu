import discord
from discord import app_commands, Interaction
from discord.ext import commands
from setup_ui import ConfigPage1

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, "active_members"):
            bot.active_members = {} 

    def get_guild_members(self, guild_id):
        if guild_id not in self.bot.active_members:
            self.bot.active_members[guild_id] = set()
        return self.bot.active_members[guild_id]

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
            await channel.connect()

        members = self.get_guild_members(interaction.guild.id)
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

    @app_commands.command(name="add", description="メンバー追加")
    async def add_member(self, interaction: discord.Interaction, user: discord.Member):
        members = self.get_guild_members(interaction.guild.id)
        members.add(user.id)
        await interaction.response.send_message(f"{user.display_name}を登録しました")


    @app_commands.command(name="remove", description="メンバー削除")
    async def remove_member(self, interaction: discord.Interaction, user: discord.Member):
        members = self.get_guild_members(interaction.guild.id)
        if user.id in members:
            members.discard(user.id)
            await interaction.response.send_message(f"{user.display_name}を削除しました")
        else:
            await interaction.response.send_message(f"{user.display_name}は登録されていません")

    @app_commands.command(name="list", description="登録メンバー表示")
    async def list(self, interaction: discord.Interaction):
        members = self.get_guild_members(interaction.guild.id)

        if not members:
            await interaction.response.send_message("現在メンバーは登録されていません")
            return

        names = []
        for member_id in members:
            member = interaction.guild.get_member(member_id)
            if member:
                names.append(member.display_name)

        await interaction.response.send_message(f"登録メンバー: {', '.join(names)}")

async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
