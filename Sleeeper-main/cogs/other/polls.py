import discord
from discord.ext import commands
from discord import app_commands
import typing

class PollView(discord.ui.View):
    def __init__(self, options, show_status: bool):
        super().__init__(timeout=300)
        self.votes = {option: set() for option in options}
        self.options = options
        self.show_status = show_status

        for idx, option in enumerate(options):
            self.add_item(PollButton(option, idx, show_status))

    def get_results(self):
        total_votes = sum(len(v) for v in self.votes.values())
        results = []
        for option in self.options:
            count = len(self.votes[option])
            if self.show_status:
                # Status bar: 10 blocks max
                percent = (count / total_votes) if total_votes > 0 else 0
                blocks = int(percent * 10)
                bar = "█" * blocks + "░" * (10 - blocks)
                results.append(f"**{option}**: {count} vote{'s' if count != 1 else ''} {bar}")
            else:
                results.append(f"**{option}**: Voting is anonymous.")
        return "\n".join(results)

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
                f"You voted for **{self.label}**!\n\nCurrent results:\n{view.get_results()}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"You voted for **{self.label}**! This is an anonymous poll.",
                ephemeral=True
            )

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Create an interactive poll with up to 5 options.")
    @app_commands.describe(
        question="The poll question",
        option1="First option",
        option2="Second option",
        option3="Third option",
        option4="Fourth option",
        option5="Fifth option",
        status_bar="Show a status bar for votes? (yes/no)",
        anonymous="Make the poll anonymous? (yes/no)"
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
        anonymous: typing.Optional[str] = "no"
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

        status_bar_value = status_bar.lower() if status_bar is not None else "yes"
        anonymous_value = anonymous.lower() if anonymous is not None else "no"
        show_status = status_bar_value == "yes" and anonymous_value != "yes"

        embed = discord.Embed(
            title="📊 Poll",
            description=question,
            color=discord.Color.blurple()
        )
        for idx, opt in enumerate(options, 1):
            embed.add_field(name=f"Option {idx}", value=opt, inline=False)
        if anonymous_value == "yes":
            embed.set_footer(text="This is an anonymous poll. Results will not be shown until the poll ends.")
        elif show_status:
            embed.set_footer(text="Votes are shown live with a status bar.")

        view = PollView(options, show_status)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Polls(bot))