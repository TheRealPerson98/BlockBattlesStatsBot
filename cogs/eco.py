import discord
from discord.ext import commands
from discord import app_commands
import json
from data.database import Database 
from buttons.coinleaderboardview import CoinLeaderboardView
class Eco(commands.Cog, name="eco"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = Database('data/database.sqlite')  # Path to your database
        with open('config.json') as f:
            self.config = json.load(f)

    @app_commands.command(name="coins", description="Displays a user's coin balance.")
    async def coins(self, interaction: discord.Interaction, member: discord.Member = None):
        # Determine if the command is for the caller or another user
        is_self = member is None or member.id == interaction.user.id
        member = member or interaction.user
        coins = self.db.get_coins(str(member.id), str(interaction.guild_id))

        embed = discord.Embed(title=f"{member.display_name}'s Coins", color=discord.Color.blue())

        # Adjust the description based on who the command is for
        if is_self:
            embed.description = f"You currently have {coins:,} coins"
        else:
            embed.description = f"{member.display_name} currently has {coins:,} coins"

        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])

        await interaction.response.send_message(embed=embed)

        
    @app_commands.command(name="pay", description="Pay coins to another user.")
    async def pay(self, interaction: discord.Interaction, amount: int, member: discord.Member):
        if amount <= 0:
            embed = discord.Embed(description="Amount must be greater than zero.", color=discord.Color.red())
            embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        sender_id = str(interaction.user.id)
        receiver_id = str(member.id)
        guild_id = str(interaction.guild_id)

        sender_balance = self.db.get_coins(sender_id, guild_id)
        if sender_balance < amount:
            embed = discord.Embed(description="You do not have enough coins to make this payment.", color=discord.Color.red())
            embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Update sender and receiver's balance
        self.db.set_coins(sender_id, guild_id, sender_balance - amount)
        receiver_balance = self.db.get_coins(receiver_id, guild_id)
        self.db.set_coins(receiver_id, guild_id, receiver_balance + amount)

        # Send success message as an embed
        embed = discord.Embed(description=f"You have successfully paid {amount:,} coins to {member.display_name}.", color=discord.Color.green())
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="givecoins", description="Give coins to a user.")
    @app_commands.checks.has_permissions(administrator=True)
    async def givecoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("Amount must be greater than zero.", ephemeral=True)
            return

        user_id = str(member.id)
        guild_id = str(interaction.guild_id)

        # Update user's balance
        current_balance = self.db.get_coins(user_id, guild_id)
        self.db.set_coins(user_id, guild_id, current_balance + amount)

        embed = discord.Embed(description=f"Successfully given {amount:,} coins to {member.display_name}.", color=discord.Color.green())
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removecoins", description="Remove coins from a user.")
    @app_commands.checks.has_permissions(administrator=True)
    async def removecoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("Amount must be greater than zero.", ephemeral=True)
            return

        user_id = str(member.id)
        guild_id = str(interaction.guild_id)

        # Update user's balance
        current_balance = self.db.get_coins(user_id, guild_id)
        new_balance = max(current_balance - amount, 0)  # Prevent negative balance
        self.db.set_coins(user_id, guild_id, new_balance)

        embed = discord.Embed(description=f"Successfully removed {amount:,} coins from {member.display_name}.", color=discord.Color.green())
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="coinstop", description="Displays the coin leaderboard.")
    async def coinstop(self, interaction: discord.Interaction):
        view = CoinLeaderboardView(self.db, self)
        embed = await view.get_page_content()
        await interaction.response.send_message(embed=embed, view=view)

        
# Add the cog to the bot
async def setup(bot) -> None:
    await bot.add_cog(Eco(bot))
