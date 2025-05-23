import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import random
import aiomysql

CURRENCY_TABLE = "currency"

async def ensure_currency_table(bot):
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {CURRENCY_TABLE} (
                    guild_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    balance BIGINT NOT NULL DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)

async def get_balance(bot, guild_id: int, user_id: int):
    await ensure_currency_table(bot)
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"SELECT balance FROM {CURRENCY_TABLE} WHERE guild_id=%s AND user_id=%s",
                (guild_id, user_id)
            )
            row = await cur.fetchone()
            return row["balance"] if row else 0

async def update_balance(bot, guild_id: int, user_id: int, amount: int):
    await ensure_currency_table(bot)
    pool = await bot.get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"INSERT INTO {CURRENCY_TABLE} (guild_id, user_id, balance) VALUES (%s, %s, %s) "
                f"ON DUPLICATE KEY UPDATE balance = balance + VALUES(balance)",
                (guild_id, user_id, amount)
            )

class BlackjackGame(discord.ui.View):
    CARD_EMOJIS = {
        "A": "🅰️", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", #Placeholder
        "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "10": "🔟", "J": "🇯", "Q": "🇶", "K": "🇰" #Placeholder
    }
    CARD_SUITS = ["♠️", "♥️", "♦️", "♣️"] #Placeholders for suits

    CARD_VALUES = {
        "A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
        "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10
    }

    def __init__(self, bot, interaction, user_id, bet):
        super().__init__()
        self.bot = bot
        self.interaction = interaction
        self.user_id = user_id
        self.bet = bet
        self.player_hand = [self.draw_card() for _ in range(2)]
        self.dealer_hand = [self.draw_card() for _ in range(2)]
        self.game_over = False

    def draw_card(self):
        card = random.choice(list(self.CARD_VALUES.keys()))
        suit = random.choice(self.CARD_SUITS)
        return (card, suit)

    def hand_display(self, hand, reveal_all=True):
        if reveal_all:
            return " ".join(f"{self.CARD_EMOJIS[card]}{suit}" for card, suit in hand)
        else:
            card, suit = hand[0]
            return f"{self.CARD_EMOJIS[card]}{suit} ❓"

    def calculate_score(self, hand):
        values = [self.CARD_VALUES[card] for card, _ in hand]
        score = sum(values)
        num_aces = sum(1 for card, _ in hand if card == "A")
        while score > 21 and num_aces:
            score -= 10
            num_aces -= 1
        return score

    async def update_message(self):
        player_score = self.calculate_score(self.player_hand)
        dealer_score = self.calculate_score(self.dealer_hand) if self.game_over else None
        player_hand_str = self.hand_display(self.player_hand)
        if self.game_over:
            dealer_hand_str = self.hand_display(self.dealer_hand)
        else:
            dealer_hand_str = self.hand_display(self.dealer_hand, reveal_all=False)
        embed = discord.Embed(
            title="🃏 Blackjack",
            description=(
                f"**Your Hand:** {player_hand_str} (Score: {player_score})\n"
                f"**Dealer's Hand:** {dealer_hand_str} (Score: {dealer_score if dealer_score is not None else '??'})"
            ),
            color=discord.Color.blue()
        )
        if self.game_over:
            if player_score > 21:
                result = "😢 You busted! You lost your bet."
                await update_balance(self.bot, self.interaction.guild.id, self.user_id, -self.bet)
            elif dealer_score is not None and (dealer_score > 21 or player_score > dealer_score):
                result = f"🎉 You won! You earned **{self.bet} Sleeeper Coins**."
                await update_balance(self.bot, self.interaction.guild.id, self.user_id, self.bet * 2)
            elif dealer_score is not None and player_score < dealer_score:
                result = "😢 You lost! The dealer wins."
                await update_balance(self.bot, self.interaction.guild.id, self.user_id, -self.bet)
            else:
                result = "🤝 It's a tie! No coins were lost or gained."
            embed.add_field(name="Result", value=result, inline=False)
            self.clear_items()
        await self.interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, _: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return

        await interaction.response.defer()

        self.player_hand.append(self.draw_card())
        if self.calculate_score(self.player_hand) > 21:
            self.game_over = True
        await self.update_message()

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, _: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return

        await interaction.response.defer()

        self.game_over = True
        while self.calculate_score(self.dealer_hand) < 17:
            self.dealer_hand.append(self.draw_card())
        await self.update_message()

class CurrencySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.work_cooldowns = {}

    async def get_balance(self, guild_id: int, user_id: int):
        return await get_balance(self.bot, guild_id, user_id)

    async def update_balance(self, guild_id: int, user_id: int, amount: int):
        await update_balance(self.bot, guild_id, user_id, amount)

    @app_commands.command(name="balance", description="Check your Sleeeper Coins balance.")
    async def balance(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        balance = await self.get_balance(guild_id, user_id)
        embed = discord.Embed(
            title="💰 Sleeeper Coins Balance",
            description=f"{interaction.user.mention}, you have **{balance} Sleeeper Coins** in this server.",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="doubleornothing", description="Play Double or Nothing to gamble your Sleeeper Coins.")
    @app_commands.describe(amount="The amount of Sleeeper Coins to gamble.")
    async def double_or_nothing(self, interaction: discord.Interaction, amount: int):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        if amount <= 0:
            await interaction.response.send_message("❌ You must gamble a positive amount.", ephemeral=True)
            return

        balance = await self.get_balance(guild_id, user_id)
        if amount > balance:
            await interaction.response.send_message("❌ You don't have enough Sleeeper Coins to gamble that amount.", ephemeral=True)
            return

        outcome = random.choice(["win", "lose"])
        if outcome == "win":
            winnings = amount * 2
            await self.update_balance(guild_id, user_id, winnings)
            embed = discord.Embed(
                title="🎲 Double or Nothing Result",
                description=f"🎉 You won! You doubled your bet and earned **{winnings} Sleeeper Coins**!",
                color=discord.Color.green()
            )
        else:
            await self.update_balance(guild_id, user_id, -amount)
            embed = discord.Embed(
                title="🎲 Double or Nothing Result",
                description=f"😢 You lost! You lost **{amount} Sleeeper Coins**.",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roulette", description="Play Roulette to gamble your Sleeeper Coins.")
    @app_commands.describe(amount="The amount of Sleeeper Coins to gamble.", color="Choose red or black.")
    async def roulette(self, interaction: discord.Interaction, amount: int, color: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        if amount <= 0:
            await interaction.response.send_message("❌ You must gamble a positive amount.", ephemeral=True)
            return

        balance = await self.get_balance(guild_id, user_id)
        if amount > balance:
            await interaction.response.send_message("❌ You don't have enough Sleeeper Coins to gamble that amount.", ephemeral=True)
            return

        if color.lower() not in ["red", "black"]:
            await interaction.response.send_message("❌ You must choose either 'red' or 'black'.", ephemeral=True)
            return

        winning_color = random.choice(["red", "black"])
        if color.lower() == winning_color:
            winnings = amount * 2
            await self.update_balance(guild_id, user_id, winnings)
            embed = discord.Embed(
                title="🎡 Roulette Result",
                description=f"🎉 You won! The ball landed on **{winning_color}**.\nYou earned **{winnings} Sleeeper Coins**!",
                color=discord.Color.green()
            )
        else:
            await self.update_balance(guild_id, user_id, -amount)
            embed = discord.Embed(
                title="🎡 Roulette Result",
                description=f"😢 You lost! The ball landed on **{winning_color}**.\nYou lost **{amount} Sleeeper Coins**.",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CurrencySystem(bot))