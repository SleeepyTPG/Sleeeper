import discord
from discord.ext import commands
from discord.ui import View, Button

verify_roles = {}  # Dictionary to store verification roles for each guild

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user

        role_id = verify_roles.get(guild.id)
        if not role_id:
            await interaction.response.send_message(
                "❌ Verification role is not configured. Please contact an administrator.",
                ephemeral=True
            )
            return

        role = guild.get_role(role_id)
        if not role:
            role = await guild.create_role(name="Verified", reason="Verification role created by bot")
            verify_roles[guild.id] = role.id

        await member.add_roles(role)
        await interaction.response.send_message(
            f"✅ You have been verified and assigned the {role.mention} role!",
            ephemeral=True
        )

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_verify_role", description="Sets the role to be assigned upon verification.")
    @commands.has_permissions(administrator=True)
    async def set_verify_role(self, ctx, role: discord.Role):
        verify_roles[ctx.guild.id] = role.id
        await ctx.send(f"✅ Verification role has been set to {role.mention}.")
    
    @commands.command(name="send_verify", description="Sends the verification embed.")
    @commands.has_permissions(administrator=True)
    async def send_verify(self, ctx):
        embed = discord.Embed(
            title="✅ Verify Yourself",
            description="Click the **Verify** button below to verify yourself and gain access to the server.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Verification System")
        await ctx.send(embed=embed, view=VerifyView())

async def setup(bot):
    await bot.add_cog(Verify(bot))