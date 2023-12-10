"""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""

import json
import logging
import os
import platform
import random
import sys

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv
import aiohttp
from buttons.tournamentview import TournamentView
from data.database import Database

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
        config = json.load(file)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True



class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(config["prefix"]),
            intents=intents,
            help_command=None,
        )
        self.logger = logger
        self.config = config

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        statuses = ["with you!", "with Krypton!", "with humans!"]
        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()
        
        
        
        
        
        
    async def fetch_server_stats(self):
        url = "https://api.mcsrvstat.us/3/play.blockbattles.org"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None

    @tasks.loop(minutes=5.0)
    async def update_mc_server_stats(self):
        server_stats = await self.fetch_server_stats()
        if not server_stats:
            return

        status = "Online" if server_stats.get("online") else "Offline"
        players = server_stats.get("players", {})
        online_players = players.get("online", 0)
        max_players = players.get("max", 0)

        guild = self.get_guild(1175988635737280542)  # Replace with your guild ID
        if guild:
            category = discord.utils.get(guild.categories, name="Server Stats")
            if not category:
                category = await guild.create_category("Server Stats")

            # Set permissions so @everyone cannot connect
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=False)
            }

            # Function to identify and update/create channels
            async def get_or_create_channel(name_prefix, new_name):
                for channel in guild.voice_channels:
                    if channel.name.startswith(name_prefix) and channel.category_id == category.id:
                        return await channel.edit(name=new_name)
                return await guild.create_voice_channel(new_name, category=category, overwrites=overwrites)

            # Update/create status channel
            await get_or_create_channel("Status -", f"Status - {status}")

            # Update/create players channel
            await get_or_create_channel("Players -", f"Players - {online_players}/{max_players}")

            # Update/create IP channel
            await get_or_create_channel("IP -", "IP - Play.BlockBattles.org")
            

    @update_mc_server_stats.before_loop
    async def before_update_mc_server_stats(self):
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        """
        This will just be executed when the bot starts the first time.
        """
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        await self.load_cogs()
        self.status_task.start()
        self.update_mc_server_stats.start() 
        db_path = 'data/database.sqlite'
        database = Database(db_path)
        database._initialize_db()
        
    async def on_ready(self):
        try:
            with open('tournament_message.json', 'r') as f:
                tournament_messages = json.load(f)

            for tournament_name, info in tournament_messages.items():
                channel = self.get_channel(info['channel_id'])
                if channel:
                    try:
                        msg = await channel.fetch_message(info['message_id'])
                        # Reattach the view to the existing message
                        view = TournamentView(self, tournament_name)
                        await msg.edit(view=view)
                        print(f"Tournament embed for '{tournament_name}' already exists.")
                    except discord.NotFound:
                        # Message does not exist, resend
                        await self.resend_tournament_embed(channel, tournament_name)
        except (FileNotFoundError, json.JSONDecodeError):
            # File not found or invalid, handle appropriately
            pass

    async def resend_tournament_embed(self, channel, tournament_name):
        # Logic to resend the embed
        embed = discord.Embed(title=f"{tournament_name}", description="Tournament details here", color=discord.Color.blue())
        # Customize your embed as needed
        embed.set_footer(text="BlockBattles Statistics", icon_url=self.config["footer_icon_url"])
        view = TournamentView(self, tournament_name)  # Make sure TournamentView is defined or imported
        msg = await channel.send(embed=embed, view=view)

        # Update the JSON file with the new message
        with open('tournament_message.json', 'r+') as f:
            tournament_messages = json.load(f)
            tournament_messages[tournament_name] = {'channel_id': channel.id, 'message_id': msg.id}
            f.seek(0)
            json.dump(tournament_messages, f)
            f.truncate()
        
    async def on_message(self, message: discord.Message) -> None:
        """
        The code in this event is executed every time someone sends a message, with or without the prefix

        :param message: The message that was sent.
        """
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        """
        The code in this event is executed every time a normal command has been *successfully* executed.

        :param context: The context of the command that has been executed.
        """
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            self.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )

    async def on_command_error(self, context: Context, error) -> None:
        """
        The code in this event is executed every time a normal valid command catches an error.

        :param context: The context of the normal command that failed executing.
        :param error: The error that has been faced.
        """
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                description="You are not the owner of the bot!", color=0xE02B2B
            )
            await context.send(embed=embed)
            if context.guild:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
                )
            else:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
                )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="You are missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to execute this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="I am missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to fully perform this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error!",
                # We need to capitalize because the command arguments have no capital letter in the code and they are the first word in the error message.
                description=str(error).capitalize(),
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        else:
            raise error


load_dotenv()

bot = DiscordBot()
bot.run(os.getenv("TOKEN"))
