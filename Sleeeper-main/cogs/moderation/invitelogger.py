import discord
from discord.ext import commands
from discord import app_commands
from utils import logging_get_channel

class InviteLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}

    async def cache_invites(self, guild: discord.Guild):
        try:
            self.invites[guild.id] = {invite.code: invite.uses for invite in await guild.invites()}
        except Exception:
            self.invites[guild.id] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self.cache_invites(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.cache_invites(guild)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.cache_invites(invite.guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.cache_invites(invite.guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        before_invites = self.invites.get(guild.id, {})
        try:
            after_invites = {invite.code: invite.uses for invite in await guild.invites()}
        except Exception:
            after_invites = {}

        used_invite = None
        for code, uses in after_invites.items():
            if code in before_invites and uses > before_invites[code]:
                used_invite = code
                break

        self.invites[guild.id] = after_invites

        log_channel_id = logging_get_channel(guild)
        channel = None
        if log_channel_id and isinstance(log_channel_id.get("channel"), int):
            channel = self.bot.get_channel(log_channel_id["channel"])

        if used_invite and channel:
            try:
                invite_obj = await guild.fetch_invite(used_invite)
                inviter = invite_obj.inviter
                uses = invite_obj.uses
            except Exception:
                inviter = None
                uses = after_invites.get(used_invite, "?")

            embed = discord.Embed(
                title="📨 Member Joined via Invite",
                description=f"{member.mention} joined using invite `{used_invite}`.",
                color=discord.Color.blue()
            )
            if inviter:
                embed.add_field(name="Inviter", value=f"{inviter.mention} ({inviter})", inline=True)
            else:
                embed.add_field(name="Inviter", value="Unknown", inline=True)
            embed.add_field(name="Times Used", value=str(uses), inline=True)
            embed.set_footer(text=f"User ID: {member.id}")
            await channel.send(embed=embed)

    @app_commands.command(name="refresh_invites", description="Refresh the invite cache for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def refresh_invites(self, interaction: discord.Interaction):
        if interaction.guild is not None:
            await self.cache_invites(interaction.guild)
            await interaction.response.send_message("✅ Invite cache refreshed.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(InviteLogger(bot))