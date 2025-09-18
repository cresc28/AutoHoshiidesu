from discord.ext import commands

class MemberManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_guild_members(self, guild_id):
        if guild_id not in self.bot.active_members:
            self.bot.active_members[guild_id] = set()
        return self.bot.active_members[guild_id]

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        guild_id = member.guild.id
        members = self.get_guild_members(guild_id)
        target_vc = member.guild.voice_client.channel if member.guild.voice_client else None

        if target_vc is None:
            return

        if after.channel == target_vc:
            members.add(member.id)
        elif before.channel == target_vc and after.channel is None:
            members.discard(member.id)

async def setup(bot):
    await bot.add_cog(MemberManager(bot))