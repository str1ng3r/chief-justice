from datetime import datetime

import discord.ui

from utils.models import Reminder


class RemindMeModal(discord.ui.Modal):
    def __init__(self, message: discord.message, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.message = message

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
        reminder = Reminder(user_id=interaction.user.id, reminder_date=final_timestamp,
                            reminder_text=self.message.jump_url)
        reminder.save()
        await interaction.response.send_message("Reminder set!")
