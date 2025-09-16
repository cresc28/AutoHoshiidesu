from discord.ext import commands

class MemberManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_members = set()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        target_vc = member.guild.voice_client
        if target_vc is None:
            return

        if after.channel == target_vc:
            self.active_members.add(member.id)
        elif before.channel == target_vc and after.channel is None:
            self.active_members.discard(member.id)

    def get_members(self):
        return list(self.active_members)

async def setup(bot):
    await bot.add_cog(MemberManager(bot))