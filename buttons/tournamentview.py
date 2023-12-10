import os
import discord
from discord.ext import commands
from discord.ui import Button, View

class TournamentView(View):
    def __init__(self, bot, tournament_name):
        super().__init__(timeout=None)
        self.bot = bot
        self.tournament_name = tournament_name
        self.tournament_file_path = f'tournaments/{tournament_name}.txt'
        os.makedirs(os.path.dirname(self.tournament_file_path), exist_ok=True)
        self.load_tournament()

    def load_tournament(self):
        self.tournament = []
        if os.path.exists(self.tournament_file_path):
            with open(self.tournament_file_path, 'r') as f:
                for line in f:
                    user_id, user_name = line.strip().split(', ')
                    self.tournament.append((int(user_id), user_name))

    async def send_embed(self, interaction: discord.Interaction, description: str, color: discord.Color):
        embed = discord.Embed(description=description, color=color)
        embed.set_footer(text="BlockBattles Statistics", icon_url="https://photos.person98.com/_data/i/upload/2023/11/24/20231124173900-ee9ba338-me.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label='Join tournament', style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: Button):
        user = interaction.user
        if (user.id, user.name) not in self.tournament:
            self.tournament.append((user.id, user.name))
            with open(self.tournament_file_path, 'a') as f:
                f.write(f'{user.id}, {user.name}\n')
            await self.send_embed(interaction, 'You joined the tournament.', discord.Color.green())
        else:
            await self.send_embed(interaction, 'You are already in the tournament.', discord.Color.orange())

    @discord.ui.button(label='Leave tournament', style=discord.ButtonStyle.red)
    async def leave_button(self, interaction: discord.Interaction, button: Button):
        user = interaction.user
        if (user.id, user.name) in self.tournament:
            self.tournament.remove((user.id, user.name))
            with open(self.tournament_file_path, 'w') as f:
                for user_id, user_name in self.tournament:
                    f.write(f'{user_id}, {user_name}\n')
            await self.send_embed(interaction, 'You left the tournament.', discord.Color.red())
        else:
            await self.send_embed(interaction, 'You are not in the tournament.', discord.Color.orange())
