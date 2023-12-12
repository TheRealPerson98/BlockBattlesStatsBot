import discord
from discord.ext import commands
from discord import app_commands
from data.database import Database

class Setup(commands.Cog, name="setup"):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database('data/database.sqlite')

    @commands.hybrid_group(name="setup", description="Setup configurations for your server.")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a subcommand (channels, categories, guild_features).")

    @setup.command(name="channels", description="Set up channel configurations for your server.")
    @app_commands.choices(channel_type=[
        app_commands.Choice(name="Suggestions Channel ID", value="SuggestionsChannelID"),
        app_commands.Choice(name="Accepted Suggestions Channel ID", value="AcceptedSuggestionsChannelID"),
        app_commands.Choice(name="Denied Suggestions Channel ID", value="DeniedSuggestionsChannelID"),
        app_commands.Choice(name="Implemented Suggestions Channel ID", value="ImplementedSuggestionsChannelID"),
        app_commands.Choice(name="Mod Commands Channel ID", value="ModCommandsChannelID"),
        app_commands.Choice(name="Log Channel ID", value="LogChannelID"),
        app_commands.Choice(name="Bug Pending Channel ID", value="BugPendingChannelID"),
        app_commands.Choice(name="Bugs Accepted Channel ID", value="BugsAcceptedChannelID"),
        app_commands.Choice(name="Bugs Denied Channel ID", value="BugsDeniedChannelID"),
        app_commands.Choice(name="Bugs Fixed Channel ID", value="BugsFixedChannelID"),
    ])
    async def setup_channels(self, context: commands.Context, channel_type: str, channel: discord.TextChannel):
        channel_id = channel.id
        self.db.set_guild_info(str(context.guild.id), **{channel_type: channel_id})

        embed = discord.Embed(
            title="Channel Setup Complete",
            description=f"{channel_type} has been set to {channel.mention} (ID: {channel_id}).",
            color=discord.Color.green()  # Emerald color
        )
        await context.send(embed=embed)

    @setup.command(name="categories", description="Set up category configurations for your server.")
    @app_commands.choices(category_type=[
        app_commands.Choice(name="Ticket Category ID", value="TicketCategoryChannelID"),
        app_commands.Choice(name="Suggestion Category ID", value="SuggestionCategoryID"),
        app_commands.Choice(name="Bug Category ID", value="BugCategoryID"),
        app_commands.Choice(name="Application Category ID", value="ApplicationCategoryID"),

    ])
    async def setup_categories(self, context: commands.Context, category_type: str, category_id: str):
        # Ensure the category_id is a valid integer (Discord ID)
        try:
            category_id = int(category_id)
        except ValueError:
            embed = discord.Embed(
                title="Invalid Category ID",
                description="Please provide a valid category ID.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return

        # Update the GuildInfo table with the provided category ID
        self.db.set_guild_info(str(context.guild.id), **{category_type: category_id})

        # Send confirmation message as an embed
        embed = discord.Embed(
            title="Category Setup Complete",
            description=f"{category_type} has been set to ID: {category_id}.",
            color=discord.Color.green()  # Emerald color
        )
        await context.send(embed=embed)

    @setup.command(name="guild_features", description="Toggle various guild features.")
    @app_commands.choices(
        feature=[
            app_commands.Choice(name="Ticket", value="Ticket"),
            app_commands.Choice(name="Suggestion", value="Suggestion"),
            app_commands.Choice(name="Application", value="Application"),
            app_commands.Choice(name="Bugs", value="Bugs"),
            app_commands.Choice(name="Log", value="Log"),
        ],
        value=[
            app_commands.Choice(name="True", value="True"),
            app_commands.Choice(name="False", value="False"),
        ]
    )
    async def setup_guild_features(self, context: commands.Context, feature: str, value: str):
        # Convert the string value to boolean
        boolean_value = True if value == "True" else False

        # Update the GuildFeatures table with the provided boolean value
        self.db.set_guild_feature(str(context.guild.id), feature, boolean_value)

        # Send confirmation message as an embed
        embed = discord.Embed(
            title="Guild Feature Setup Complete",
            description=f"Feature '{feature}' has been set to {'enabled' if boolean_value else 'disabled'}.",
            color=discord.Color.green()  # Emerald color
        )
        await context.send(embed=embed)
        
        
    @setup.command(name="doitforme", description="Automatically set up channels and categories.")
    @commands.has_permissions(administrator=True)
    async def setup_do_it_for_me(self, context: commands.Context):
        guild_id = str(context.guild.id)
        guild_features = self.db.get_guild_features(guild_id)

        if not isinstance(guild_features, dict):
            await context.send("Error: Guild features data is not in the expected format.")
            return

        # Send initial embed indicating the start of the setup
        start_embed = discord.Embed(
            title="Automatic Setup Started",
            description="Beginning the process of setting up channels and categories...",
            color=discord.Color.blue()
        )
        await context.send(embed=start_embed)

        for feature, is_enabled in guild_features.items():
            if is_enabled:
                await self.create_default_channel_or_category(context.guild, feature)

        # Send final embed once setup is complete
        complete_embed = discord.Embed(
            title="Automatic Setup Complete",
            description="Channels and categories have been set up as needed.",
            color=discord.Color.green()
        )
        await context.send(embed=complete_embed)

    async def create_default_channel_or_category(self, guild, feature):
        guild_id = str(guild.id)

        if feature == 'Ticket':
            everyone_role = guild.default_role
            overwrites = {
                everyone_role: discord.PermissionOverwrite(read_messages=False)
            }
            ticket_category = await guild.create_category("Tickets", overwrites=overwrites)
            self.db.set_guild_info(guild_id, TicketCategoryChannelID=ticket_category.id)

        if feature == 'Suggestion':
            # Create Suggestion Category and Channels
            suggestion_category = await guild.create_category("Suggestions")
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)
            }

            # Create each channel under the Suggestion category
            suggestions_channel = await guild.create_text_channel("suggestions", category=suggestion_category, overwrites=overwrites)
            accepted_suggestions_channel = await guild.create_text_channel("accepted-suggestions", category=suggestion_category, overwrites=overwrites)
            denied_suggestions_channel = await guild.create_text_channel("denied-suggestions", category=suggestion_category, overwrites=overwrites)
            implemented_suggestions_channel = await guild.create_text_channel("implemented-suggestions", category=suggestion_category, overwrites=overwrites)

            # Update the GuildInfo table with the new channel IDs
            self.db.set_guild_info(guild_id, 
                                   SuggestionCategoryID=suggestion_category.id, 
                                   SuggestionsChannelID=suggestions_channel.id,
                                   AcceptedSuggestionsChannelID=accepted_suggestions_channel.id,
                                   DeniedSuggestionsChannelID=denied_suggestions_channel.id,
                                   ImplementedSuggestionsChannelID=implemented_suggestions_channel.id)

        elif feature == 'Application':
            # Get the @everyone role
            everyone_role = guild.default_role
            overwrites = {
                everyone_role: discord.PermissionOverwrite(read_messages=False)
            }
            application_category = await guild.create_category("Applications", overwrites=overwrites)

            self.db.set_guild_info(guild_id, ApplicationCategoryID=application_category.id)


        elif feature == 'Bugs':
            everyone_role = guild.default_role
            overwrites = {
                everyone_role: discord.PermissionOverwrite(read_messages=False)
            }
            bugs_category = await guild.create_category("Bugs")
            bug_pending_channel = await guild.create_text_channel("bug-pending", category=bugs_category, overwrites=overwrites)
            bugs_accepted_channel = await guild.create_text_channel("bugs-accepted", category=bugs_category, overwrites=overwrites)
            bugs_denied_channel = await guild.create_text_channel("bugs-denied", category=bugs_category, overwrites=overwrites)
            bugs_fixed_channel = await guild.create_text_channel("bugs-fixed", category=bugs_category, overwrites=overwrites)
            self.db.set_guild_info(guild_id, BugCategoryID=bugs_category.id, BugPendingChannelID=bug_pending_channel.id, BugsAcceptedChannelID=bugs_accepted_channel.id, BugsDeniedChannelID=bugs_denied_channel.id, BugsFixedChannelID=bugs_fixed_channel.id)

        elif feature == 'Log':
            # Create Log Channel
            log_channel = await guild.create_text_channel("log")
            self.db.set_guild_info(guild_id, LogChannelID=log_channel.id)

            
            
            
            
async def setup(bot) -> None:
    await bot.add_cog(Setup(bot))
