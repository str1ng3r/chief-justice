import discord
from discord.ext import commands, tasks
from database_managers.LawyerManager import LawyerManager
from web_handlers.MainForumRegistryEditor import MainForumRegistryEditor
from config import guild_id, main_forum_name, main_forum_pass
from datetime import datetime


class Renewals(commands.Cog):
    def __init__(self, client):
        self.client = client
        print("Renewals module loaded.")
        self.renewal_loop.start()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.client.get_guild(guild_id)
        channel = await guild.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        # Simply checks if a reaction on a case has been sent. The emoji needs to be the same and the open-cases
        # channel.
        if (payload.member != self.client.user and
                str(payload.emoji) == '✅' and
                str(channel.category) == 'BAR RENEWALS' and
                str(message.content) == 'React to this message in order to renew it.'):
            expired_role = discord.utils.get(guild.roles, name="Expired BAR")
            await payload.member.remove_roles(expired_role)
            lm = LawyerManager()
            await lm.renew(channel.name.split('-')[2])
            await channel.delete()
            log_channel = self.client.get_channel_on_guild('bot-logs')
            await log_channel.send(f'{channel.name.split("-")[0].capitalize()}'
                                   f' {channel.name.split("-")[1].capitalize()} has renewed his BAR License.')

    # TASKS

    @tasks.loop(hours=24)
    async def renewal_loop(self):
        # Gets the guild, category, log channel, needed roles and instantiates the lawyer manger
        guild = self.client.get_guild(guild_id)
        category = discord.utils.get(guild.categories, name="BAR RENEWALS")
        log_channel = self.client.get_channel_on_guild('bot-logs')
        lm = LawyerManager()
        bar_attorney_role = discord.utils.get(guild.roles, name="BAR Attorney")
        expired_role = discord.utils.get(guild.roles, name="Expired BAR")

        # Loops through every channel in the BAR RENEWALS category and grabs the lawyer ID from the channel name.
        for channel in category.channels:
            bar_id = channel.name.split('-')[2]
            lawyer = await lm.get_lawyer_by_bar_id(bar_id)
            # If the current date is greater than the expiry date + 5 days, it deletes the channel, lawyer and
            # updates reg
            if datetime.now().timestamp() > lawyer['exp_date'] + 432_000:
                await lm.remove_lawyer(bar_id)
                await channel.delete()
                await log_channel.send(f'{channel.name.split("-")[0].capitalize()}'
                                       f' {channel.name.split("-")[1].capitalize()} has been disbarred for inactivity.')
                member = guild.get_member(lawyer['user_id'])
                await member.remove_roles(bar_attorney_role)
                await member.remove_roles(expired_role)
                reg_editor = MainForumRegistryEditor(main_forum_name, main_forum_pass)
                await reg_editor.update_forum_post()

        # After looping through the channels, it pulls all of the expired lawyers and checks if they already have a
        # channel.
        expired_lawyers = await lm.get_expired_lawyers()
        async for lawyer in expired_lawyers:
            if 'expired' in lawyer:
                continue
            # If they do not have a channel, the expired tag is set and then a channel is created.
            await lm.set_expired_tag(lawyer['bar_id'])
            member = guild.get_member(lawyer['user_id'])

            # Overwrites sets the permissions for the channel to be created.
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True)
            }
            try:
                channel = await guild.create_text_channel(f"{lawyer['name']}-{lawyer['bar_id']}", category=category,
                                                          overwrites=overwrites)
            except AttributeError:
                print(f"Unable to create channel for member {member}")
                continue
            # Edits the expiry date to be the same as when the channel is created.
            await lm.edit_lawyer(lawyer['bar_id'], 'exp_date', datetime.now().timestamp())
            # Adds the expired role and sends the renewal message.
            if member is None:
                await channel.send("User is no longer in the server.")
            await member.add_roles(expired_role)
            await channel.send(f'<@{lawyer["user_id"]}>')
            await channel.send(
                'Your BAR License has expired and it has to be renewed. Failure to renew it within 5 days '
                'will result in disbarment')
            msg = await channel.send('React to this message in order to renew it.')
            await msg.add_reaction('✅')


def setup(client):
    client.add_cog(Renewals(client))
