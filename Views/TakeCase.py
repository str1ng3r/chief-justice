from datetime import datetime

import discord

from utils.models import Case


class TakeCase(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Take case', style=discord.ButtonStyle.green)
    async def take(self, button: discord.ui.Button, interaction: discord.Interaction):
        today = datetime.now()
        case = Case.objects(name=interaction.message.embeds[0].title).first()
        if case is None:
            return
        case.justice = True
        case.handler = interaction.user.id
        case.month = today.month
        case.year = today.year
        case.save()
        await interaction.message.delete()
