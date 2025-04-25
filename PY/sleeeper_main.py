from math import fabs
import discord
from discord.ext import commands
from discord import Color, Embed, app_commands
from discord.ui import View, Button, Modal, TextInput
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import uuid
from datetime import timedelta
from discord.app_commands import checks
import json

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def setup_error_logger():
    error_logger = logging.getLogger("error_logger")
    error_logger.setLevel(logging.ERROR)

    handler = RotatingFileHandler("error.log", maxBytes=1000000, backupCount=1, delay=True)
    handler.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    error_logger.addHandler(handler)
    return error_logger

error_logger = setup_error_logger()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_APPLICATION_ID = os.getenv("DISCORD_APPLICATION_ID")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")

ALLOWED_GUILD_ID = int(DISCORD_GUILD_ID)

if not DISCORD_BOT_TOKEN or not DISCORD_APPLICATION_ID or not DISCORD_GUILD_ID:
    raise ValueError("❌ Missing required environment variables. Please check your .env file.")

VERSION = "0.4.2 Beta Build"
NEXT_VERSION = "0.4.3 Beta Build"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="´",
            intents=intents,
            application_id=DISCORD_APPLICATION_ID
        )
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="Starting up...")

    async def setup_hook(self):
        await self.tree.sync()
        logging.info("✅ Slash-Commands registered:")
        for command in self.tree.get_commands():
            logging.info(f" - {command.name}: {command.description}")

bot = MyBot()

WARNING_LOG_FILE = "warnings.log"

log_channels = {}

def get_log_channel(guild_id):
    return log_channels.get(guild_id)

ticket_log_channels = {}

def get_ticket_log_channel(guild_id):
    return ticket_log_channels.get(guild_id)

verify_roles = {}

@bot.event
async def on_ready():
    load_afk_users()
    total_members = sum(guild.member_count or 0 for guild in bot.guilds)
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"{total_members} Members"
    ))
    print(f"🤖 Bot is Online as {bot.user}")
    logging.info(f"Bot is ready and watching {total_members} members.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have the required permissions to use this command!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument. Please check the command usage.")
    else:
        await ctx.send("❌ An unexpected error occurred!")
    
    error_logger.error(f"Error in command '{ctx.command}': {error}")

@bot.tree.command(name="ping", description="Responds with the current latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! 🏓 {latency}ms")

@bot.tree.command(name="info", description="Shows information about the bot")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Info", color=Color.blue())
    embed.add_field(name="Version", value=VERSION, inline=False)
    embed.add_field(name="Coder", value="<@1104736921474834493>", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="version", description="Shows the current version")
async def version_info(interaction: discord.Interaction):
    embed = discord.Embed(title="Version Info", color=Color.blue())
    embed.add_field(name="Bot Name", value=bot.user.name, inline=False)
    embed.add_field(name="Version", value=VERSION, inline=False)
    embed.add_field(name="Next Version", value=NEXT_VERSION, inline=False)
    embed.add_field(name="Release Date", value="TBA", inline=False)
    embed.add_field(name="Support Server", value="https://discord.gg/WwApdk4z4H", inline=False)
    embed.add_field(name="Extra Info", value="**Note:** This bot is in Beta phase.", inline=False)
    embed.set_footer(text="For more information, visit the support server.")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="say", description="The bot says what you want")
