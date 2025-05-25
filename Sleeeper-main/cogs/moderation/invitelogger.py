import discord
from discord.ext import commands
from discord import app_commands
from utils import logging_get_channel
import logging
import asyncio

logger = logging.getLogger(__name__)

class InviteLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}
        self._invite_locks = {}

    async def cache_invites(self, guild: discord.Guild):
        try:
            self.invites[guild.id] = {invite.code: invite.uses for invite in await guild.invites()}
        except Exception as e:
            logger.warning(f"Failed to cache invites for guild {guild.id}: {e}")
            self.invites[guild.id] = {}

    def get_guild_lock(self, guild_id):
        if guild_id not in self._invite_locks:
            self._invite_locks[guild_id] = asyncio.Lock()
        return self._invite_locks[guild_id]

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
        lock = self.get_guild_lock(guild.id)
        async with lock:
            before_invites = self.invites.get(guild.id, {})
            try:
                after_invites = {invite.code: invite.uses for invite in await guild.invites()}
            except Exception as e:
                logger.warning(f"Failed to fetch invites on member join for guild {guild.id}: {e}")
                after_invites = {}

            used_invite = None
            for code, uses in after_invites.items():
                before_uses = before_invites.get(code, 0)
                if uses > before_uses:
                    used_invite = code
                    break

            self.invites[guild.id] = after_invites

            log_channel_id = logging_get_channel(guild)
            channel = None
            if isinstance(log_channel_id, dict) and isinstance(log_channel_id.get("channel"), int):
                channel = self.bot.get_channel(log_channel_id["channel"])

            if used_invite and channel:
                try:
                    invite_obj = await guild.fetch_invite(used_invite)
                    inviter = invite_obj.inviter
                    uses = invite_obj.uses
                    if inviter is None and invite_obj.code == getattr(guild, "vanity_url_code", None):
                        inviter = "Vanity URL"
                except Exception as e:
                    logger.warning(f"Failed to fetch invite object for code {used_invite} in guild {guild.id}: {e}")
                    inviter = None
                    uses = after_invites.get(used_invite, "?")

                embed = discord.Embed(
                    title="📨 Member Joined via Invite",
                    description=f"{member.mention} joined using invite `{used_invite}`.",
                    color=discord.Color.blue()
                )
                if inviter:
                    if inviter == "Vanity URL":
                        embed.add_field(name="Inviter", value="Vanity URL", inline=True)
                    else:
                        embed.add_field(name="Inviter", value=f"{inviter.mention} ({inviter})", inline=True)
                else:
                    embed.add_field(name="Inviter", value="Unknown", inline=True)
                embed.add_field(name="Times Used", value=str(uses), inline=True)
                embed.set_footer(text=f"User ID: {member.id}")
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    logger.warning(f"Failed to send invite log embed in guild {guild.id}: {e}")

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