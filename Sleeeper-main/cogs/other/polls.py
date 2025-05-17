import discord
from discord.ext import commands
from discord import app_commands
import typing
import asyncio

class PollView(discord.ui.View):
    def __init__(self, options, show_status: bool, embed: discord.Embed, interaction: discord.Interaction, poll_duration: int):
        super().__init__(timeout=poll_duration)
        self.votes = {option: set() for option in options}
        self.options = options
        self.show_status = show_status
        self.embed = embed
        self.interaction = interaction
        self.poll_duration = poll_duration

        for idx, option in enumerate(options):
            self.add_item(PollButton(option, idx, show_status))

    def get_results(self):
        total_votes = sum(len(v) for v in self.votes.values())
        results = []
        for option in self.options:
            count = len(self.votes[option])
            if self.show_status:
                percent = (count / total_votes) if total_votes > 0 else 0
                blocks = int(percent * 10)
                bar = "█" * blocks + "░" * (10 - blocks)
                results.append((option, count, bar))
            else:
                results.append((option, count, None))
        return results

    async def update_embed(self):
        self.embed.clear_fields()
        results = self.get_results()
        for idx, (option, count, bar) in enumerate(results, 1):
            if self.show_status:
                value = f"Votes: {count}\n{bar}"
            else:
                value = "Voting is anonymous."
            self.embed.add_field(name=f"Option {idx}: {option}", value=value, inline=False)
        await self.interaction.edit_original_response(embed=self.embed, view=self)

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        self.embed.clear_fields()
        results = self.get_results()
        for idx, (option, count, bar) in enumerate(results, 1):
            if self.show_status:
                value = f"Final votes: {count}\n{bar}"
            else:
                value = f"Final votes: {count}"
            self.embed.add_field(name=f"Option {idx}: {option}", value=value, inline=False)
        self.embed.set_footer(text="Poll ended.")
        await self.interaction.edit_original_response(embed=self.embed, view=self)

class PollButton(discord.ui.Button):
    def __init__(self, option, idx, show_status):
        super().__init__(label=option, style=discord.ButtonStyle.primary, custom_id=f"poll_{idx}")
        self.show_status = show_status

    async def callback(self, interaction: discord.Interaction):
        view: typing.Optional[PollView] = self.view
        if view is None:
            await interaction.response.send_message("An error occurred: Poll view is not available.", ephemeral=True)
            return
        for voters in view.votes.values():
            voters.discard(interaction.user.id)
        view.votes[self.label].add(interaction.user.id)
        if self.show_status:
            await interaction.response.send_message(
                f"You voted for **{self.label}**!\n\nCurrent results are shown in the poll embed.",
                ephemeral=True
            )
            await view.update_embed()
        else:
            await interaction.response.send_message(
                f"You voted for **{self.label}**! This is an anonymous poll.",
                ephemeral=True
            )

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Create an interactive poll with up to 5 options and a timer.")
    @app_commands.describe(
        question="The poll question",
        option1="First option",
        option2="Second option",
        option3="Third option",
        option4="Fourth option",
        option5="Fifth option",
        status_bar="Show a status bar for votes? (yes/no)",
        anonymous="Make the poll anonymous? (yes/no)",
        duration="How long should the poll last? (seconds, e.g. 60 = 1 minute)"
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: typing.Optional[str] = None,
        option4: typing.Optional[str] = None,
        option5: typing.Optional[str] = None,
        status_bar: typing.Optional[str] = "yes",
        anonymous: typing.Optional[str] = "no",
        duration: typing.Optional[int] = 60
    ):
        options = [option1, option2]
        if option3: options.append(option3)
        if option4: options.append(option4)
        if option5: options.append(option5)

        if len(options) < 2:
            await interaction.response.send_message("You must provide at least two options.", ephemeral=True)
            return
        if len(options) > 5:
            await interaction.response.send_message("You can provide up to five options.", ephemeral=True)
            return
        if duration is None or duration < 10 or duration > 86400:
            await interaction.response.send_message("Please provide a duration between 10 and 86400 seconds (24 hours).", ephemeral=True)
            return

        status_bar_value = status_bar.lower() if status_bar is not None else "yes"
        anonymous_value = anonymous.lower() if anonymous is not None else "no"
        show_status = status_bar_value == "yes" and anonymous_value != "yes"

        embed = discord.Embed(
            title="📊 Poll",
            description=f"{question}\n\n⏳ This poll will end in {duration} seconds.",
            color=discord.Color.blurple()
        )
        for idx, opt in enumerate(options, 1):
            if show_status:
                value = "Votes: 0\n" + "░" * 10
            else:
                value = "Voting is anonymous."
            embed.add_field(name=f"Option {idx}: {opt}", value=value, inline=False)
        if anonymous_value == "yes":
            embed.set_footer(text="This is an anonymous poll. Results will not be shown until the poll ends.")
        elif show_status:
            embed.set_footer(text="Votes are shown live with a status bar.")

        view = PollView(options, show_status, embed, interaction, poll_duration=duration)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Polls(bot))