import discord
from discord.ext import commands
from discord import app_commands
import aiomysql

MARRIAGE_TABLE = "marriages"
ADOPTION_TABLE = "adoptions"

async def ensure_family_tables_exist(bot):
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {MARRIAGE_TABLE} (
                    member1 BIGINT NOT NULL,
                    member2 BIGINT NOT NULL,
                    PRIMARY KEY (member1, member2)
                )
            """)
            await cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {ADOPTION_TABLE} (
                    adopter BIGINT NOT NULL,
                    adoptee BIGINT NOT NULL,
                    PRIMARY KEY (adopter, adoptee)
                )
            """)

async def get_mysql_pool(bot):
    return await bot.get_mysql_pool()

async def marry_add_user(bot, member1: discord.Member, member2: discord.Member):
    await ensure_family_tables_exist(bot)
    pool = await get_mysql_pool(bot)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"INSERT INTO {MARRIAGE_TABLE} (member1, member2) VALUES (%s, %s)",
                (member1.id, member2.id)
            )


async def marry_get_user(bot, member: discord.Member):
    await ensure_family_tables_exist(bot)
    pool = await get_mysql_pool(bot)
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"SELECT * FROM {MARRIAGE_TABLE} WHERE member1=%s OR member2=%s",
                (member.id, member.id)
            )
            return await cur.fetchone()


async def marry_remove_user(bot, member: discord.Member):
    await ensure_family_tables_exist(bot)
    pool = await get_mysql_pool(bot)
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"SELECT * FROM {MARRIAGE_TABLE} WHERE member1=%s OR member2=%s",
                (member.id, member.id)
            )
            result = await cur.fetchone()
            await cur.execute(
                f"DELETE FROM {MARRIAGE_TABLE} WHERE member1=%s OR member2=%s",
                (member.id, member.id)
            )
            return result


async def adopt_user(bot, adopter: discord.Member, adoptee: discord.Member):
    await ensure_family_tables_exist(bot)
    pool = await get_mysql_pool(bot)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"INSERT INTO {ADOPTION_TABLE} (adopter, adoptee) VALUES (%s, %s)",
                (adopter.id, adoptee.id)
            )


async def get_adoption_data(bot, member: discord.Member):
    await ensure_family_tables_exist(bot)
    pool = await get_mysql_pool(bot)
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"SELECT * FROM {ADOPTION_TABLE} WHERE adopter=%s OR adoptee=%s",
                (member.id, member.id)
            )
            return await cur.fetchone()


async def remove_adoption(bot, member: discord.Member):
    await ensure_family_tables_exist(bot)
    pool = await get_mysql_pool(bot)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"DELETE FROM {ADOPTION_TABLE} WHERE adopter=%s OR adoptee=%s",
                (member.id, member.id)
            )

