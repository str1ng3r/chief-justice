import asyncio

import discord
from discord.ext import commands, tasks
from database_managers.CaseManager import CaseManager
from utils.enums import CaseType
from web_handlers.MainForumScraper import MainForumScraper
from config import MAIN_FORUM_NAME, MAIN_FORUM_PASS
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
        main_forum_scraper = MainForumScraper()

        await main_forum_scraper.get_cases()
        await bot_channel.send("Received cases...")

        # Grabs all the available cases from the database
        cases = await case_manager.get_available_cases()

        async for case in cases:
            if case['case_type'] == CaseType.TRAFFIC.value:
                clr = 0x2e2eff
            elif case['case_type'] == CaseType.CIVIL.value:
                clr = 0x00d100
            else:
                clr = 0xd10000
            emb = discord.Embed(title=case['name'], description=f"[ACCESS]({case['url']})", colour=clr)
            view = TakeCase()
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
