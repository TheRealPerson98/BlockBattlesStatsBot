import discord
from discord.ext import commands
from discord import app_commands
import json
from data.database import Database 
from datetime import datetime

class JobApplicationView(discord.ui.View):
    def __init__(self, available_jobs, user_id, guild_id, db, config):
        super().__init__()
        self.user_id = user_id
        self.guild_id = guild_id
        self.db = db
        self.config = config

        # Add buttons for each available job
        for job_name, job_desc, job_pay in available_jobs:
            button = discord.ui.Button(label=job_name, style=discord.ButtonStyle.primary)
            button.callback = lambda interaction, button=button: self.button_callback(interaction, button)
            self.add_item(button)

    async def interaction_check(self, interaction) -> bool:
        return str(interaction.user.id) == self.user_id

    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        job_name = button.label

        # Logic to handle job application
        self.db.set_job_info(self.user_id, self.guild_id, job_name, datetime.now().isoformat(), None, 0)

        embed = discord.Embed(title="Job Applied", description=f"You have successfully got the job: {job_name}", color=discord.Color.green())
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ... Rest of your class ...
