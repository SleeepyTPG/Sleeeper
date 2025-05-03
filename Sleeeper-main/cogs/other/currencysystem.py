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

class BlackjackGame(discord.ui.View):
    def __init__(self, bot, interaction, user_id, bet, update_balance):
        super().__init__()
        self.bot = bot
        self.interaction = interaction
        self.user_id = user_id
        self.bet = bet
        self.update_balance = update_balance
        self.player_hand = [random.randint(1, 11), random.randint(1, 11)]
        self.dealer_hand = [random.randint(1, 11), random.randint(1, 11)]
        self.game_over = False

    def calculate_score(self, hand):
        return sum(hand)

    async def update_message(self):
        player_score = self.calculate_score(self.player_hand)
        dealer_score = self.calculate_score(self.dealer_hand) if self.game_over else "??"
        embed = discord.Embed(
            title="🃏 Blackjack",
            description=(
                f"**Your Hand:** {self.player_hand} (Score: {player_score})\n"
                f"**Dealer's Hand:** {self.dealer_hand if self.game_over else [self.dealer_hand[0], '??']} (Score: {dealer_score})"
            ),
            color=discord.Color.blue()
        )
        if self.game_over:
            if player_score > 21:
                result = "😢 You busted! You lost your bet."
                self.update_balance(self.user_id, -self.bet)
            elif dealer_score > 21 or player_score > dealer_score:
                result = f"🎉 You won! You earned **{self.bet} Sleeeper Coins**."
                self.update_balance(self.user_id, self.bet)
            elif player_score < dealer_score:
                result = "😢 You lost! The dealer wins."
                self.update_balance(self.user_id, -self.bet)
            else:
                result = "🤝 It's a tie! No coins were lost or gained."
            embed.add_field(name="Result", value=result, inline=False)
            self.clear_items()  # Remove buttons when the game is over
        await self.interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return

        await interaction.response.defer()

        self.player_hand.append(random.randint(1, 11))
        if self.calculate_score(self.player_hand) > 21:
            self.game_over = True
        await self.update_message()

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return

        await interaction.response.defer()

        self.game_over = True
        while self.calculate_score(self.dealer_hand) < 17:
            self.dealer_hand.append(random.randint(1, 11))
        await self.update_message()

class CurrencySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances = load_balances()
        self.work_cooldowns = {}

    def get_balance(self, guild_id: int, user_id: int):
        guild_id = str(guild_id)
        user_id = str(user_id)
        return self.balances.get(guild_id, {}).get(user_id, 0)

    def update_balance(self, guild_id: int, user_id: int, amount: int):
        guild_id = str(guild_id)
        user_id = str(user_id)
        if guild_id not in self.balances:
            self.balances[guild_id] = {}
        if user_id not in self.balances[guild_id]:
            self.balances[guild_id][user_id] = 0
        self.balances[guild_id][user_id] += amount
        save_balances(self.balances)

    @app_commands.command(name="balance", description="Check your Sleeeper Coins balance.")
    async def balance(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        balance = self.get_balance(guild_id, user_id)
        embed = discord.Embed(
            title="💰 Sleeeper Coins Balance",
            description=f"{interaction.user.mention}, you have **{balance} Sleeeper Coins** in this server.",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Work to earn Sleeeper Coins.")
    async def work(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
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
        self.update_balance(guild_id, user_id, earnings)
        self.work_cooldowns[user_id] = current_time

        embed = discord.Embed(
            title="🛠️ Work Completed",
            description=f"{interaction.user.mention}, you earned **{earnings} Sleeeper Coins** for your work!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="blackjack", description="Play Blackjack to gamble your Sleeeper Coins.")
    @app_commands.describe(amount="The amount of Sleeeper Coins to gamble.")
    async def blackjack(self, interaction: discord.Interaction, amount: int):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        if amount <= 0:
            await interaction.response.send_message("❌ You must gamble a positive amount.", ephemeral=True)
            return

        balance = self.get_balance(guild_id, user_id)
        if amount > balance:
            await interaction.response.send_message("❌ You don't have enough Sleeeper Coins to gamble that amount.", ephemeral=True)
            return

        view = BlackjackGame(self.bot, interaction, user_id, amount, lambda uid, amt: self.update_balance(guild_id, uid, amt))
        embed = discord.Embed(
            title="🃏 Blackjack",
            description=(
                f"**Your Hand:** {view.player_hand} (Score: {sum(view.player_hand)})\n"
                f"**Dealer's Hand:** [{view.dealer_hand[0]}, '??'] (Score: ??)"
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="doubleornothing", description="Play Double or Nothing to gamble your Sleeeper Coins.")
    @app_commands.describe(amount="The amount of Sleeeper Coins to gamble.")
    async def double_or_nothing(self, interaction: discord.Interaction, amount: int):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        if amount <= 0:
            await interaction.response.send_message("❌ You must gamble a positive amount.", ephemeral=True)
            return

        balance = self.get_balance(guild_id, user_id)
        if amount > balance:
            await interaction.response.send_message("❌ You don't have enough Sleeeper Coins to gamble that amount.", ephemeral=True)
            return

        outcome = random.choice(["win", "lose"])
        if outcome == "win":
            winnings = amount * 2
            self.update_balance(guild_id, user_id, winnings)
            embed = discord.Embed(
                title="🎲 Double or Nothing Result",
                description=f"🎉 You won! You doubled your bet and earned **{winnings} Sleeeper Coins**!",
                color=discord.Color.green()
            )
        else:
            self.update_balance(guild_id, user_id, -amount)
            embed = discord.Embed(
                title="🎲 Double or Nothing Result",
                description=f"😢 You lost! You lost **{amount} Sleeeper Coins**.",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roulette", description="Play Roulette to gamble your Sleeeper Coins.")
    @app_commands.describe(amount="The amount of Sleeeper Coins to gamble.", color="Choose red or black.")
    async def roulette(self, interaction: discord.Interaction, amount: int, color: str):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        if amount <= 0:
            await interaction.response.send_message("❌ You must gamble a positive amount.", ephemeral=True)
            return

        balance = self.get_balance(guild_id, user_id)
        if amount > balance:
            await interaction.response.send_message("❌ You don't have enough Sleeeper Coins to gamble that amount.", ephemeral=True)
            return

        if color.lower() not in ["red", "black"]:
            await interaction.response.send_message("❌ You must choose either 'red' or 'black'.", ephemeral=True)
            return

        winning_color = random.choice(["red", "black"])
        if color.lower() == winning_color:
            winnings = amount * 2
            self.update_balance(guild_id, user_id, winnings)
            embed = discord.Embed(
                title="🎡 Roulette Result",
                description=f"🎉 You won! The ball landed on **{winning_color}**.\nYou earned **{winnings} Sleeeper Coins**!",
                color=discord.Color.green()
            )
        else:
            self.update_balance(guild_id, user_id, -amount)
            embed = discord.Embed(
                title="🎡 Roulette Result",
                description=f"😢 You lost! The ball landed on **{winning_color}**.\nYou lost **{amount} Sleeeper Coins**.",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CurrencySystem(bot))