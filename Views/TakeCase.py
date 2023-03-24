import discord

from database_managers.CaseManager import CaseManager


class TakeCase(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Take case', style=discord.ButtonStyle.green)
    async def take(self, button: discord.ui.Button, interaction: discord.Interaction):
        async with CaseManager() as cm:
            await cm.make_unavailable(interaction.message.embeds[0].title, interaction.user.id)
        self.stop()
        await interaction.message.delete()
