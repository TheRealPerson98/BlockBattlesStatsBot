import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from buttons.tournamentview import TournamentView

import aiohttp
from datetime import datetime
import os
import json
import datetime
import random
import asyncio

class Tournament(commands.Cog, name="Tournament"):
    def __init__(self, bot):
        self.bot = bot
        with open('config.json') as f:
            self.config = json.load(f)

    def get_tournaments_test(self):
        return [file.replace('.txt', '') for file in os.listdir('tournaments') if file.endswith('.txt')]
    
    def get_tournaments(self):
        tournament_folder = 'tournaments'
        if not os.path.exists(tournament_folder):
            return []

        tournament_files = os.listdir(tournament_folder)
        tournaments = [os.path.splitext(tournament_file)[0] for tournament_file in tournament_files if tournament_file.endswith('.txt')]
        return tournaments
    
    
    
    
    
    

    @commands.hybrid_group(name="tournament", description="Tournament related commands.")
    @commands.has_permissions(administrator=True)
    async def tournament(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a subcommand (create, delete, makebracket, etc.)")
            
            

    @tournament.command(name="create", description="Create a new tournament.")
    async def create(self, context: commands.Context, tournament_name: str, title: str, description: str, channel: discord.TextChannel):

        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        embed.set_footer(text="BlockBattles Statistics", icon_url="https://photos.person98.com/_data/i/upload/2023/11/24/20231124173900-ee9ba338-me.png")
        view = TournamentView(self.bot, tournament_name)
        
        msg = await channel.send(embed=embed, view=view)

        tournament_messages = {}
        try:
            with open('tournament_message.json', 'r') as f:
                tournament_messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # File not found or empty, we'll create it

        tournament_messages[tournament_name] = {
            'channel_id': channel.id,
            'message_id': msg.id
        }

        with open('tournament_message.json', 'w') as f:
            json.dump(tournament_messages, f)
            
        await context.send(f"✅ tournament '{tournament_name}' started in {channel.mention}")
    
    
    

    @tournament.command(name="delete", description="Delete a specific tournament.")
    async def delete(self, context: Context, tournament_name: str):
        tournament_file_path = f'tournaments/{tournament_name}.txt'
        if os.path.exists(tournament_file_path):
            os.remove(tournament_file_path)

            # Delete the tournament message if it exists
            try:
                with open('tournament_message.json', 'r') as file:
                    tournament_messages = json.load(file)
                    if tournament_name in tournament_messages:
                        channel_id = tournament_messages[tournament_name]['channel_id']
                        message_id = tournament_messages[tournament_name]['message_id']
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            try:
                                msg = await channel.fetch_message(message_id)
                                await msg.delete()
                            except discord.NotFound:
                                pass  # Message already deleted or not found
                        del tournament_messages[tournament_name]

                with open('tournament_message.json', 'w') as file:
                    json.dump(tournament_messages, file)

                await context.send(f"✅ tournament '{tournament_name}' has been deleted.")
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                # File not found or tournament not in file
                pass
        else:
            await context.send("❌ tournament not found.")

    @tournament.command(name="list", description="List all users in a specific tournament.")
    async def list(self, context: Context, tournament_name: str):
        """
        List all users in a specific tournament.

        :param context: The application command context.
        :param tournament_name: The name of the tournament.
        """
        tournament_file_path = f'tournaments/{tournament_name}.txt'
        if not os.path.exists(tournament_file_path):
            await context.send("❌ tournament not found.")
            return

        with open(tournament_file_path, 'r') as f:
            tournament_users = f.readlines()

        if not tournament_users:
            await context.send("The tournament is currently empty.")
            return

        embed = discord.Embed(title=f"📋 Users in the '{tournament_name}' Tournament", color=discord.Color.blue())
        formatted_users = [f"<@{line.split(',')[0].strip()}>" for line in tournament_users]
        embed.description = '\n'.join(formatted_users)
        embed.set_footer(text="BlockBattles Statistics", icon_url="https://photos.person98.com/_data/i/upload/2023/11/24/20231124173900-ee9ba338-me.png")  # Replace with an actual icon URL
        await context.send(embed=embed)
        pass
    
    @tournament.command(name="makebracket", description="Create a tournament bracket.")
    async def make_bracket(self, context: commands.Context, tournament_name: str, round_number: int, channel: discord.TextChannel):
        participants = []
        participant_ids = []
        if round_number == 1:
            # First round: Read participants from the tournament file
            tournament_file_path = f'tournaments/{tournament_name}.txt'
            if not os.path.exists(tournament_file_path):
                await context.send("❌ Tournament not found.")
                return

            with open(tournament_file_path, 'r') as f:
                participant_ids = [line.split(',')[0].strip() for line in f.read().splitlines()]
        else:
            # Subsequent rounds: Read winners from results file
            results_file_path = f'tournaments/results/{tournament_name}_results_{round_number - 1}.txt'
        if not os.path.exists(results_file_path):
            await context.send(f"❌ Results for round {round_number - 1} not found.")
            return

        with open(results_file_path, 'r') as f:
            for line in f:
                if "Winner" in line:
                    winner_id = line.split('Winner ')[1].split(',')[0].strip()  # Correctly isolate the user ID
                    participant_ids.append(winner_id)



        for user_id in participant_ids:
            user = self.bot.get_user(int(user_id))
            if user:
                participants.append(user_id)

        if not participants:
            await context.send("No participants available for this round.")
            return

        # Shuffle and pair participants
        random.shuffle(participants)
        pairs = []
        auto_advance_results = []

        while len(participants) > 1:
            user1_id = participants.pop()
            user2_id = participants.pop()
            if user2_id == 'Pass':
                # Auto-advance user1
                auto_advance_results.append(f"Winner {user1_id}, Loser n/a")
                continue
            pair = f"<@{user1_id}> vs <@{user2_id}>"
            pairs.append(pair)

        if participants:
            user_id = participants.pop()
            auto_advance_results.append(f"Winner {user_id}, Loser n/a")
            pairs.append(f"<@{user_id}> - Pass")

        # Save auto-advanced results
        results_file_path = f'tournaments/results/{tournament_name}_results_{round_number}.txt'
        os.makedirs(os.path.dirname(results_file_path), exist_ok=True)
        with open(results_file_path, 'a') as file:
            for result in auto_advance_results:
                file.write(f"{result}\n")

        # Send bracket to specified channel
        embed = discord.Embed(title=f"🏆 Bracket for '{tournament_name}' Tournament - Round {round_number}", color=discord.Color.blue())
        embed.description = '\n'.join(pairs)
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        msg = await channel.send(embed=embed)

        # Save bracket info
        bracket_info = {'channel_id': channel.id, 'message_id': msg.id}
        bracket_folder = f'tournaments/brackets/{tournament_name}'
        os.makedirs(bracket_folder, exist_ok=True)
        with open(f'{bracket_folder}/round_{round_number}.json', 'w') as f:
            json.dump(bracket_info, f)

        await context.send(f"✅ Bracket for round {round_number} of '{tournament_name}' created in {channel.mention}.")




    
    @tournament.command(name="match", description="Record a match result for a tournament.")
    async def match(self, context: commands.Context, tournament_name: str, winner: discord.Member, loser: discord.Member, round_number: int, channel: discord.TextChannel):
        # Ensure the tournament file exists
        tournament_file_path = f'tournaments/{tournament_name}.txt'
        if not os.path.exists(tournament_file_path):
            await context.send("❌ Tournament not found.")
            return

        # Record the match result
        result_file_path = f'tournaments/results/{tournament_name}_results_{round_number}.txt'
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
        with open(result_file_path, 'a') as file:
            file.write(f"Winner {winner.id}, Loser {loser.id}\n")

        # Check if it's the final match
        is_final_match = False
        with open(result_file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) == 1:  # Only two participants left
                is_final_match = True

        # Fetch the bracket embed to update
        bracket_info_path = f'tournaments/brackets/{tournament_name}/round_{round_number}.json'
        if os.path.exists(bracket_info_path):
            with open(bracket_info_path, 'r') as file:
                bracket_info = json.load(file)
                bracket_channel_id = bracket_info.get('channel_id')
                bracket_message_id = bracket_info.get('message_id')
                bracket_channel = self.bot.get_channel(bracket_channel_id)
                if bracket_channel:
                    try:
                        bracket_message = await bracket_channel.fetch_message(bracket_message_id)
                        updated_embed = bracket_message.embeds[0]  # Assuming the first embed is the bracket embed
                        
                        # Update the embed with the match result
                        new_description = updated_embed.description.replace(f"{winner.mention} vs {loser.mention}", f"{winner.mention} defeated {loser.mention}")
                        updated_embed.description = new_description
                        
                        await bracket_message.edit(embed=updated_embed)
                    except discord.NotFound:
                        await context.send("⚠️ Bracket message not found. Unable to update.")

        # Send match result embed
        embed = discord.Embed(title=f"Match Result - {tournament_name}" "- Round: {round_number}", description=f"{winner.mention} defeated {loser.mention}" , color=discord.Color.green())
        embed.set_footer(text="BlockBattles Tournament", icon_url=self.config["footer_icon_url"])
        await channel.send(embed=embed)

        # If final match, announce the overall winner
        if is_final_match:
            final_embed = discord.Embed(title=f"🏆 {tournament_name} - Tournament Winner", description=f"Congratulations to {winner.mention} for winning the tournament!", color=discord.Color.gold())
            final_embed.set_footer(text="BlockBattles Tournament", icon_url=self.config["footer_icon_url"])
            await bracket_channel.send(embed=final_embed)

        await context.send(f"✅ Match result recorded for round {round_number} of tournament '{tournament_name}'.")



    
    
    
    
    @match.autocomplete('tournament_name')
    async def delete_autocomplete(self, interaction: discord.Interaction, current: str):
        tournaments = self.get_tournaments()
        return [app_commands.Choice(name=tournament, value=tournament) for tournament in tournaments if current.lower() in tournament.lower()]
    
    @list.autocomplete('tournament_name')
    async def delete_autocomplete(self, interaction: discord.Interaction, current: str):
        tournaments = self.get_tournaments()
        return [app_commands.Choice(name=tournament, value=tournament) for tournament in tournaments if current.lower() in tournament.lower()]
    
    @delete.autocomplete('tournament_name')
    async def delete_autocomplete(self, interaction: discord.Interaction, current: str):
        tournaments = self.get_tournaments()
        return [app_commands.Choice(name=tournament, value=tournament) for tournament in tournaments if current.lower() in tournament.lower()]
    
    @make_bracket.autocomplete('tournament_name')
    async def delete_autocomplete(self, interaction: discord.Interaction, current: str):
        tournaments = self.get_tournaments()
        return [app_commands.Choice(name=tournament, value=tournament) for tournament in tournaments if current.lower() in tournament.lower()]
async def setup(bot) -> None:
    await bot.add_cog(Tournament(bot))
