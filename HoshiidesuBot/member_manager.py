import discord
from discord.ext import commands
from discord import app_commands

class MemberManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add", description="メンバー追加")
    async def add_member(self, interaction: discord.Interaction, user: discord.Member):
        members = self.bot.active_members.setdefault(interaction.guild.id, set())
        members.add(user.id)
        await interaction.response.send_message(f"{user.display_name}を登録しました")

    @app_commands.command(name="remove", description="メンバー削除")
    async def remove_member(self, interaction: discord.Interaction, user: discord.Member):
        members = self.bot.active_members.setdefault(interaction.guild.id, set())
        if user.id in members:
            members.discard(user.id)
            await interaction.response.send_message(f"{user.display_name}を削除しました")
        else:
            await interaction.response.send_message(f"{user.display_name}は登録されていません")

    @app_commands.command(name="list", description="登録メンバー表示")
    async def list(self, interaction: discord.Interaction):
        members = self.bot.active_members.setdefault(interaction.guild.id, set())
        if not members:
            await interaction.response.send_message("現在メンバーは登録されていません")
            return
        names = []
        for member_id in members:
            member = interaction.guild.get_member(member_id)
            if member:
                names.append(member.display_name)

        await interaction.response.send_message(f"登録メンバー: {', '.join(names)}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        members = self.bot.active_members.setdefault(member.guild.id, set())
        target_vc = member.guild.voice_client.channel if member.guild.voice_client else None

        if target_vc is None:
            return

        if after.channel == target_vc:
            members.add(member.id)
        elif before.channel == target_vc and after.channel != target_vc:
            members.discard(member.id)

async def setup(bot):
    await bot.add_cog(MemberManager(bot))