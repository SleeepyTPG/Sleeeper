import discord
from discord.ext import commands

WELCOME_CHANNEL_ID = 1366982809562120242

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_message = (
            "👋 Welcome {member} to **{guild}**!\n"
            "You are our {member_count}th member!\n"
            "Please look into <#1372516055188246588> for your Roles"
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            msg = self.welcome_message.format(
                member=member.mention,
                guild=member.guild.name,
                member_count=member.guild.member_count
            )
            await channel.send(msg)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, *, message: str):
        self.welcome_message = message
        await ctx.send("Welcome message updated!")

async def setup(bot):
    await bot.add_cog(Welcomer(bot))