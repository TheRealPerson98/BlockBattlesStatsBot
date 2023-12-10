import discord
import aiohttp

class PaginatedLeaderboardView(discord.ui.View):
    def __init__(self, leaderboard_data, start_page=0):
        super().__init__()
        self.leaderboard_data = leaderboard_data
        self.current_page = start_page
        self.max_page = len(leaderboard_data) // 10

    async def get_page_content(self):
        start = self.current_page * 10
        end = start + 10
        page_data = self.leaderboard_data[start:end]

        embed = discord.Embed(title="🏆 BlockBattles Leaderboard", color=discord.Color.dark_blue())
        embed.description = f"📄 Page {self.current_page + 1} of {self.max_page + 1}\n\n"
        for i, player in enumerate(page_data, start=start + 1):
            embed.description += f"**#{i} - {player['name']}**\nELO: **{player['elo']}**\n\n"

        embed.set_footer(text="BlockBattles Statistics", icon_url="https://photos.person98.com/_data/i/upload/2023/11/24/20231124173900-ee9ba338-me.png")  # Replace with an actual icon URL
        return embed

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.grey)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            embed = await self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.max_page:
            self.current_page += 1
            embed = await self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
