import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
import time

CURRENCY_FILE = "currency.json"

def load_balances():
    if os.path.exists(CURRENCY_FILE):
        with open(CURRENCY_FILE, "r") as file:
            return json.load(file)
    return {}

def save_balances(balances):
    with open(CURRENCY_FILE, "w") as file:
        json.dump(balances, file)

class LeaderboardView(discord.ui.View):
    def __init__(self, bot, balances, interaction):
        super().__init__()
        self.bot = bot
        self.balances = balances
        self.interaction = interaction
        self.current_page = 0
        self.entries_per_page = 10
        self.total_pages = (len(balances) - 1) // self.entries_per_page + 1

        # Add navigation buttons
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
        page_entries = list(self.balances.items())[start_index:end_index]

        embed = discord.Embed(
            title=f"🏆 Sleeeper Coins Leaderboard (Page {self.current_page + 1}/{self.total_pages})",
            color=discord.Color.gold()
        )

        for i, (user_id, balance) in enumerate(page_entries, start=start_index + 1):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(
                name=f"{i}. {user.display_name}",
                value=f"**Coins:** {balance}",
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

class CurrencySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances = load_balances()
        self.work_cooldowns = {}

    def get_balance(self, user_id: int):
        return self.balances.get(str(user_id), 0)

    def update_balance(self, user_id: int, amount: int):
        user_id = str(user_id)
        if user_id not in self.balances:
            self.balances[user_id] = 0
        self.balances[user_id] += amount
        save_balances(self.balances)

    @app_commands.command(name="balance", description="Check your Sleeeper Coins balance.")
    async def balance(self, interaction: discord.Interaction):
        balance = self.get_balance(interaction.user.id)
        embed = discord.Embed(
            title="💰 Sleeeper Coins Balance",
            description=f"{interaction.user.mention}, you have **{balance} Sleeeper Coins**.",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Work to earn Sleeeper Coins.")
    async def work(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        cooldown_time = 2 * 60 * 60

        if user_id in self.work_cooldowns:
            last_used = self.work_cooldowns[user_id]
            time_remaining = cooldown_time - (current_time - last_used)
            if time_remaining > 0:
                minutes, seconds = divmod(int(time_remaining), 60)
                hours, minutes = divmod(minutes, 60)
                await interaction.response.send_message(
                    f"⏳ You need to wait **{hours}h {minutes}m {seconds}s** before using `/work` again.",
                    ephemeral=True
                )
                return

        earnings = random.randint(50, 200)
        self.update_balance(user_id, earnings)
        self.work_cooldowns[user_id] = current_time

        embed = discord.Embed(
            title="🛠️ Work Completed",
            description=f"{interaction.user.mention}, you earned **{earnings} Sleeeper Coins** for your work!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="gamble", description="Gamble your Sleeeper Coins.")
    @app_commands.describe(amount="The amount of Sleeeper Coins to gamble.")
    async def gamble(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ You must gamble a positive amount.", ephemeral=True)
            return

        balance = self.get_balance(interaction.user.id)
        if amount > balance:
            await interaction.response.send_message("❌ You don't have enough Sleeeper Coins to gamble that amount.", ephemeral=True)
            return

        outcome = random.choice(["win", "lose"])
        if outcome == "win":
            winnings = amount * 2
            self.update_balance(interaction.user.id, winnings)
            embed = discord.Embed(
                title="🎲 Gambling Result",
                description=f"🎉 {interaction.user.mention}, you won **{winnings} Sleeeper Coins**!",
                color=discord.Color.green()
            )
        else:
            self.update_balance(interaction.user.id, -amount)
            embed = discord.Embed(
                title="🎲 Gambling Result",
                description=f"😢 {interaction.user.mention}, you lost **{amount} Sleeeper Coins**.",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="trade", description="Trade Sleeeper Coins with another user.")
    @app_commands.describe(user="The user to trade with.", amount="The amount of Sleeeper Coins to trade.")
    async def trade(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ You must trade a positive amount.", ephemeral=True)
            return

        balance = self.get_balance(interaction.user.id)
        if amount > balance:
            await interaction.response.send_message("❌ You don't have enough Sleeeper Coins to trade that amount.", ephemeral=True)
            return

        self.update_balance(interaction.user.id, -amount)
        self.update_balance(user.id, amount)

        embed = discord.Embed(
            title="🤝 Trade Successful",
            description=f"{interaction.user.mention} traded **{amount} Sleeeper Coins** with {user.mention}.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coins-leaderboard", description="Show the Sleeeper Coins leaderboard.")
    async def coins_leaderboard(self, interaction: discord.Interaction):
        if not self.balances:
            await interaction.response.send_message("No data available for the leaderboard.", ephemeral=True)
            return

        sorted_balances = dict(sorted(self.balances.items(), key=lambda item: item[1], reverse=True))

        view = LeaderboardView(self.bot, sorted_balances, interaction)
        await interaction.response.send_message("Loading leaderboard...", ephemeral=False)
        await view.send_page()

async def setup(bot):
    await bot.add_cog(CurrencySystem(bot))