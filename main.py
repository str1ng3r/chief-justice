import os
from abc import ABC

import discord
from discord import Option
from discord.ext import commands
from mongoengine import connect

from config import BOT_TOKEN, DISABLED_COGS, GUILD_ID, DB_CONN_STRING, DATABASE

intents = discord.Intents.all()
connect(DB_CONN_STRING, db=DATABASE)


class Bot(commands.Bot, ABC):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=intents)
        self.guild = None

    def get_channel_on_guild(self, channel_name):
        channel_guild = discord.utils.get(self.get_all_channels(), name=channel_name).guild
        channel_id = discord.utils.get(self.get_all_channels(), name=channel_name).id
        return channel_guild.get_channel(channel_id)

    @staticmethod
    def get_cog_list():
        """
        This static method loops through all of the files in the cogs directory and appends them to a list without
        their .py extension.
        :return: List containing the names of all the cogs.
        """
        cog_list = list()
        for file in os.listdir('./cogs'):
            if file.endswith('.py'):
                cog_list.append(file[:-3])
        return cog_list

    async def on_ready(self):
        print("Bot is up.")


def main():
    client = Bot()
    cog_list = client.get_cog_list()
    for cog in cog_list:
        if cog not in DISABLED_COGS:
            client.load_extension(f'cogs.{cog}')

    cog_list = client.get_cog_list()

    # COMMANDS

    @client.slash_command(guild_ids=[GUILD_ID], description='Loads a module.')
    @commands.has_permissions(administrator=True)
    async def load(ctx, extension: Option(str, 'Select module', choices=cog_list)):
        client.load_extension(f'cogs.{extension}')
        await ctx.respond(f'{str(extension).capitalize()} loaded!')

    @client.slash_command(guild_ids=[GUILD_ID], description='Unloads a module.')
    @commands.has_permissions(administrator=True)
    async def unload(ctx, extension: Option(str, 'Select module', choices=cog_list)):
        client.unload_extension(f'cogs.{extension}')
        await ctx.respond(f'{str(extension).capitalize()} unloaded!')

    @client.slash_command(guild_ids=[GUILD_ID], description='Reloads a module.')
    @commands.has_permissions(administrator=True)
    async def reload(ctx, extension: Option(str, 'Select module', choices=cog_list)):
        client.reload_extension(f'cogs.{extension}')
        await ctx.respond(f'{str(extension).capitalize()} reloaded!')

    @client.slash_command(guild_ids=[GUILD_ID], description='Displays all modules. Bold modules are currently loaded.')
    @commands.has_permissions(administrator=True)
    async def modules(ctx):
        enabled_modules = [x[5:] for x in client.extensions]
        module_list = list()
        for module in cog_list:
            if module in enabled_modules:
                module_list.append(f'**{module.capitalize()}**')
            else:
                module_list.append(module.capitalize())
        final_response = ', '.join(module_list)
        await ctx.respond(final_response)


    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('Command not found.')

    client.run(BOT_TOKEN)


if __name__ == '__main__':
    main()
