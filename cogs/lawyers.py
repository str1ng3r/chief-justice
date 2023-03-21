import discord
from discord.ext import commands
from database_managers.LawyerManager import LawyerManager
from web_handlers.MainForumRegistryEditor import MainForumRegistryEditor
from config import MAIN_FORUM_NAME, MAIN_FORUM_PASS
import re
from datetime import datetime


class Lawyers(commands.Cog):
    def __init__(self, client):
        self.client = client
        print("Lawyers module loaded.")

    @commands.command()
    async def reglawyer(self, ctx, *, addition_details):
        if str(ctx.channel) != "bot-commands":
            return 1
        # Splits everything at newline and adds it to a list
        temp_list = addition_details.split('\n')
        addition_details_split = list()
        for item in temp_list:
            addition_details_split.append(item.split(': ')[1])
        # Runs a regular expression on the 2nd element of the list (bar number) and pulls just the numbers
        addition_details_split[1] = re.findall(r"(\d+)", addition_details_split[1])[0]

        # Removes spaces and brackets from discord id
        addition_details_split[-1] = addition_details_split[-1].replace(')', '')
        addition_details_split[-1] = addition_details_split[-1].replace(' ', '')

        # Removes spaces and brackets from forum name
        addition_details_split[-2] = addition_details_split[-2].replace(')', '')
        addition_details_split[-2] = addition_details_split[-2].replace(' ', '')

        lawyer_manager = LawyerManager()
        # Adding the expiry date 2 months in the future
        addition_details_split.append(datetime.now().timestamp() + 5_259_492)
        name_details = addition_details_split[9].split('#')
        member = discord.utils.get(self.client.get_all_members(), name=name_details[0], discriminator=name_details[1])
        if member is None:
            await ctx.send("The specified lawyer is not in the discord server.")
            return 1
        addition_details_split.append(member.id)
        result = await lawyer_manager.add_lawyer(addition_details_split)
        if result == 1:
            await ctx.send("Error with the details you entered.")
        elif result == 2:
            await ctx.send(f"{addition_details_split[0]} is already in the database!")
        else:
            await ctx.send(f"{addition_details_split[0]} (#{addition_details_split[1]}) has been added!")

    @commands.command()
    async def removelawyer(self, ctx, bar_id):
        # Simply removes a lawyer based on his bar id.
        if str(ctx.channel) != "bot-commands":
            return 1
        lawyer_manager = LawyerManager()
        result = await lawyer_manager.remove_lawyer(bar_id)
        if result == 1:
            await ctx.send("There is no lawyer with that bar ID.")
        else:
            await ctx.send(f"{bar_id} has been removed from the registry")

    @removelawyer.error
    async def removelawyer_error(self, ctx, error):
        # Error handling for removing lawyers.
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Correct usage: .removelawyer [bar_id]")

    @commands.command()
    async def editlawyer(self, ctx, bar_id, field, *, details):
        if str(ctx.channel) != "bot-commands":
            return 1
        if field not in ['name', 'bar_id', 'firm', 'specialty', 'availability', 'billing', 'phone', 'email',
                         'forum_name',
                         'discord']:
            await ctx.send("Invalid field.")
            return 1
        lawyer_manager = LawyerManager()
        result = await lawyer_manager.edit_lawyer(bar_id, field, details)
        if result == 1:
            await ctx.send("There is no lawyer with that bar ID.")
        else:
            await ctx.send(f"{bar_id}'s {field} has been changed to {details}")

    @editlawyer.error
    async def editlawyer_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Correct usage: .editlawyer [bar_id] [field] [what you want changed].")
            await ctx.send("Available fields: name, bar_id, firm, specialty, availability, billing, phone, email, "
                           "forum_name, discord")

    @commands.command()
    async def updateregistry(self, ctx):
        if str(ctx.channel) != "bot-commands":
            return 1
        await ctx.send("Updating lawyer registry...")
        reg_editor = MainForumRegistryEditor(MAIN_FORUM_NAME, MAIN_FORUM_PASS)
        await reg_editor.update_forum_post()
        await ctx.send("Registry updated!")


def setup(client):
    client.add_cog(Lawyers(client))
