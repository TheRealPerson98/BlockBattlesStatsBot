from discord.ext import commands
from discord.ext.commands import Context
from data.database import Database
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import datetime
from views.bugreportbiew import BugReportView
import datetime

class Bugs(commands.Cog, name="bugs"):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database('data/database.sqlite')

    @commands.hybrid_command(
        name="reportbug",
        description="Report a bug to the developers.",
    )
    @app_commands.describe(bug='Description of the bug', video_link='Optional video link showcasing the bug')
    async def reportbug(self, ctx: Context, bug: str, video_link: str = None):
        # Check if the bug feature is enabled
        guild_features = self.db.get_guild_features(str(ctx.guild.id))
        if not guild_features.get('Bugs', False):
            await ctx.send("Bug reporting is currently disabled in this server.", ephemeral=True)
            return

        # Get the channel ID for pending bugs
        guild_info = self.db.get_all_guild_info(str(ctx.guild.id))
        bug_pending_channel_id = guild_info.get('BugPendingChannelID')
        if not bug_pending_channel_id:
            await ctx.send("Bug reporting channel is not set up. Please contact an administrator.", ephemeral=True)
            return

        bug_pending_channel = self.bot.get_channel(int(bug_pending_channel_id))
        if bug_pending_channel:
            # Prepare the embed
            embed = discord.Embed(
                title="New Bug Report",
                description=f"**Reported by:** {ctx.author.mention}\n\n**Bug:**\n{bug}\n\n",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            if video_link:
                embed.description += f"**Video Link:** [Click Here]({video_link})\n\n"
            if ctx.message.attachments:
                embed.description += "**Attachments:**\n"
                for attachment in ctx.message.attachments:
                    embed.description += f"[{attachment.filename}]({attachment.url})\n"

            embed.set_thumbnail(url=ctx.author.avatar.url)
            embed.set_footer(text=f"Reported on: {datetime.datetime.now().strftime('%d/%m/%Y')}")

            # Send the bug report and attach the BugReportView
            message = await bug_pending_channel.send(embed=embed)

            # Add the bug report to the database and get its ID
            bug_id = self.db.add_bug(str(ctx.guild.id), str(ctx.author.id), str(message.id), str(bug_pending_channel.id), bug)

            # Create and attach the view for bug report management
            view = BugReportView(self.db, bug_id, guild_info, self.bot)
            await message.edit(view=view)

            # Send confirmation embed to the user
            confirm_embed = discord.Embed(
                title="Bug Report Submitted",
                description="Your bug report has been successfully submitted to the developers.",
                color=discord.Color.green()
            )
            await ctx.send(embed=confirm_embed, ephemeral=True)
        else:
            await ctx.send("Bug reporting channel not found.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Bugs(bot))