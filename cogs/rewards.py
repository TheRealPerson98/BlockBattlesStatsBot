import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta
from data.database import Database 

class Rewards(commands.Cog, name="rewards"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = Database('data/database.sqlite')  # Path to your database
        with open('config.json') as f:
            self.config = json.load(f)

    @app_commands.command(name="daily", description="Claim your daily coins.")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)
        last_claimed = self.db.get_daily_reward(user_id, guild_id)
        if last_claimed and datetime.fromisoformat(last_claimed) + timedelta(days=1) > datetime.now():
            await self.send_embed(interaction, "You have already claimed your daily reward.", "error")
            return

        self.db.set_daily_reward(user_id, guild_id)
        current_balance = self.db.get_coins(user_id, guild_id)
        self.db.set_coins(user_id, guild_id, current_balance + 1000)
        await self.send_embed(interaction, "You have successfully claimed 1,000 coins.", "success")

    @app_commands.command(name="weekly", description="Claim your weekly coins.")
    async def weekly(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)
        last_claimed = self.db.get_weekly_reward(user_id, guild_id)
        if last_claimed and datetime.fromisoformat(last_claimed) + timedelta(weeks=1) > datetime.now():
            await self.send_embed(interaction, "You have already claimed your weekly reward.", "error")
            return

        self.db.set_weekly_reward(user_id, guild_id)
        current_balance = self.db.get_coins(user_id, guild_id)
        self.db.set_coins(user_id, guild_id, current_balance + 10000)
        await self.send_embed(interaction, "You have successfully claimed 10,000 coins.", "success")

    async def send_embed(self, interaction, message, embed_type):
        color = discord.Color.green() if embed_type == "success" else discord.Color.red()
        embed = discord.Embed(description=message, color=color)
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        await interaction.response.send_message(embed=embed)

# Add the cog to the bot
async def setup(bot) -> None:
    await bot.add_cog(Rewards(bot))
