import discord
from discord.ext import commands
from discord import app_commands
import aiomysql

WELCOME_CHANNELS_TABLE = "welcome_channels"
WELCOME_MESSAGES_TABLE = "welcome_messages"

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_welcome_message = (
            "👋 Welcome {member} to **{guild}**!\n"
            "You are our {member_count}th member!\n"
        )

    async def ensure_tables_exist(self):
        pool = await self.bot.get_mysql_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {WELCOME_CHANNELS_TABLE} (
                        guild_id BIGINT PRIMARY KEY,
                        channel_id BIGINT NOT NULL
                    )
                """)
                await cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {WELCOME_MESSAGES_TABLE} (
                        guild_id BIGINT PRIMARY KEY,
                        message TEXT NOT NULL
                    )
                """)

    async def get_welcome_channel(self, guild_id):
        await self.ensure_tables_exist()
        pool = await self.bot.get_mysql_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    f"SELECT channel_id FROM {WELCOME_CHANNELS_TABLE} WHERE guild_id=%s",
                    (guild_id,)
                )
                row = await cur.fetchone()
                return row["channel_id"] if row else None

    async def get_welcome_message(self, guild_id):
        await self.ensure_tables_exist()
        pool = await self.bot.get_mysql_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    f"SELECT message FROM {WELCOME_MESSAGES_TABLE} WHERE guild_id=%s",
                    (guild_id,)
                )
                row = await cur.fetchone()
                return row["message"] if row else self.default_welcome_message

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = await self.get_welcome_channel(member.guild.id)
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                msg = (await self.get_welcome_message(member.guild.id)).format(
                    member=member.mention,
                    guild=member.guild.name,
                    member_count=member.guild.member_count
                )
                await channel.send(msg)

    @app_commands.command(name="setwelcome", description="Set the welcome message for new members.")
    @app_commands.describe(message="The welcome message. Use {member}, {guild}, {member_count} as placeholders.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setwelcome(self, interaction: discord.Interaction, message: str):
        if interaction.guild is not None:
            await self.ensure_tables_exist()
            pool = await self.bot.get_mysql_pool()
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"REPLACE INTO {WELCOME_MESSAGES_TABLE} (guild_id, message) VALUES (%s, %s)",
                        (interaction.guild.id, message)
                    )
            await interaction.response.send_message("Welcome message updated!", ephemeral=True)
        else:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)

    @app_commands.command(name="setwelcomechannel", description="Set the channel for welcome messages.")
    @app_commands.describe(channel="The channel to send welcome messages in.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setwelcomechannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.guild is not None:
            await self.ensure_tables_exist()
            pool = await self.bot.get_mysql_pool()
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"REPLACE INTO {WELCOME_CHANNELS_TABLE} (guild_id, channel_id) VALUES (%s, %s)",
                        (interaction.guild.id, channel.id)
                    )
            await interaction.response.send_message(f"Welcome channel set to {channel.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Welcomer(bot))