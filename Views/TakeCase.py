import discord


class TakeCase(discord.ui.View):
    def __init__(self, case_manager):
        super().__init__(timeout=None)
        self.case_manager = case_manager

    @discord.ui.button(label='Take case', style=discord.ButtonStyle.green)
    async def take(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.case_manager.make_unavailable(interaction.message.embeds[0].title, interaction.user.id)
        self.stop()
        await interaction.message.delete()
