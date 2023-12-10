import discord
from discord.ext import commands
from discord import app_commands
import json
from data.database import Database 
import random

class Gambling(commands.Cog, name="gambling"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = Database('data/database.sqlite')  # Path to your database
        with open('config.json') as f:
            self.config = json.load(f)

    @app_commands.command(name="coinflip", description="Flip a coin and bet coins on the outcome.")
    @app_commands.choices(outcome=[
        app_commands.Choice(name="Heads", value="heads"),
        app_commands.Choice(name="Tails", value="tails")
    ])
    async def coinflip(self, interaction: discord.Interaction, outcome: str, coins: int):
        if coins <= 1:
            await interaction.response.send_message("You must bet more than 1 coin.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)
        current_balance = self.db.get_coins(user_id, guild_id)

        if current_balance < coins:
            await interaction.response.send_message("You do not have enough coins to make this bet.", ephemeral=True)
            return

        # Coin flip logic
        result = random.choice(["heads", "tails"])
        if result == outcome:
            new_balance = current_balance + coins
            message = f"The coin landed on {result.capitalize()} and you earned {coins:,} coins\nNew Balance: {new_balance:,}"
        else:
            new_balance = current_balance - coins
            message = f"The coin landed on {result.capitalize()} and you lost {coins:,} coins\nNew Balance: {new_balance:,}"

        self.db.set_coins(user_id, guild_id, new_balance)

        embed = discord.Embed(title="🔄 Coin Flipped", description=message, color=discord.Color.blue())
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
    @app_commands.command(name="slots", description="Gamble a certain amount of your coins on slots.")
    async def slots(self, interaction: discord.Interaction, coins: int):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)
        current_balance = self.db.get_coins(user_id, guild_id)

        if coins <= 1:
            await interaction.response.send_message("You must bet more than 1 coin.", ephemeral=True)
            return

        if coins > current_balance:
            await interaction.response.send_message("You do not have enough coins to play.", ephemeral=True)
            return

        # Slot machine logic
        slots_config = {
            '🍒': {'Chance': 40, 'Multiplier': 0.5},
            '🍋': {'Chance': 30, 'Multiplier': 0.75},
            '🍊': {'Chance': 15, 'Multiplier': 1},
            '🍉': {'Chance': 10, 'Multiplier': 1.5},
            '🍇': {'Chance': 5, 'Multiplier': 2}
        }
        slots_result, winnings = self.play_slots(slots_config, coins)
        new_balance = current_balance - coins + winnings
        self.db.set_coins(user_id, guild_id, new_balance)

        # Creating and sending the embed
        embed = discord.Embed(title="🎰 Slots", color=discord.Color.blue())
        embed.add_field(name="Result", value=slots_result, inline=False)
        embed.add_field(name="Outcome", value=f"You gambled {coins:,} coins and won {winnings:,} coins.\nNew Balance: {new_balance:,}", inline=False)
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    def play_slots(self, config, bet):
        # Calculate the chance ranges for each emoji
        total_chance = sum(emoji['Chance'] for emoji in config.values())
        if total_chance != 100:
            print("Total slot chances do not add up to 100.")
            return "Error", 0

        emojis = list(config.keys())
        chances = [config[emoji]['Chance'] for emoji in emojis]
        ranges = [sum(chances[:i+1]) for i in range(len(chances))]

        # Determine the result of each slot
        result = []
        for _ in range(3):
            rand = random.randint(1, 100)
            for i, upper_bound in enumerate(ranges):
                if rand <= upper_bound:
                    result.append(emojis[i])
                    break

        # Calculate winnings
        winnings = 0
        if result[0] == result[1] == result[2]:
            winnings = int(bet * config[result[0]]['Multiplier'])

        return ' | '.join(result), winnings
# Add the cog to the bot
async def setup(bot) -> None:
    await bot.add_cog(Gambling(bot))
