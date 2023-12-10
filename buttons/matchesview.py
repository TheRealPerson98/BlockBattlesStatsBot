import discord
import datetime

class MatchesView(discord.ui.View):
    def __init__(self, ctx, name, pages, current_page=0):
        super().__init__()
        self.ctx = ctx
        self.name = name
        self.pages = pages
        self.current_page = current_page

    async def get_page_content(self):
        page = self.pages[self.current_page]
        embed = discord.Embed(title=f"Matches for {self.name}", color=discord.Color.blue())
        matches_info = ""
        for match in page:
            match_time = datetime.datetime.fromtimestamp(int(float(match["match_time"]))/1000.0).strftime('%Y-%m-%d %H:%M:%S')
            matches_info += f"ID: {match['id']} | Winner: {match['winner_name']} | Loser: {match['loser_name']} | Date: {match_time}\n"
        embed.add_field(name=f"Matches", value=matches_info, inline=False)
        return embed

    @discord.ui.button(label='Previous', style=discord.ButtonStyle.grey)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            embed = await self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            embed = await self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)
