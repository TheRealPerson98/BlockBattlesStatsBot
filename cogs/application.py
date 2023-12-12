import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import json
import os
import asyncio
from views.applicationselect import ApplicationSelect
from discord.ui import View, Select
from data.database import Database
import logging


class Application(commands.Cog, name="application"):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database('data/database.sqlite')
        
    @commands.hybrid_group(
        name="application",
        description="Manage application.",
    )
    async def application(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("You can manage applications using /application [subcommand]")

    @application.command(name="create")
    @commands.has_permissions(administrator=True)
    async def create(self, ctx: commands.Context):
        # Inform the user to check their DMs
        embed = discord.Embed(
            title="Application Creation Process Started",
            description="Please check your DMs to create a new application form.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

        # Start the application creation process in DMs
        def check(m):
            return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

        # Ask for the name of the application
        await ctx.author.send(embed=discord.Embed(
            title="Application Name",
            description="What is the name of the Application?",
            color=discord.Color.green()
        ))

        try:
            app_name_msg = await self.bot.wait_for('message', check=check, timeout=300)
            app_name = app_name_msg.content.strip()
        except asyncio.TimeoutError:
            await ctx.author.send(embed=discord.Embed(
                title="Timeout",
                description="You took too long to respond. Application creation process terminated.",
                color=discord.Color.red()
            ))
            return

        # Ask for application questions
        application_questions = []
        await ctx.author.send(embed=discord.Embed(
            title="Application Questions",
            description="Write a question or type 'Done' to finish adding questions.",
            color=discord.Color.green()
        ))

        print("Asking for questions...")  # Debug print

        while True:
            try:
                print("Waiting for a question...")  # Debug print
                question_msg = await self.bot.wait_for('message', check=check, timeout=300)
                question = question_msg.content.strip()
                print(f"Received question: {question}")  # Debug print
                
                await ctx.author.send(embed=discord.Embed(
                    title="Application Questions",
                    description="Write a question or type 'Done' to finish adding questions.",
                    color=discord.Color.green()
                ))
                
                if question.lower() == 'done':
                    print("Done received, breaking out of loop")  # Debug print
                    break
                application_questions.append(question)
            except asyncio.TimeoutError:
                await ctx.author.send(embed=discord.Embed(
                    title="Timeout",
                    description="You took too long to respond. Application creation process terminated.",
                    color=discord.Color.red()
                ))
                print("Timeout occurred")  # Debug print
                return

        # Save the application structure
        self.save_application_structure(ctx.author.id, app_name, application_questions)
        await ctx.author.send(embed=discord.Embed(
            title="Application Structure Saved",
            description="The application structure has been successfully saved.",
            color=discord.Color.green()
        ))

    def save_application_structure(self, user_id, app_name, application_questions):
        os.makedirs('applications', exist_ok=True)
        safe_app_name = "".join([c for c in app_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        file_path = f'applications/{safe_app_name}.json'
        with open(file_path, 'w') as file:
            json.dump({"name": app_name, "questions": application_questions}, file, indent=4)
        print(f"Application structure saved: {file_path}")
    
    
    
    def get_applications(self):
        """Retrieve a list of application names from the applications directory."""
        application_files = os.listdir('applications')
        return [os.path.splitext(file)[0] for file in application_files]

    @application.command(name="delete")
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx: commands.Context, app_name: str):
        """Delete a specific application."""
        file_path = f'applications/{app_name}.json'
        if os.path.exists(file_path):
            os.remove(file_path)
            await ctx.send(embed=discord.Embed(
                title="Application Deleted",
                description=f"The application '{app_name}' has been deleted.",
                color=discord.Color.green()
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title="Error",
                description=f"No application found with the name '{app_name}'.",
                color=discord.Color.red()
            ))

    @delete.autocomplete('app_name')
    async def delete_autocomplete(self, interaction: discord.Interaction, current: str):
        applications = self.get_applications()
        return [app_commands.Choice(name=application, value=application) for application in applications if current.lower() in application.lower()]

    @application.command(name="prefiew")
    @commands.has_permissions(administrator=True)
    async def prefiew(self, ctx: commands.Context, app_name: str):
        """View a specific application."""
        file_path = f'applications/{app_name}.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                application_data = json.load(file)
            # Format and send the application data
            questions_formatted = "\n".join(application_data.get("questions", []))
            embed = discord.Embed(
                title=f"Application: {application_data.get('name', 'Unknown')}",
                description=f"**Questions:**\n{questions_formatted}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed, ephemeral=True)
        else:
            await ctx.send(embed=discord.Embed(
                title="Error",
                description=f"No application found with the name '{app_name}'.",
                color=discord.Color.red()
            ), ephemeral=True)



    @application.command(name="sendembed")
    @commands.has_permissions(administrator=True)
    async def sendembed(self, ctx: commands.Context, channel: discord.TextChannel):
        applications = self.get_applications()
        select_menu = ApplicationSelect(applications, self.db, self.bot)
        view = View()
        view.add_item(select_menu)
        
        embed = discord.Embed(
            title="Application Process",
            description="To apply for roles, staff positions, etc., please select an option from the dropdown menu.",
            color=discord.Color.blue()
        )

        message = await channel.send(embed=embed, view=view)

        # Save the message ID to a file
        with open("data/application_message_info.txt", "w") as file:
            file.write(f"{message.id},{channel.id}")

        # Send confirmation to admin
        confirm_embed = discord.Embed(
            title="Embed Sent",
            description=f"The application embed has been sent to {channel.mention}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=confirm_embed, ephemeral=True)

    @application.command(name="deleteembed")
    @commands.has_permissions(administrator=True)
    async def deleteembed(self, ctx: commands.Context):
        try:
            with open("data/application_message_info.txt", "r") as file:
                data = file.read().strip().split(',')
                if len(data) != 2:
                    raise ValueError("Invalid data format in application_message_info.txt")

            message_id, channel_id = data
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                message = await channel.fetch_message(int(message_id))
                await message.delete()

                # Clearing the file after successful deletion
                with open("data/application_message_info.txt", "w") as file:
                    file.write("")

                confirm_embed = discord.Embed(
                    title="Embed Deleted",
                    description=f"The application embed in {channel.mention} has been successfully deleted.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=confirm_embed, ephemeral=True)
            else:
                await ctx.send(embed=discord.Embed(
                    title="Error",
                    description="Channel not found.",
                    color=discord.Color.red()
                ), ephemeral=True)
        except FileNotFoundError:
            await ctx.send(embed=discord.Embed(
                title="Error",
                description="No application embed information found.",
                color=discord.Color.red()
            ), ephemeral=True)
        except discord.NotFound:
            await ctx.send(embed=discord.Embed(
                title="Error",
                description="Message not found in the specified channel.",
                color=discord.Color.red()
            ), ephemeral=True)
        except Exception as e:
            await ctx.send(embed=discord.Embed(
                title="Error",
                description=f"An error occurred: {e}",
                color=discord.Color.red()
            ), ephemeral=True)


    @prefiew.autocomplete('app_name')
    async def view_autocomplete(self, interaction: discord.Interaction, current: str):
        """Provide autocomplete options for application names."""
        applications = self.get_applications()
        return [app_commands.Choice(name=application, value=application) for application in applications if current.lower() in application.lower()]

    @application.command(name="accept")
    @commands.has_permissions(administrator=True)
    async def accept(self, ctx: commands.Context):
        """Accept an application based on the channel it's run in."""
        application = self.db.get_application_by_channel_id(ctx.channel.id)
        if application:
            user = ctx.guild.get_member(int(application['UserID']))
            if user:
                try:
                    await user.send(embed=discord.Embed(
                        title="Application Accepted",
                        description=f"Your application for '{application['AppName']}' has been accepted.",
                        color=discord.Color.green()
                    ))

                    # Send embedded message in the channel
                    await ctx.channel.send(embed=discord.Embed(
                        title="Application Accepted",
                        description=f"{user.mention}, your application for '{application['AppName']}' has been accepted.",
                        color=discord.Color.green()
                    ))

                    # Rename the channel to include 'accepted-'
                    await ctx.channel.edit(name=f"accepted-{ctx.channel.name}")

                except discord.HTTPException as e:
                    await ctx.send(embed=discord.Embed(
                        title="Error",
                        description=f"Failed to send DM to the user. Error: {e}",
                        color=discord.Color.red()
                    ))
            else:
                await ctx.send(embed=discord.Embed(
                    title="Error",
                    description="User not found in the guild.",
                    color=discord.Color.red()
                ))


    @application.command(name="deny")
    @commands.has_permissions(administrator=True)
    async def deny(self, ctx: commands.Context):
        """Deny an application based on the channel it's run in."""
        application = self.db.get_application_by_channel_id(ctx.channel.id)
        if application:
            user = ctx.guild.get_member(int(application['UserID']))
            if user:
                await user.send(embed=discord.Embed(
                    title="Application Denied",
                    description=f"Your application for '{application['AppName']}' has been denied.",
                    color=discord.Color.red()
                ))

                # Send embedded message in the channel
                await ctx.channel.send(embed=discord.Embed(
                    title="Application Denied",
                    description=f"{user.mention}, your application for '{application['AppName']}' has been denied.",
                    color=discord.Color.red()
                ))

                # Rename the channel to include 'denied-'
                await ctx.channel.edit(name=f"denied-{ctx.channel.name}")
                
    @application.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx: commands.Context):
        """Delete an application and its channel."""
        application = self.db.get_application_by_channel_id(ctx.channel.id)
        if application:
            await ctx.channel.delete(reason="Application deleted")
            self.db.delete_application(application['ApplicationID'])
            self.db.delete_application_review_message(ctx.channel.id)
        else:
            await ctx.send(embed=discord.Embed(
                title="Error",
                description="No application found for this channel.",
                color=discord.Color.red()
            ))
    
async def setup(bot):
    await bot.add_cog(Application(bot))