@app_commands.describe(text="What the bot should say")
async def say(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(f"{text}")

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/WwApdk4z4H"))

@bot.tree.command(name="help", description="Shows a list of available commands")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message("If you need any Help with my Bot Join my Discord Server below:", view=HelpView())

@bot.tree.command(name="lock_channel", description="Locks the current channel so no one can write.")
@commands.has_permissions(manage_channels=True)
async def lock_channel(interaction: discord.Interaction):
    channel = interaction.channel  
    guild = interaction.guild

    overwrite = channel.overwrites_for(guild.default_role)
    overwrite.send_messages = False  
    await channel.set_permissions(guild.default_role, overwrite=overwrite)

    await interaction.response.send_message(
        f"🔒 The channel {channel.mention} has been locked. Members can no longer write here."
    )
    logging.info(f"🔒 Channel {channel.name} was locked by {interaction.user}.")


@bot.tree.command(name="unlock_channel", description="Unlocks the current channel so members can write again.")
@commands.has_permissions(manage_channels=True)
async def unlock_channel(interaction: discord.Interaction):
    channel = interaction.channel
    guild = interaction.guild

    overwrite = channel.overwrites_for(guild.default_role)
    overwrite.send_messages = True 
    await channel.set_permissions(guild.default_role, overwrite=overwrite)

    await interaction.response.send_message(
        f"🔓 The channel {channel.mention} has been unlocked. Members can write here again."
    )
    logging.info(f"🔓 Channel {channel.name} was unlocked by {interaction.user}.")

@bot.tree.command(name="warn", description="Warns a user and sends them a DM with the reason.")
@checks.has_permissions(moderate_members=True)
@app_commands.describe(user="The user to warn", reason="The reason for the warning")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    warning_id = str(uuid.uuid4())[:8]

    dm_embed = discord.Embed(
        title="⚠️ You Have Been Warned",
        description=f"You have been warned in **{interaction.guild.name}**.",
        color=discord.Color.red()
    )
    dm_embed.add_field(name="Reason", value=reason, inline=False)
    dm_embed.add_field(name="Warning ID", value=warning_id, inline=False)
    dm_embed.set_footer(text=f"Warned by {interaction.user}", icon_url=interaction.user.avatar.url)

    try:
        await user.send(embed=dm_embed)
    except discord.Forbidden:
        await interaction.response.send_message(
            f"❌ Could not send a DM to {user.mention}. They might have DMs disabled.",
            ephemeral=True
        )
        return

    channel_embed = discord.Embed(
        title="✅ User Warned",
        description=f"{user.mention} has been warned.",
        color=discord.Color.orange()
    )
    channel_embed.add_field(name="Reason", value=reason, inline=False)
    channel_embed.add_field(name="Warning ID", value=warning_id, inline=False)
    channel_embed.set_footer(text=f"Warned by {interaction.user}", icon_url=interaction.user.avatar.url)

    await interaction.response.send_message(embed=channel_embed)

    with open(WARNING_LOG_FILE, "a") as log_file:
        log_file.write(f"{warning_id} | {user} | {reason} | Warned by {interaction.user}\n")

    log_channel_id = get_log_channel(interaction.guild.id)
    if log_channel_id:
        log_channel = interaction.guild.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=channel_embed)

    logging.info(f"⚠️ {user} was warned by {interaction.user} for: {reason} (ID: {warning_id})")

@bot.tree.command(name="set_warn_log", description="Sets the channel where warnings will be logged.")
@commands.has_permissions(administrator=True)
async def set_warn_log(interaction: discord.Interaction, channel: discord.TextChannel):
    log_channels[interaction.guild.id] = channel.id
    await interaction.response.send_message(
        f"✅ Warning log channel has been set to {channel.mention}.",
        ephemeral=True
    )
    logging.info(f"Warning log channel set to {channel.name} in guild {interaction.guild.name}.")
    
@bot.tree.command(name="set_verify_role", description="Sets the role to be assigned upon verification.")
@commands.has_permissions(administrator=True)
async def set_verify_role(interaction: discord.Interaction, role: discord.Role):
    verify_roles[interaction.guild.id] = role.id
    await interaction.response.send_message(
        f"✅ Verification role has been set to {role.mention}.",
        ephemeral=True
    )
    logging.info(f"Verification role set to {role.name} in guild {interaction.guild.name}.")

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
            logging.info(f"Created verification role 'Verified' in guild {guild.name}.")

        await member.add_roles(role)
        await interaction.response.send_message(
            f"✅ You have been verified and assigned the {role.mention} role!",
            ephemeral=True
        )
        logging.info(f"Assigned role '{role.name}' to {member.name} in guild {guild.name}.")

@bot.tree.command(name="send_verify", description="Sends the verification embed.")
@commands.has_permissions(administrator=True)
async def send_verify(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✅ Verify Yourself",
        description="Click the **Verify** button below to verify yourself and gain access to the server.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Verification System")
    await interaction.response.send_message(embed=embed, view=VerifyView())

