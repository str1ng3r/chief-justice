from datetime import datetime

import discord.ui

from database_managers.ReminderManager import ReminderManager


class RemindMeModal(discord.ui.Modal):
    def __init__(self, cog, message: discord.message, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.message = message
        self.cog_instance = cog

        self.add_item(discord.ui.InputText(label="Days", placeholder='0'))
        self.add_item(discord.ui.InputText(label="Hours", placeholder='0'))
        self.add_item(discord.ui.InputText(label="Minutes", placeholder='0'))

    async def callback(self, interaction: discord.Interaction):
        input_valid = [child.value.isdigit() for child in self.children]
        if not all(input_valid):
            await interaction.response.send_message("All inputs must be numbers.", ephemeral=True)
            return

        days = int(self.children[0].value)
        hours = int(self.children[1].value)
        minutes = int(self.children[2].value)

        total_seconds: float = days * 86400 + hours * 3600 + minutes * 60
        current_timestamp = datetime.now().timestamp()
        final_timestamp = current_timestamp + total_seconds
        async with ReminderManager() as rm:
            await rm.create_reminder(interaction.user.id, final_timestamp, self.message.jump_url)
            await self.cog_instance.get_reminders()
        await interaction.response.send_message("Reminder set!")
