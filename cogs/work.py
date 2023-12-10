import discord
from discord.ext import commands
from discord import app_commands
import json
from data.database import Database
from buttons.jobapplicationview import JobApplicationView
from datetime import datetime, timedelta
import random
import math

class Work(commands.Cog, name="work"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = Database('data/database.sqlite')  # Path to your database
        with open('config.json') as f:
            self.config = json.load(f)

    @commands.hybrid_group(name="job", description="Job related commands.")
    async def job(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                description="Please specify a subcommand.\n\n**Subcommands:**\n`apply` - Apply for a job.\n`work` - Work at your job.\n`quit` - Quit your job.",
                color=discord.Color.blue()
            )
            embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
            await ctx.send(embed=embed)

    @job.command(name="apply", description="Apply for a job.")
    async def job_apply(self, ctx: commands.Context) -> None:
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Check current school level
        school_info = self.db.get_school_info(user_id, guild_id)
        if not school_info:
            embed = discord.Embed(title="No School Record", description="You need to be in school to apply for a job.", color=discord.Color.red())
            embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
            await ctx.send(embed=embed)
            return

        school_type = school_info[0]

        # Check if the user already has a job
        job_info = self.db.get_job_info(user_id, guild_id)
        if job_info and job_info[0]:
            embed = discord.Embed(title="Already Employed", description="You already have a job. Quit your current job to apply for a new one.", color=discord.Color.orange())
            embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
            await ctx.send(embed=embed)
            return

        jobs_by_school_level = {
            "elementary": [],
            "middle": [
                ("Picking weeds", "A simple job for young students.", 2),
                ("Cleaning sheds", "Help clean and organize sheds.", 3)
            ],
            "high": [
                ("Library Assistant", "Assist in managing the school library.", 5),
                ("Cafeteria Helper", "Help in the school cafeteria.", 4),
                ("Tutoring", "Tutor younger students.", 6)
            ],
            "college": [
                ("Research Assistant", "Assist in academic research.", 8),
                ("Campus Guide", "Help newcomers navigate the campus.", 7),
                ("Tech Support", "Provide tech support at the IT desk.", 9)
            ],
            "graduate": [
                ("Teaching Assistant", "Assist professors in teaching.", 10),
                ("Lab Technician", "Work in the university labs.", 12),
                ("Intern at a Company", "Intern at a local business.", 11),
                ("Campus Coordinator", "Manage campus events and activities.", 13),
                ("Graduate Researcher", "Conduct your own research.", 15)
            ]
        }


        available_jobs = jobs_by_school_level.get(school_type, [])

        if not available_jobs:
            embed = discord.Embed(title="No Available Jobs", description="There are no available jobs for your school level.", color=discord.Color.red())
            embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
            await ctx.send(embed=embed)
            return

        # Create job application embed
        embed = discord.Embed(title="Job Application", description="Select a job to apply for:", color=discord.Color.green())
        for job, description, pay in available_jobs:
            embed.add_field(name=job, value=f"{description}\nCoins per hour: {pay}", inline=False)
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])


        # Create a view for job application
        view = JobApplicationView(available_jobs, user_id, guild_id, self.db, self.config)

        # Send the embed and view
        await ctx.send(embed=embed, view=view, ephemeral=True)

    @job.command(name="work", description="Work at your job.")
    async def job_work(self, ctx: commands.Context) -> None:
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Retrieve job info from the database
        job_info = self.db.get_job_info(user_id, guild_id)
        if not job_info or not job_info[0]:
            embed = discord.Embed(
                title="No Job",
                description="You do not have a job. Apply for one to start working.",
                color=discord.Color.red()
            )
            embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
            await ctx.send(embed=embed)
            return

        job_name, date_got_job, last_worked, amount_worked = job_info
        if last_worked:
            last_worked_date = datetime.fromisoformat(last_worked)
            next_available_time = last_worked_date + timedelta(hours=24)
            if datetime.now() < next_available_time:
                time_remaining = next_available_time - datetime.now()
                hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                embed = discord.Embed(
                    title="Too Soon",
                    description=f"You have already worked in the last 24 hours. You can work again in {hours} hours and {minutes} minutes.",
                    color=discord.Color.orange()
                )
                embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
                await ctx.send(embed=embed)
                return


        # Random hours worked between 8 and 12
        hours_worked = random.randint(8, 12)
        amount_worked += hours_worked
        # Calculate pay based on job
        base_pay_per_hour = {
            "Picking weeds": 2,
            "Cleaning sheds": 3,
            "Library Assistant": 5,
            "Cafeteria Helper": 4,
            "Tutoring": 6,
            "Research Assistant": 8,
            "Campus Guide": 7,
            "Tech Support": 9,
            "Teaching Assistant": 10,
            "Lab Technician": 12,
            "Intern at a Company": 11,
            "Campus Coordinator": 13,
            "Graduate Researcher": 15,
        }
        promotion_thresholds = {
            50: ("Jr", 0.1),  # 10% pay bump
            160: ("Middle Management", 0.25),  # 25% pay bump
            300: ("Higher up", 0.3),  # 30% pay bump
            500: ("Board Member", 0.5),  # 50% pay bump
            1000: ("CEO", 0.7),  # 70% pay bump
        }
        base_job_name = next((job for job in base_pay_per_hour if job_name.startswith(job)), None)
        
        print(base_job_name)
        
    # Check for promotion
        promotion_title = ""
        pay_bump = 0
        for threshold, (title, bump) in promotion_thresholds.items():
            if amount_worked >= threshold:
                promotion_title = title
                pay_bump = bump

        # Update job title with promotion, if any
        new_job_name = f"{base_job_name} {promotion_title}" if promotion_title else base_job_name
        if job_name != new_job_name:
            job_name = new_job_name
            embed = discord.Embed(
                title="Promotion",
                description=f"Congratulations! You've been promoted to {job_name}.",
                color=discord.Color.green()
            )
            embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
            await ctx.send(embed=embed)

        # Calculate pay
        pay_per_hour = base_pay_per_hour[base_job_name] * (1 + pay_bump)
        total_pay = math.ceil(hours_worked * pay_per_hour)

        # Update coins
        current_coins = self.db.get_coins(user_id, guild_id)
        self.db.set_coins(user_id, guild_id, current_coins + total_pay)

        # Update job info with the new last worked date and amount worked
        self.db.set_job_info(user_id, guild_id, job_name, date_got_job, datetime.now().isoformat(), amount_worked)

        # Send success message
        embed = discord.Embed(
            title="Work Completed",
            description=f"You worked for {hours_worked} hours as a {job_name} and earned {total_pay:,} coins.",
            color=discord.Color.green()
        )
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        await ctx.send(embed=embed)

    @job.command(name="quit", description="Quit your job.")
    async def job_quit(self, ctx: commands.Context) -> None:
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Retrieve job info from the database
        job_info = self.db.get_job_info(user_id, guild_id)
        if not job_info or not job_info[0]:
            embed = discord.Embed(
                title="No Job",
                description="You do not currently have a job to quit.",
                color=discord.Color.red()
            )
            embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
            await ctx.send(embed=embed)
            return

        job_name, date_got_job, _, _ = job_info
        employment_duration = datetime.now() - datetime.fromisoformat(date_got_job)
        days_employed = employment_duration.days

        # Remove the job from the database
        self.db.remove_job(user_id, guild_id)

        # Confirmation message
        embed = discord.Embed(
            title="Job Quit",
            description=f"You have successfully quit your job as a {job_name}, which you had for {days_employed} days.",
            color=discord.Color.green()
        )
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        await ctx.send(embed=embed)

    @job.command(name="info", description="Shows information about your current job.")
    async def job_info(self, ctx: commands.Context) -> None:
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Retrieve job info from the database
        job_info = self.db.get_job_info(user_id, guild_id)
        if not job_info or not job_info[0]:
            embed = discord.Embed(
                title="No Job",
                description="You do not currently have a job.",
                color=discord.Color.red()
            )
            embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
            await ctx.send(embed=embed)
            return

        job_name, date_got_job, last_worked, amount_worked = job_info
        start_date = datetime.fromisoformat(date_got_job).strftime('%Y-%m-%d')
        last_worked_date = datetime.fromisoformat(last_worked).strftime('%Y-%m-%d') if last_worked else 'N/A'

        # Determine hours until next promotion
        promotion_thresholds = [50, 160, 300, 500, 1000]
        next_promotion_threshold = next((threshold for threshold in promotion_thresholds if amount_worked < threshold), None)
        hours_until_next_promotion = next_promotion_threshold - amount_worked if next_promotion_threshold else 0

        embed = discord.Embed(
            title="Job Information",
            description=f"**Job Title:** {job_name}\n"
                        f"**Hours Worked:** {amount_worked}\n"
                        f"**Start Date:** {start_date}\n"
                        f"**Last Worked:** {last_worked_date}\n"
                        f"**Hours Until Next Promotion:** {hours_until_next_promotion}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        await ctx.send(embed=embed)
        



# Add the cog to the bot
async def setup(bot) -> None:
    await bot.add_cog(Work(bot))
