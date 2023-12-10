import discord
from discord.ext import commands
from discord import app_commands
import json
from data.database import Database 

class CoinLeaderboardView(discord.ui.View):
    def __init__(self, db, ctx, current_page=0):
        super().__init__()
        self.db = db
        self.ctx = ctx
        self.current_page = current_page

    async def get_page_content(self):
        start_index = self.current_page * 15
        end_index = start_index + 15
        leaderboard_data = self.db.get_top_coins(start_index, end_index)

        total_coins = sum([entry[2] for entry in leaderboard_data])
        embed = discord.Embed(title=f"👑 Coin Leaderboard (Page {self.current_page + 1})", color=discord.Color.blue())

        for rank, entry in enumerate(leaderboard_data, start=start_index + 1):
            user_id = int(entry[0])
            coins = entry[2]
            user = await self.ctx.bot.fetch_user(user_id)
            embed.add_field(name=f"{rank}. {user.display_name}", value=f"{coins:,} coins", inline=True)

        embed.set_footer(text=self.ctx.config["footer_text"], icon_url=self.ctx.config["footer_icon_url"])
        return embed


    @discord.ui.button(label='Previous', style=discord.ButtonStyle.grey)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            embed = await self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Assuming there's a method in your database class to get the total number of unique users
        total_pages = (self.db.get_unique_users_count() - 1) // 15
        if self.current_page < total_pages:
            self.current_page += 1
            embed = await self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)

