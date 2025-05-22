import discord
from discord.ext import commands
from discord import app_commands
import aiomysql

LEVEL_TABLE = "levels"
LEVEL_CHANNELS_TABLE = "level_channels"

async def ensure_tables_exist(bot):
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {LEVEL_TABLE} (
                    user_id BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    xp INT NOT NULL DEFAULT 0,
                    level INT NOT NULL DEFAULT 1,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            await cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {LEVEL_CHANNELS_TABLE} (
                    guild_id BIGINT PRIMARY KEY,
                    channel BIGINT NOT NULL
                )
            """)

async def level_add_xp(bot, member: discord.Member, guild: discord.Guild, xp: int):
    await ensure_tables_exist(bot)
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"SELECT * FROM {LEVEL_TABLE} WHERE user_id=%s AND guild_id=%s",
                (member.id, guild.id)
            )
            row = await cur.fetchone()
            if row:
                new_xp = row["xp"] + xp
                new_level = row["level"]
                leveled_up = False
                if new_xp >= new_level * 100:
                    new_xp -= new_level * 100
                    new_level += 1
                    leveled_up = True
                await cur.execute(
                    f"UPDATE {LEVEL_TABLE} SET xp=%s, level=%s WHERE user_id=%s AND guild_id=%s",
                    (new_xp, new_level, member.id, guild.id)
                )
                return leveled_up, new_level
            else:
                await cur.execute(
                    f"INSERT INTO {LEVEL_TABLE} (user_id, guild_id, xp, level) VALUES (%s, %s, %s, %s)",
                    (member.id, guild.id, xp, 1)
                )
                return False, 1

def make_level_embed(member, user_data):
    return discord.Embed(
        title=f"📊 {member.display_name}'s Rank",
        description=f"**Level:** {user_data['level']}\n**XP:** {user_data['xp']}/{user_data['level'] * 100}",
        color=discord.Color.blue()
    ).set_footer(text="Keep chatting to earn more XP!")

async def level_get(bot, member: discord.Member, guild: discord.Guild):
    await ensure_tables_exist(bot)
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"SELECT * FROM {LEVEL_TABLE} WHERE user_id=%s AND guild_id=%s",
                (member.id, guild.id)
            )
            return await cur.fetchone()

async def level_get_all(bot, guild: discord.Guild):
    await ensure_tables_exist(bot)
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"SELECT * FROM {LEVEL_TABLE} WHERE guild_id=%s",
                (guild.id,)
            )
            return await cur.fetchall()

async def level_set_channel(bot, channel: discord.TextChannel, guild: discord.Guild):
    await ensure_tables_exist(bot)
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"REPLACE INTO {LEVEL_CHANNELS_TABLE} (guild_id, channel) VALUES (%s, %s)",
                (guild.id, channel.id)
            )

async def level_get_channel(bot, guild: discord.Guild):
    await ensure_tables_exist(bot)
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"SELECT channel FROM {LEVEL_CHANNELS_TABLE} WHERE guild_id=%s",
                (guild.id,)
            )
            return await cur.fetchone()

class LeaderboardView(discord.ui.View):
    def __init__(self, bot: commands.Bot, leaderboard, interaction: discord.Interaction):
        super().__init__()
        self.bot = bot
        self.leaderboard = leaderboard
        self.interaction = interaction
        self.current_page = 0
        self.entries_per_page = 10
        self.total_pages = (len(leaderboard) - 1) // self.entries_per_page + 1
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        if self.current_page > 0:
            self.add_item(discord.ui.Button(label="Previous", style=discord.ButtonStyle.primary, custom_id="prev"))
        if self.current_page < self.total_pages - 1:
            self.add_item(discord.ui.Button(label="Next", style=discord.ButtonStyle.primary, custom_id="next"))

    async def send_page(self):
        start_index = self.current_page * self.entries_per_page
        end_index = start_index + self.entries_per_page
        page_entries = self.leaderboard[start_index:end_index]

        embed = discord.Embed(
            title=f"🏆 Server Leaderboard (Page {self.current_page + 1}/{self.total_pages})",
            color=discord.Color.gold()
        )

        for i, entry in enumerate(page_entries, start=start_index + 1):
            user_id = entry["user_id"]
            level = entry["level"]
            xp = entry["xp"]
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(
                name=f"{i}. {user.display_name}",
                value=f"**Level:** {level} | **XP:** {xp}",
                inline=False
            )

        await self.interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await self.send_page()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            await self.send_page()

class LevelSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        member = message.author
        if not isinstance(member, discord.Member):
            if message.guild is not None:
                member = message.guild.get_member(message.author.id)
                if member is None:
                    return
            else:
                return

        leveled_up, new_level = await level_add_xp(self.bot, member, message.guild, 10)

        if leveled_up:
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"Congratulations {message.author.mention}, you reached **Level {new_level}**!",
                color=discord.Color.green()
            )
            embed.set_footer(text="Keep chatting to level up more!")

            level_channel_id = await level_get_channel(self.bot, message.guild)
            if level_channel_id and "channel" in level_channel_id:
                level_channel = self.bot.get_channel(level_channel_id["channel"])
                if isinstance(level_channel, discord.TextChannel):
                    return await level_channel.send(embed=embed)

            await message.channel.send(embed=embed)

    @app_commands.command(name="rank", description="Check your current level and XP.")
    async def _rank(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            await interaction.response.send_message("Could not find your member data in this server.", ephemeral=True)
            return

        user_data = await level_get(self.bot, member, interaction.guild)
        if user_data is None:
            await interaction.response.send_message("No level data found for you in this server.", ephemeral=True)
            return
        embed = make_level_embed(member, user_data)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Show the server's top users by level.")
    async def _leaderboard(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        levels = await level_get_all(self.bot, interaction.guild)
        if levels is None:
            await interaction.response.send_message("No data available for this server.", ephemeral=True)
            return

        leaderboard = sorted(
            levels,
            key=lambda x: (x["level"], x["xp"]),
            reverse=True
        )

        if not leaderboard:
            await interaction.response.send_message("No data available for this server.", ephemeral=True)
            return

        view = LeaderboardView(self.bot, leaderboard, interaction)
        await interaction.response.send_message("Loading leaderboard...", ephemeral=False)
        await view.send_page()

    @app_commands.command(name="set_level_channel", description="Set the channel where level-up messages will be sent.")
    @app_commands.describe(channel="The channel to send level-up messages")
    @app_commands.checks.has_permissions(administrator=True)
    async def _set_level_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        await level_set_channel(self.bot, channel, interaction.guild)
        await interaction.response.send_message(f"✅ Level-up messages will now be sent in {channel.mention}.")

    @app_commands.command(name="reset_levels", description="Reset the levels and XP of all users in the server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def _reset_levels(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        await level_reset_all(self.bot, interaction.guild)
        await interaction.response.send_message("✅ All user levels and XP have been reset.")

async def level_reset_all(bot, guild: discord.Guild):
    await ensure_tables_exist(bot)
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"DELETE FROM {LEVEL_TABLE} WHERE guild_id=%s",
                (guild.id,)
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(LevelSystem(bot))