@bot.tree.command(name="servers", description="Displays all the servers the bot is currently in.")
@commands.has_permissions(administrator=True)
async def servers(interaction: discord.Interaction):
    guilds = bot.guilds

    embed = discord.Embed(
        title="🤖 Servers the Bot is On",
        description=f"The bot is currently in **{len(guilds)}** servers.",
        color=discord.Color.blue()
    )

    for guild in guilds:
        embed.add_field(
            name=guild.name,
            value=f"**ID:** {guild.id}\n**Members:** {guild.member_count}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="timeout", description="Timeout a user for a custom duration with a reason.")
@checks.has_permissions(moderate_members=True)
@app_commands.describe(
    user="The user to timeout",
    duration="The duration of the timeout in minutes",
    reason="The reason for the timeout"
)
async def timeout(interaction: discord.Interaction, user: discord.Member, duration: int, reason: str):
    timeout_duration = timedelta(minutes=duration)

    try:
        await user.timeout(timeout_duration, reason=reason)
    except discord.Forbidden:
        await interaction.response.send_message(
            f"❌ I do not have permission to timeout {user.mention}.",
            ephemeral=True
        )
        return
    except discord.HTTPException as e:
        await interaction.response.send_message(
            f"❌ Failed to timeout {user.mention}. Error: {e}",
            ephemeral=True
        )
        return

    try:
        dm_embed = discord.Embed(
            title="⏳ You Have Been Timed Out",
            description=f"You have been timed out in **{interaction.guild.name}**.",
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        dm_embed.set_footer(text="Please follow the server rules to avoid further actions.")
        await user.send(embed=dm_embed)
    except discord.Forbidden:
        await interaction.response.send_message(
            f"⚠️ Could not send a DM to {user.mention}. They might have DMs disabled.",
            ephemeral=True
        )

    channel_embed = discord.Embed(
        title="✅ User Timed Out",
        description=f"{user.mention} has been timed out.",
        color=discord.Color.orange()
    )
    channel_embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
    channel_embed.add_field(name="Reason", value=reason, inline=False)
    channel_embed.set_footer(text=f"Timed out by {interaction.user}", icon_url=interaction.user.avatar.url)

    await interaction.response.send_message(embed=channel_embed)

    logging.info(f"⏳ {user} was timed out by {interaction.user} for {duration} minutes. Reason: {reason}")

AFK_FILE = "afk_users.json"

def save_afk_users():
    with open(AFK_FILE, "w") as file:
        json.dump(afk_users, file)

def load_afk_users():
    global afk_users
    if os.path.exists(AFK_FILE):
        with open(AFK_FILE, "r") as file:
            afk_users = json.load(file)
    else:
        afk_users = {}

@bot.tree.command(name="afk", description="Set your AFK status with an optional reason.")
@app_commands.describe(reason="The reason why you're AFK (optional)")
async def afk(interaction: discord.Interaction, reason: str = "No reason provided"):
    afk_users[interaction.user.id] = reason
    save_afk_users()

    afk_embed = discord.Embed(
        title="✅ AFK Status Set",
        description=f"{interaction.user.mention}, you are now AFK.",
        color=discord.Color.blue()
    )
    afk_embed.add_field(name="Reason", value=reason, inline=False)
    afk_embed.set_footer(text="You will be notified when someone mentions you.")

    await interaction.response.send_message(embed=afk_embed, ephemeral=True)
    logging.info(f"{interaction.user} is now AFK globally. Reason: {reason}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    for user_id, reason in afk_users.items():
        if message.mentions and user_id in [mention.id for mention in message.mentions]:
            afk_user = await bot.fetch_user(user_id)

            afk_notify_embed = discord.Embed(
                title="🚨 User is AFK",
                description=f"{afk_user.mention} is currently AFK.",
                color=discord.Color.orange()
            )
            afk_notify_embed.add_field(name="Reason", value=reason, inline=False)
            afk_notify_embed.set_footer(text="They will respond when they return.")

            await message.reply(embed=afk_notify_embed, mention_author=False)

    if message.author.id in afk_users:
        del afk_users[message.author.id]
        save_afk_users()

        afk_removed_embed = discord.Embed(
            title="Welcome Back!",
            description=f"{message.author.mention}, your AFK status has been removed.",
            color=discord.Color.green()
        )
        afk_removed_embed.set_footer(text="Glad to have you back!")

        await message.channel.send(embed=afk_removed_embed, delete_after=10)
        logging.info(f"{message.author} is no longer AFK globally.")

    await bot.process_commands(message)

bot.run(DISCORD_BOT_TOKEN)
