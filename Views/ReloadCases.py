import discord


class ReloadCases(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.reload_fag = False
        self.cog = cog

    @discord.ui.button(label='Reload cases', style=discord.ButtonStyle.blurple)
    async def reload(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.stop()
        await interaction.response.defer()
        await self.cog.reload_cases()
