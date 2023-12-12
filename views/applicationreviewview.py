import discord
from discord.ui import View, Button

class ApplicationReviewView(View):
    def __init__(self, db, channel_id, user_id, client, guild_id):
        super().__init__()
        self.db = db
        self.channel_id = channel_id
        self.user_id = user_id
        self.client = client
        self.guild_id = guild_id  # Store the guild_id
        self.application = self.db.get_application_by_channel_id(channel_id)

        if not self.application:
            print(f"No application found for channel ID {self.channel_id}")
            return

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.application:
            print("Application not found.")
            return

        try:
            guild = await self.client.fetch_guild(self.guild_id)
            if not guild:
                print("Guild not found.")
                return

            user_id = int(self.application['UserID'])
            user = await guild.fetch_member(user_id)
            if not user:
                print("User not found in the guild.")
                return
            
            channel = await self.client.fetch_channel(self.channel_id)

            await user.send(embed=discord.Embed(
                title="Application Accepted",
                description=f"Your application for '{self.application['AppName']}' has been accepted.",
                color=discord.Color.green()
            ))
            emebed = discord.Embed(
                title="Application Accepted",
                description=f"{user.mention}'s application for '{self.application['AppName']}' has been accepted.",
                color=discord.Color.green()
            )
            await channel.send(embed=emebed)
            
            embed = discord.Embed(
                title="Application Accepted",
                description=f"You accepted {user.mention}'s application for '{self.application['AppName']}'.",
                color=discord.Color.green()  # You can set the color as per your preference
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Logic for accepting the application
            if channel:
                await channel.edit(name=f"accepted-{channel.name}")
            else:
                print("Channel not found in interaction.")
                
            
            
        except discord.HTTPException as e:
            print(f"Discord HTTP exception occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.application:
            print("Application not found.")
            return

        try:
            guild = await self.client.fetch_guild(self.guild_id)
            if not guild:
                print("Guild not found.")
                return

            user_id = int(self.application['UserID'])
            user = await guild.fetch_member(user_id)
            if not user:
                print("User not found in the guild.")
                return
            
            channel = await self.client.fetch_channel(self.channel_id)

            await user.send(embed=discord.Embed(
                title="Application Denied",
                description=f"Your application for '{self.application['AppName']}' has been denied.",
                color=discord.Color.green()
            ))
            emebed = discord.Embed(
                title="Application Denied",
                description=f"{user.mention}'s application for '{self.application['AppName']}' has been denied.",
                color=discord.Color.green()
            )
            await channel.send(embed=emebed)
            
            embed = discord.Embed(
                title="Application Denied",
                description=f"You denied {user.mention}'s application for '{self.application['AppName']}'.",
                color=discord.Color.green()  # You can set the color as per your preference
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Logic for accepting the application
            if channel:
                await channel.edit(name=f"denied-{channel.name}")
            else:
                print("Channel not found in interaction.")
                
            
            
        except discord.HTTPException as e:
            print(f"Discord HTTP exception occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    @discord.ui.button(label="Delete", style=discord.ButtonStyle.grey)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.application:
            print("Application not found.")
            return
        try:
            guild = await self.client.fetch_guild(self.guild_id)
            if not guild:
                print("Guild not found.")
                return

            user_id = int(self.application['UserID'])
            user = await guild.fetch_member(user_id)
            if not user:
                print("User not found in the guild.")
                return
            
            channel = await self.client.fetch_channel(self.channel_id)
            self.db.delete_application(self.application['ApplicationID'])
            self.db.delete_application_review_message(channel.id)
            await channel.delete()
            
        except discord.HTTPException as e:
            print(f"Discord HTTP exception occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
