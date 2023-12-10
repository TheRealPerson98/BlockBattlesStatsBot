import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from buttons.paginated_view import PaginatedView
from buttons.paginated_leaderboard_view import PaginatedLeaderboardView
from buttons.tournamentview import TournamentView
from buttons.matchesview import MatchesView
from utils.hotbar_generator import create_hotbar

import aiohttp
from datetime import datetime
import os
import json
import datetime
import random
import asyncio

class Template(commands.Cog, name="template"):
    def __init__(self, bot) -> None:
        self.bot = bot
        
    def find_match_deck(self, matches, match_id, deck_type):
        for match in matches:
            if match["id"] == match_id:
                if deck_type == "winner":
                    return match["winner_deck"]
                elif deck_type == "loser":
                    return match["loser_deck"]
        return None
    
    @commands.hybrid_command(
        name="stats",
        description="Get the statistics of a BlockBattles player.",
    )
    async def stats(self, context: Context, username: str) -> None:
        """
        Get the statistics of a BlockBattles player.

        :param context: The application command context.
        :param username: The username of the player.
        """
        api_url = f"https://api.blockbattles.org/e999a90e7f321d4f4a36ddb9541fa774/blockbattles/stats/{username}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    player_stats = await response.json()
                    data = await response.json()
                    
                    
                    embed = discord.Embed(title=f"📊 Stats for {player_stats['name']}", color=discord.Color.gold())
                    embed.add_field(name="🏆 Ranked Wins", value=player_stats['ranked_wins'], inline=True)
                    embed.add_field(name="🔻 Ranked Losses", value=player_stats['ranked_losses'], inline=True)
                    embed.add_field(name="🎮 Casual Wins", value=player_stats['casual_wins'], inline=True)
                    embed.add_field(name="🚫 Casual Losses", value=player_stats['casual_losses'], inline=True)
                    embed.add_field(name="🎲 Random Wins", value=player_stats['random_wins'], inline=True)
                    embed.add_field(name="⛔ Random Losses", value=player_stats['random_losses'], inline=True)
                    embed.add_field(name="🔥 ELO", value=player_stats['elo'], inline=True)
                    embed.add_field(name="🌟 Streak", value=player_stats['streak'], inline=True)
                    embed.set_footer(text="BlockBattles Statistics", icon_url="https://photos.person98.com/_data/i/upload/2023/11/24/20231124173900-ee9ba338-me.png")  # Replace with an actual icon URL

                    await context.send(embed=embed)
                else:
                    error_embed = discord.Embed(title="❌ Invalid IGN", description="No data found for the provided username.", color=discord.Color.red())
                    await context.send(embed=error_embed)

    
    
    @commands.hybrid_command(
        name="topclans",
        description="Get the top clans in BlockBattles.",
    )
    async def topclans(self, context: Context) -> None:
        api_url = "https://api.blockbattles.org/e999a90e7f321d4f4a36ddb9541fa774/blockbattles/clans"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    clans_data = await response.json()
                    clans_data.sort(key=lambda x: x['clan_elo'], reverse=True)

                    view = PaginatedView(clans_data)
                    embed = await view.get_page_content()
                    await context.send(embed=embed, view=view)
                else:
                    await context.send("An error occurred while fetching data.")

    @commands.hybrid_command(
        name="clan",
        description="Get the details of a specific BlockBattles clan.",
    )
    async def clan(self, context: Context, clan_name: str) -> None:
        """
        Get the details of a specific BlockBattles clan.

        :param context: The application command context.
        :param clan_name: The name of the clan.
        """
        api_url = f"https://api.blockbattles.org/e999a90e7f321d4f4a36ddb9541fa774/blockbattles/clan/{clan_name}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    clan_data = await response.json()
                    leader_name = await self.fetch_username(session, clan_data['leader_uuid'])
                    creation_date = datetime.fromisoformat(clan_data['creation_date'].rstrip('Z')).strftime("%B %d, %Y")
                    embed = discord.Embed(title=f"🛡️ {clan_data['clan_name']} Clan Details", color=discord.Color.green())
                    
                    embed.add_field(name="👑 Leader", value=leader_name, inline=True)
                    embed.add_field(name="🏆 Clan ELO", value=clan_data['clan_elo'], inline=True)
                    embed.add_field(name="📜 Description", value=clan_data['clan_description'], inline=False)
                    embed.add_field(name="🚪 Open to Join", value="Yes" if clan_data['is_open'] else "No", inline=True)
                    embed.add_field(name="📅 Creation Date", value=creation_date, inline=True)
                    members = '\n'.join([f"{await self.fetch_username(session, member['member_uuid'])} ({member['role']})" for member in clan_data['members']])
                    embed.add_field(name="👥 Members", value=members, inline=False)
                    embed.set_footer(text="BlockBattles Statistics", icon_url="https://photos.person98.com/_data/i/upload/2023/11/24/20231124173900-ee9ba338-me.png")  # Replace with an actual icon URL

                    await context.send(embed=embed)
                else:
                    error_embed = discord.Embed(title="❌ Invalid Clan", description="No data found for the provided Clan.", color=discord.Color.red())
                    await context.send(embed=error_embed)
                           
    @commands.hybrid_command(
        name="leaderboard",
        description="Get the BlockBattles player leaderboard.",
    )
    async def leaderboard(self, context: Context) -> None:
        api_url = "https://api.blockbattles.org/e999a90e7f321d4f4a36ddb9541fa774/blockbattles/leaderboard"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    leaderboard_data = await response.json()

                    view = PaginatedLeaderboardView(leaderboard_data)
                    embed = await view.get_page_content()
                    await context.send(embed=embed, view=view)
                else:
                    await context.send("❌ Error: Could not retrieve leaderboard data.")
                    
    async def fetch_username(self, session, uuid):
        mojang_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
        async with session.get(mojang_url) as response:
            if response.status == 200:
                data = await response.json()
                return data['name']
            return "Unknown"
        
    async def fetch_matches(self, name):
        url = f"https://api.blockbattles.org/e999a90e7f321d4f4a36ddb9541fa774/blockbattles/matches/{name}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
                
    
    @commands.hybrid_command(name="matches", description="Get BlockBattles match history.")
    async def matches(self, ctx: commands.Context, name: str):
        matches = await self.fetch_matches(name)
        if not matches:
            await ctx.send("No matches found.")
            return

        pages = [matches[i:i + 8] for i in range(0, len(matches), 8)]
        view = MatchesView(ctx, name, pages)
        embed = await view.get_page_content()
        await ctx.send(embed=embed, view=view)
        
    @commands.hybrid_command(name="matchdeck", description="Get deck of a specific match.")
    @app_commands.choices(deck_type=[
        app_commands.Choice(name="Winner", value="winner"),
        app_commands.Choice(name="Loser", value="loser"),
    ])
    async def matchdeck(self, ctx: commands.Context, name: str, match_id: int, deck_type: str):
        if deck_type not in ["winner", "loser"]:
            await ctx.send("Deck type must be 'winner' or 'loser'.")
            return

        matches = await self.fetch_matches(name)
        if matches is None:
            await ctx.send("No matches found for this player.")
            return

        deck = self.find_match_deck(matches, match_id, deck_type)
        if deck is None:
            await ctx.send(f"No match found with ID {match_id}.")
            return

        # Generate the hotbar image
        image_folder = 'generated_images'
        os.makedirs(image_folder, exist_ok=True)
        image_name = os.path.join(image_folder, f"hotbar_{match_id}_{deck_type}_{random.randint(1000, 9999)}.png")
        create_hotbar(deck, image_name)

        # Send the image in an embed
        file = discord.File(image_name, filename=os.path.basename(image_name))
        embed = discord.Embed(title=f"{deck_type.capitalize()} Deck for Match {match_id}", color=discord.Color.blue())
        embed.set_image(url=f"attachment://{os.path.basename(image_name)}")
        await ctx.send(embed=embed, file=file)

        # Schedule file deletion after 30 seconds
        await asyncio.sleep(30)
        os.remove(image_name)






        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

# Add the cog to the bot
async def setup(bot) -> None:
    await bot.add_cog(Template(bot))
    
