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

async def setup(bot):
    await bot.add_cog(CurrencySystem(bot))