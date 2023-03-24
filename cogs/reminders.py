import discord
from discord.ext import commands, tasks
from datetime import datetime
from discord.errors import Forbidden

from UI.remindme_modal import RemindMeModal
from utils.models import Reminder
from config import GUILD_ID


class Reminders(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.reminder_task.start()
        print('Reminders module loaded.')

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def reminder(self, ctx, days: int, hours: int, minutes: int, reminder_text: str):
        # Converts the time inputted by the command into seconds, grabs the current timestamp and adds it, to form
        # The future reminder date.
        total_seconds: float = days * 86400 + hours * 3600 + minutes * 60
        current_timestamp = datetime.now().timestamp()
        final_timestamp = current_timestamp + total_seconds
        reminder = Reminder(user_id=ctx.author.id, reminder_date=final_timestamp, reminder_text=reminder_text)
        reminder.save()
        await ctx.respond("Reminder added!")

    @discord.message_command(name="Set a reminder")
    async def remindme(self, ctx, message: discord.message):
        modal = RemindMeModal(message, title="Set a reminder")
        await ctx.send_modal(modal)

    @tasks.loop(minutes=2)
    async def reminder_task(self):
        # The task loops every 2 minutes, grabbing all reminders and looping through them.
        for rem in Reminder.objects:
            # Checks if the reminder is expired.
            if rem.reminder_date > datetime.now().timestamp():
                continue
            # Gets a user object using the user id.
            user = await self.client.fetch_user(rem.user_id)
            # Creates a direct message channel.
            dm = await user.create_dm()
            if "https://discord.com/channels/" in rem.reminder_text:
                description = f"[ACCESS]({rem.reminder_text})"
                footer = "Click to go to message"
            else:
                description = rem.reminder_text
                footer = ""
            # Create the embed and sends it in a private message, proceeding to delete the reminder from the db.
            embed = discord.Embed(title="Reminder alert", description=description, color=0x60fc38)
            embed.set_author(name="Chief Justice", icon_url="https://i.imgur.com/0wDghTQ.png")
            embed.set_footer(text=footer)
            try:
                await dm.send(embed=embed)
            except Forbidden:
                print(f"Unable to send reminder private message to: {user}")

            # Delete the reminder.
            rem.delete()


def setup(client):
    client.add_cog(Reminders(client))
