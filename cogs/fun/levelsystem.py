import discord
from discord.ext import commands
from discord import app_commands
from utils import level_set_channel, level_add_xp, level_get, level_get_channel, level_get_all


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

        for i, (user_id, data) in enumerate(page_entries, start=start_index + 1):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(
                name=f"{i}. {user.display_name}",
                value=f"**Level:** {data['level']} | **XP:** {data['xp']}",
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
        if message.author.bot:
            return

        leveled_up, new_level = level_add_xp(message.author, message.guild, 10)

        if leveled_up:
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"Congratulations {message.author.mention}, you reached **Level {new_level}**!",
                color=discord.Color.green()
            )
            embed.set_footer(text="Keep chatting to level up more!")

            level_channel_id = level_get_channel(message.guild)
            if level_channel_id:
                level_channel = self.bot.get_channel(level_channel_id["channel"])
                if level_channel:
                    return await level_channel.send(embed=embed)

            await message.channel.send(embed=embed)

    @app_commands.command(name="rank", description="Check your current level and XP.")
    async def _rank(self, interaction: discord.Interaction):
        user_data = level_get(interaction.user, interaction.guild)
        embed = discord.Embed(
            title=f"📊 {interaction.user.display_name}'s Rank",
            description=f"**Level:** {user_data['level']}\n**XP:** {user_data['xp']}/{user_data['level'] * 100}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Keep chatting to earn more XP!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Show the server's top users by level.")
    async def _leaderboard(self, interaction: discord.Interaction):
        levels = level_get_all(interaction.guild)
        if levels == None:
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
        level_set_channel(channel, interaction.guild)
        await interaction.response.send_message(f"✅ Level-up messages will now be sent in {channel.mention}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(LevelSystem(bot))
