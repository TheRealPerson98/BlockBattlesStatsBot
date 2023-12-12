import discord
from discord.ui import View, Select
from discord.ext import commands
import asyncio
import json
import os
import sys


from views.applicationreviewview import ApplicationReviewView
class ApplicationSelect(Select):
    def __init__(self, applications, db, bot):
        super().__init__(placeholder="Choose an application...", min_values=1, max_values=1)
        self.options = [
            discord.SelectOption(label=app, description=f"Apply for {app}", emoji="✅") 
            for app in applications
        ]
        self.db = db
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        app_name = self.values[0]

        # Check if Application feature is enabled
        guild_features = self.db.get_guild_features(str(interaction.guild_id))
        if not guild_features.get('Application', False):
            await interaction.response.send_message("Application feature is not enabled in this server.", ephemeral=True)
            return

        guild_info = self.db.get_all_guild_info(str(interaction.guild_id))
        app_category_id = guild_info.get('ApplicationCategoryID')
        if not app_category_id:
            await interaction.response.send_message("Application category is not set up.", ephemeral=True)
            return

        # Create or find a channel for the application process
        category = self.bot.get_channel(int(app_category_id))
        if not category:
            await interaction.response.send_message("Application category not found.", ephemeral=True)
            return

        # Ensure the user can view the channel and others cannot
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
            
        }
        channel_topic = "**User:** {interaction.user.display_name} **Applying for: ** {app_name}"
        app_channel = await interaction.guild.create_text_channel(f"{app_name}-App-{interaction.user.display_name}", category=category, overwrites=overwrites, topic=channel_topic)
        
        
        application_channel_embed = discord.Embed(
            title=f"Application for {app_name}",
            description=f"Your application will take place in {app_channel.mention}. Please proceed there to continue.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=application_channel_embed, ephemeral=True)
        

        
        application_id = self.db.add_application(str(interaction.guild_id), app_name, str(interaction.user.id), str(app_channel.id))

        # Start the application process in the channel
        file_path = f'applications/{app_name}.json'
        if not os.path.exists(file_path):
            await interaction.response.send_message("Application form not found.", ephemeral=True)
            return

        with open(file_path, 'r') as file:
            application_data = json.load(file)
        questions = application_data.get("questions", [])

        # Start the application process in the channel
        await app_channel.send(embed=discord.Embed(
            title=f"Application for {app_name}",
            description=f"{interaction.user.mention}, let's start your application. Please answer the following questions:",
            color=discord.Color.blue()
        ))

        responses = {}
        for question in questions:
            await app_channel.send(embed=discord.Embed(
                title="Question",
                description=question,
                color=discord.Color.green()
            ))

            def check(m):
                return m.author == interaction.user and m.channel == app_channel

            try:
                response = await self.bot.wait_for('message', check=check, timeout=300)  # 5 minutes timeout
                responses[question] = response.content
            except asyncio.TimeoutError:
                await app_channel.send(embed=discord.Embed(
                    title="Timeout",
                    description="You took too long to respond. Application process terminated.",
                    color=discord.Color.red()
                ))
                return

        # Clear the channel messages
        await app_channel.purge(limit=None)

        # Post a summary embed with all responses
        summary_description = "\n\n".join([f"**Question:** {q}\n**Response:** {a}" for q, a in responses.items()])
        summary_embed = discord.Embed(
            title=f"Application for {app_name}",
            description=summary_description,
            color=discord.Color.gold()
        )
        summary_embed.set_footer(text=f"Application by: {interaction.user.display_name}")

        # Create an instance of ApplicationReviewView with necessary parameters
        application_review_view = ApplicationReviewView(self.db, app_channel.id, interaction.user.id, self.bot, guild_id=interaction.guild_id)

        # Send the summary embed with the view
        sent_message = await app_channel.send(embed=summary_embed, view=application_review_view)

        # Log the application review message in the database
        self.db.log_application_review_message(str(interaction.guild_id), str(app_channel.id), str(sent_message.id), application_id)