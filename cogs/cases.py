import discord
from discord.ext import commands, tasks
from database_managers.CaseManager import CaseManager
from web_handlers.MainForumScraper import MainForumScraper
from config import main_forum_name, main_forum_pass
from Views.TakeCase import TakeCase
from Views.ReloadCases import ReloadCases


class Cases(commands.Cog):
    def __init__(self, client):
        self.client = client
        print("Cases module loaded.")
        self.cases_refresh.start()

    # COMMANDS

    @commands.command()
    async def reloadcases(self, ctx):
        # Checks if the command is executed in the bot-commands channel
        if str(ctx.channel) == "bot-commands":
            await self.reload_cases()
            await ctx.send("Case list reloaded.")

    async def reload_cases(self):
        # It grabs the "open-cases" channel from all the channels.
        bot_channel = self.client.get_channel_on_guild('open-cases')
        # Purges it then grabs the cases using the forum scraper.
        await bot_channel.purge()
        await bot_channel.send("Cases that currently have no judge:")
        case_manager = CaseManager()

        # Scrapes the forum in each of the three sections and the upload them to the database
        main_forum_scraper = MainForumScraper(main_forum_name, main_forum_pass)
        await main_forum_scraper.get_cases('criminal')
        await bot_channel.send("Received criminal cases...")
        await main_forum_scraper.get_cases('civil')
        await bot_channel.send("Received civil cases...")
        await main_forum_scraper.get_cases('traffic')
        await bot_channel.send("Received traffic cases...")

        # Grabs all the available cases from the database
        cases = await case_manager.get_available_cases()
        async for case in cases:
            if case['case_type'] == 'traffic':
                clr = 0x2e2eff
            elif case['case_type'] == 'civil':
                clr = 0x00d100
            else:
                clr = 0xd10000
            emb = discord.Embed(title=case['name'], description=f"[ACCESS]({case['url']})", colour=clr)
            view = TakeCase(case_manager)
            await bot_channel.send('⠀', embed=emb, view=view)
        view = ReloadCases(self)
        await case_manager.close()
        await bot_channel.send("Cases loaded.", view=view)

    # TASKS

    @tasks.loop(hours=3)
    async def cases_refresh(self):
        await self.reload_cases()


def setup(client):
    client.add_cog(Cases(client))
