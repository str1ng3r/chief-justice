import discord
from discord.ext import commands, tasks
from datetime import datetime
from discord.errors import Forbidden
from database_managers.ReminderManager import ReminderManager
from config import GUILD_ID


class Reminders(commands.Cog):
    def __init__(self, client):
        self.client = client
        print('Reminders module loaded.')
        self.reminder_task.start()        

    @commands.command()
    async def reminder(self, ctx, days: int, hours: int, minutes: int, reminder_text: str):
        # Converts the time inputted by the command into seconds, grabs the current timestamp and adds it, to form
        # The future reminder date.
        total_seconds: float = days * 86400 + hours * 3600 + minutes * 60
        current_timestamp = datetime.now().timestamp()
        final_timestamp = current_timestamp + total_seconds
        reminder_manager = ReminderManager()
        # Creates the reminder in the database and replies to the message.
        await reminder_manager.create_reminder(ctx.author.id, final_timestamp, reminder_text)
        await reminder_manager.close()
        await ctx.send("Reminder added!")

    @reminder.error
    async def reminder_error(self, ctx, error):
        # Error handling for wrong input.
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Correct usage: .reminder [days] [hours] [minutes] [reminder details]")

    @commands.command()
    async def remindme(self, ctx, days: int, hours: int, minutes: int):
        # It's basically the same idea as the reminder command, but instead it works when you reply to a message.
        if not ctx.message.reference:
            await ctx.send("In order to use this command, you need to reply to a message.")
        else:
            total_seconds: float = days * 86400 + hours * 3600 + minutes * 60
            current_timestamp = datetime.now().timestamp()
            final_timestamp = current_timestamp + total_seconds
            reminder_manager = ReminderManager()
            await reminder_manager.create_reminder(ctx.author.id, final_timestamp, ctx.message.reference.jump_url)
            await reminder_manager.close()
            await ctx.reply("Reminder added!")

    @remindme.error
    async def remindme_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Correct usage: .remindme [days] [hours] [minutes]")

    @tasks.loop(minutes=2)
    async def reminder_task(self):
        # The task loops every 2 minutes, grabbing all reminders and looping through them.
        reminder_manager = ReminderManager()
        reminders = await reminder_manager.get_all_reminders()
        for rem in reminders:
            # Checks if the reminder is expired.
            if rem['reminder_date'] < datetime.now().timestamp():
                # Gets an user object using the user id.
                user = await self.client.fetch_user(rem['user_id'])
                # Creates a direct message channel.
                dm = await user.create_dm()
                if "https://discord.com/channels/" in rem['reminder_text']:
                    description = f"[ACCESS]({rem['reminder_text']})"
                    footer = "Click to go to message"
                else:
                    description = rem['reminder_text']
                    footer = ""
                # Create the embed and sends it in a private message, proceeding to delete the reminder from the db.
                embed = discord.Embed(title="Reminder alert", description=description, color=0x60fc38)
                embed.set_author(name="Chief Justice", icon_url="https://i.imgur.com/0wDghTQ.png")
                embed.set_footer(text=footer)
                try:
                    await dm.send(embed=embed)
                except Forbidden:
                    print(f"Unable to send reminder private message to: {user}")
                await reminder_manager.delete_reminder(rem['_id'])
        await reminder_manager.close()


def setup(client):
    client.add_cog(Reminders(client))
