import discord
from discord.ext import commands
from discord.ui import Button, View


class BugReportView(discord.ui.View):
    def __init__(self, db, bug_id, guild_info, bot):
        super().__init__()
        self.db = db
        self.bug_id = bug_id
        self.guild_info = guild_info
        self.bot = bot

    async def handle_interaction(self, interaction, new_status):
        bug_report = self.db.get_bug_by_id(self.bug_id)
        if not bug_report:
            embed = discord.Embed(
                title="Error",
                description="Bug report not found.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        new_channel_id = self.guild_info.get(f'Bugs{new_status.capitalize()}ChannelID')
        new_channel = self.bot.get_channel(int(new_channel_id))

        if new_channel:
            embed = interaction.message.embeds[0]
            new_view = BugReportView(self.db, self.bug_id, self.guild_info, self.bot)
            new_message = await new_channel.send(embed=embed, view=new_view)
            self.db.update_bug(self.bug_id, new_status, str(new_channel.id), str(new_message.id))
            await interaction.message.delete()

            # Send acknowledgment as an embed
            ack_embed = discord.Embed(
                title="Bug Report Updated",
                description=f"Bug report marked as {new_status} and moved.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=ack_embed, ephemeral=True)



    async def delete_bug_report(self, interaction):
        # Delete the bug report from the database
        self.db.delete_bug(self.bug_id)

        # Delete the message from the channel
        await interaction.message.delete()

        # Send acknowledgment as an embed
        ack_embed = discord.Embed(
            title="Bug Report Deleted",
            description="The bug report has been successfully deleted.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=ack_embed, ephemeral=True)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_interaction(interaction, "accepted")

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_interaction(interaction, "denied")

    @discord.ui.button(label="Mark as Fixed", style=discord.ButtonStyle.blurple)
    async def fixed_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_interaction(interaction, "fixed")

    @discord.ui.button(label="Delete Report", style=discord.ButtonStyle.danger)
    async def delete_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.delete_bug_report(interaction)