import discord
import aiohttp

class PaginatedView(discord.ui.View):
    def __init__(self, clans_data, start_page=0):
        super().__init__()
        self.clans_data = clans_data
        self.current_page = start_page
        self.max_page = len(clans_data) // 10

    async def fetch_username(self, uuid):
        mojang_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
        async with aiohttp.ClientSession() as session:
            async with session.get(mojang_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['name']
                return "Unknown"

    async def get_page_content(self):
        start = self.current_page * 10
        end = start + 10
        page_data = self.clans_data[start:end]

        for clan in page_data:
            clan['leader_name'] = await self.fetch_username(clan['leader_uuid'])

        embed = discord.Embed(title="🛡️ Top Clans in BlockBattles", description=f"📄 Page {self.current_page + 1}/{self.max_page + 1}", color=discord.Color.blue())
        for clan in page_data:
            embed.add_field(name=f"🏰 {clan['clan_name']}", value=f"👑 Leader: {clan.get('leader_name', 'Unknown')}\n🏆 ELO: {clan['clan_elo']}", inline=True)

        embed.set_footer(text="BlockBattles Statistics", icon_url="https://photos.person98.com/_data/i/upload/2023/11/24/20231124173900-ee9ba338-me.png")  # Replace with an actual icon URL
        embed.timestamp = discord.utils.utcnow()
        return embed


    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            embed = await self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.max_page:
            self.current_page += 1
            embed = await self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
