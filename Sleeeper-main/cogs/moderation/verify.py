import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from utils import verify_set_role, verify_get_role
import random
import string


class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user

        role_id = verify_get_role(guild).get("role")
        if not role_id:
            await interaction.response.send_message(
                "❌ Verification role is not configured. Please contact an administrator.",
                ephemeral=True
            )
            return

        role = guild.get_role(role_id)
        if not role:
            role = await guild.create_role(name="Verified", reason="Verification role created by bot")
            verify_set_role(role, guild)

        captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        await interaction.response.send_message(
            f"🛡️ Please complete the CAPTCHA to verify yourself:\n\n`{captcha}`\n\nType the CAPTCHA in this channel.",
            ephemeral=True
        )

        def check(msg):
            return msg.author == member and msg.channel == interaction.channel and msg.content == captcha

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ CAPTCHA verification failed. Please try again.", ephemeral=True)
            return

        await member.add_roles(role)
        await interaction.followup.send(
            f"✅ You have been verified and assigned the {role.mention} role!",
            ephemeral=True
        )


class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="set_verify_role", description="Sets the role to be assigned upon verification.")
    @commands.has_permissions(administrator=True)
    async def _set_verify_role(self, itx: discord.Interaction, role: discord.Role):
        verify_set_role(role, itx.guild)
        await itx.response.send_message(f"✅ Verification role has been set to {role.mention}.")
    
    @app_commands.command(name="send_verify", description="Sends the verification embed.")
    @commands.has_permissions(administrator=True)
    async def _send_verify(self, itx: discord.Interaction):
        embed = discord.Embed(
            title="✅ Verify Yourself",
            description="Click the **Verify** button below to verify yourself and gain access to the server.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Verification System")
        await itx.channel.send(embed=embed, view=VerifyView())
        await itx.response.send_message("Ok, sent 👌", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))
