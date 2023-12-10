import discord
from discord.ext import commands
from discord import app_commands
import json
from data.database import Database
from datetime import datetime, timedelta

class Life(commands.Cog, name="life"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = Database('data/database.sqlite')  # Path to your database
        with open('config.json') as f:
            self.config = json.load(f)

    async def send_embed(self, interaction, description, color=discord.Color.blue(), timestamp=None):
        embed = discord.Embed(description=description, color=color)
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        if timestamp:
            embed.timestamp = timestamp
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="gotoschool", description="Go to school and progress through education.")
    async def gotoschool(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)
        school_info = self.db.get_school_info(user_id, guild_id)

        if not school_info:
            self.db.set_school_info(user_id, guild_id, "elementary", 0, datetime.now().isoformat())
            await self.send_embed(interaction, "You're now in elementary school!")
            return

        school_type, progress, last_date = school_info
        last_date = datetime.fromisoformat(last_date)
        days_passed = (datetime.now() - last_date).days

        days_required = {"elementary": 1, "middle": 2, "high": 4, "college": 4}

        if days_passed < days_required[school_type]:
            next_date = last_date + timedelta(days=days_required[school_type])
            await self.send_embed(interaction, f"You need to spend more time in {school_type} school. You can go to school again on {next_date.strftime('%Y-%m-%d')}.", discord.Color.red(), timestamp=next_date)
            return

        next_school_stage = {"elementary": "middle", "middle": "high", "high": "college", "college": "graduate"}
        new_school_type = next_school_stage.get(school_type, school_type)
        self.db.set_school_info(user_id, guild_id, new_school_type, progress + days_passed, datetime.now().isoformat())

        if new_school_type == "graduate":
            await self.send_embed(interaction, "Congratulations, you've graduated!")
        else:
            await self.send_embed(interaction, f"You're now in {new_school_type} school!")

# Add the cog to the bot
async def setup(bot) -> None:
    await bot.add_cog(Life(bot))