class ProposalView(discord.ui.View):
    def __init__(self, bot, proposer: discord.Member, proposee: discord.Member):
        super().__init__(timeout=360)
        self.bot = bot
        self.proposer = proposer
        self.proposee = proposee
        self.result = None

    @discord.ui.button(label="Accept 💍", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.proposee:
            await interaction.response.send_message("❌ This proposal is not for you!", ephemeral=True)
            return

        await marry_add_user(self.bot, self.proposer, self.proposee)

        embed = discord.Embed(
            title="💍 Marriage Accepted!",
            description=f"{self.proposee.mention} has accepted {self.proposer.mention}'s proposal! 🎉",
            color=discord.Color.green()
        )
        embed.set_footer(text="Congratulations on your marriage!")
        await interaction.response.edit_message(embed=embed, view=None)
        self.result = "accepted"
        self.stop()

    @discord.ui.button(label="Decline 💔", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.proposee:
            await interaction.response.send_message("❌ This proposal is not for you!", ephemeral=True)
            return

        embed = discord.Embed(
            title="💔 Proposal Declined",
            description=f"{self.proposee.mention} has declined {self.proposer.mention}'s proposal. 😢",
            color=discord.Color.red()
        )
        embed.set_footer(text="Better luck next time!")
        await interaction.response.edit_message(embed=embed, view=None)
        self.result = "declined"
        self.stop()


class AdoptionView(discord.ui.View):
    def __init__(self, bot, adopter: discord.Member, adoptee: discord.Member):
        super().__init__(timeout=360)
        self.bot = bot
        self.adopter = adopter
        self.adoptee = adoptee
        self.result = None

    @discord.ui.button(label="Accept 👪", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.adoptee:
            await interaction.response.send_message("❌ This adoption request is not for you!", ephemeral=True)
            return

        await adopt_user(self.bot, self.adopter, self.adoptee)

        embed = discord.Embed(
            title="👪 Adoption Accepted!",
            description=f"{self.adoptee.mention} has been adopted by {self.adopter.mention}! 🎉",
            color=discord.Color.green()
        )
        embed.set_footer(text="Congratulations on your new family!")
        await interaction.response.edit_message(embed=embed, view=None)
        self.result = "accepted"
        self.stop()

    @discord.ui.button(label="Decline 💔", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.adoptee:
            await interaction.response.send_message("❌ This adoption request is not for you!", ephemeral=True)
            return

        embed = discord.Embed(
            title="💔 Adoption Declined",
            description=f"{self.adoptee.mention} has declined {self.adopter.mention}'s adoption request. 😢",
            color=discord.Color.red()
        )
        embed.set_footer(text="Better luck next time!")
        await interaction.response.edit_message(embed=embed, view=None)
        self.result = "declined"
        self.stop()
        
class Marry(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="marry", description="Propose to another user!")
    @app_commands.describe(user="The user you want to marry")
    async def _marry(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild only command!", ephemeral=True)

        if user.id == interaction.user.id:
            return await interaction.response.send_message("💔 You can't marry yourself!", ephemeral=True)
        
        if user.bot:   
            return await interaction.response.send_message("💔 You can't marry a bot!", ephemeral=True)
        
        member = interaction.user
        if not isinstance(member, discord.Member):
            member = interaction.guild.get_member(member.id)
        if member is None:
            await interaction.response.send_message("❌ Could not find your member data in this guild.", ephemeral=True)
            return
        self_married = await marry_get_user(self.bot, member)
        other_married = await marry_get_user(self.bot, user)

        if self_married:
            await interaction.response.send_message("💔 You are already married! Divorce first to marry someone else.", ephemeral=True)
            return

        if other_married:
            await interaction.response.send_message(f"💔 {user.mention} is already married to someone else!", ephemeral=True)
            return

        embed = discord.Embed(
            title="💍 Marriage Proposal",
            description=f"{interaction.user.mention} has proposed to {user.mention}! 💕\n\n{user.mention}, do you accept?",
            color=discord.Color.pink()
        )
        embed.set_footer(text="You have 6 Minutes to respond.")

        proposer_member = interaction.user
        if not isinstance(proposer_member, discord.Member):
            proposer_member = interaction.guild.get_member(proposer_member.id)
        if proposer_member is None:
            await interaction.response.send_message("❌ Could not find your member data in this guild.", ephemeral=True)
            return
        view = ProposalView(self.bot, proposer=proposer_member, proposee=user)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="divorce", description="Divorce your current partner.")
    async def _divorce(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild only command!", ephemeral=True)

        member = interaction.user
        if not isinstance(member, discord.Member):
            member = interaction.guild.get_member(member.id)
        if member is None:
            await interaction.response.send_message("❌ Could not find your member data in this guild.", ephemeral=True)
            return
        marriage = await marry_get_user(self.bot, member)
        if not marriage:
            await interaction.response.send_message("💔 You are not married to anyone!", ephemeral=True)
            return

        result = await marry_remove_user(self.bot, member)

        if not result:
            await interaction.response.send_message("❌ Failed to process your divorce. Please try again.", ephemeral=True)
            return

        partner_id = result["member1"] if result["member1"] != interaction.user.id else result["member2"]

        embed = discord.Embed(
            title="💔 Divorce",
            description=f"{interaction.user.mention} has divorced <@{partner_id}>. 😢",
            color=discord.Color.red()
        )
        embed.set_footer(text="We hope you find happiness again.")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="adopt", description="Adopt another user!")
    @app_commands.describe(user="The user you want to adopt")
    async def _adopt(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild-only command!", ephemeral=True)

        if user.id == interaction.user.id:
            return await interaction.response.send_message("❌ You can't adopt yourself!", ephemeral=True)

        if user.bot:
            return await interaction.response.send_message("❌ You can't adopt a bot!", ephemeral=True)

        adoption_data = await get_adoption_data(self.bot, user)
        if adoption_data:
            await interaction.response.send_message(f"❌ {user.mention} is already adopted by someone else!", ephemeral=True)
            return

        embed = discord.Embed(
            title="👪 Adoption Request",
            description=f"{interaction.user.mention} wants to adopt {user.mention}! 💕\n\n{user.mention}, do you accept?",
            color=discord.Color.pink()
        )
        embed.set_footer(text="You have 6 minutes to respond.")

        adopter_member = interaction.user
        if not isinstance(adopter_member, discord.Member):
            adopter_member = interaction.guild.get_member(adopter_member.id)
        if adopter_member is None:
            await interaction.response.send_message("❌ Could not find your member data in this guild.", ephemeral=True)
            return
        view = AdoptionView(self.bot, adopter=adopter_member, adoptee=user)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="runaway", description="Run away from your current adopter.")
    async def _runaway(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild-only command!", ephemeral=True)

        member = interaction.user
        if not isinstance(member, discord.Member):
            member = interaction.guild.get_member(member.id)
        if member is None:
            await interaction.response.send_message("❌ Could not find your member data in this guild.", ephemeral=True)
            return

        adoption_data = await get_adoption_data(self.bot, member)
        if not adoption_data:
            await interaction.response.send_message("❌ You are not adopted by anyone!", ephemeral=True)
            return

        adopter_id = adoption_data["adopter"]
        await remove_adoption(self.bot, member)

        embed = discord.Embed(
            title="🏃 Runaway",
            description=f"{interaction.user.mention} has run away from their adopter (<@{adopter_id}>). 😢",
            color=discord.Color.red()
        )
        embed.set_footer(text="We hope you find happiness again.")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Marry(bot))
