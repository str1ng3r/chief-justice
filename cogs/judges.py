from io import BytesIO
from statistics import median

import discord
from discord.ext import commands
from aiohttp import ClientSession
from calendar import month_name

from config import GUILD_ID, JUDGE_ROLE
from utils.models import Case
from utils.utils import Utils


class Judges(commands.Cog):
    CHART_URL = "https://quickchart.io/chart/render/zm-2abd0eb9-04b5-423c-8586-bf8f55fd6d8c"

    def __init__(self, client):
        self.client = client
        print('Judges module loaded.')

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def judges(self, ctx):
        guild = self.client.get_guild(GUILD_ID)

        judge_list = list()
        for role in guild.roles:
            if role.name == JUDGE_ROLE:
                judge_list.extend(role.members)
        emb = discord.Embed(title="Judges", colour=0x2ecc71)
        for judge in judge_list:
            emb.add_field(name=f"​", value=f'<@{judge.id}>', inline=True)
        await ctx.respond(embed=emb)

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def activity(self, ctx, month: discord.Option(int, choices=Utils.MONTH_CHOICES), year: int):
        """
        Checks the activity of all the judges for a specific month.
        :param ctx: Discord application context
        :param month: Month to get the activity for
        :param year: Year to get the activity for
        :return: None
        """
        if not await Utils.is_in_channel(ctx):
            return
        await ctx.defer()
        data = dict()

        guild = self.client.get_guild(GUILD_ID)
        # Grabs a list of judges and them adds it to the data dictionary with 0 assigned cases by default.
        judge_list = discord.utils.get(guild.roles, name=JUDGE_ROLE).members
        # Forced to use the judge ID here because cases have the handler stored as the id.
        for judge in judge_list:
            data[judge.id] = 0

        # Grabs a list of cases
        cases = Case.objects(year=year, month=month)

        if not cases:
            await ctx.send_followup("No data found for the specified month and year.")
            return

        # Loops through the cases and if it finds the handler of one in the data dictionary, it adds 1 to it.
        for case in cases:
            if case.handler in data.keys():
                data[case.handler] += 1

        # Converting the keys of the dictionary from discord user id to discord name
        data = {(await guild.fetch_member(key)).display_name: value for (key, value) in data.items()}

        case_count = [str(x) for x in data.values()]

        async with ClientSession() as session:
            results = await session.get(f"{self.CHART_URL}?title=Judicial activity for {month_name[month]} {year}"
                                        f"&labels={','.join(data.keys())}&data1={','.join(case_count)}")
            chart_image = BytesIO(await results.content.read())

        msg = f"Total cases for the month: {sum(data.values())}\n" \
              f"Judge with most cases: {max(data, key=data.get)}\n" \
              f"Judge with the least cases: {min(data, key=data.get)}\n" \
              f"Median of cases per judge: {median(data.values())}"
        await ctx.send_followup(msg, file=discord.File(chart_image, filename='activity.png'))

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def cases(self, ctx, judge: discord.User, month: discord.Option(int, choices=Utils.MONTH_CHOICES), year: int):
        await ctx.defer()
        cases = Case.objects(year=year, month=month, handler=judge.id)

        if not cases:
            await ctx.send_followup(f"No data found for {judge.name} on {month}/{year}")
            return

        embed_chunks = list()
        case_chunks = list()
        temp_case_chunk = str()
        embed_chunk_size = 0
        for case in cases:

            case_chunk_to_add = f"\n[{case.name}]({case.url})"
            potential_case_chunk_length = len(temp_case_chunk) + len(case_chunk_to_add)

            if potential_case_chunk_length + embed_chunk_size >= 5800:
                embed_chunks.append(case_chunks)
                case_chunks = list()
                embed_chunk_size = 0

            if potential_case_chunk_length > 1000:
                case_chunks.append(temp_case_chunk)
                embed_chunk_size += len(temp_case_chunk)
                temp_case_chunk = ''
            temp_case_chunk = f"{temp_case_chunk}{case_chunk_to_add}"

        if not case_chunks:
            case_chunks.append(temp_case_chunk)

        if embed_chunk_size >= 0:
            embed_chunks.append(case_chunks)

        for idx, embed_chunk in enumerate(embed_chunks):
            match idx:
                case 0:
                    title = f"Cases for Judge {judge.display_name}"
                case _:
                    title = f"Cases for Judge {judge.display_name} ({idx+1})"

            emb = discord.Embed(title=title, colour=0x00FFFF)

            for case_chunk in embed_chunk:
                emb.add_field(name=f"​", value=f"{case_chunk}", inline=False)

            await ctx.send_followup(embed=emb)

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def make_available(self, ctx, url: str):
        if not await Utils.is_in_channel(ctx):
            return

        await ctx.defer()

        case = Case.objects(url=url).first()

        if case is None:
            await ctx.send_followup("Case not found.")
            return

        case.modify(set__justice=False, unset__handler=True)
        await ctx.send_followup("Case has been made available and will be visible upon refresh.")

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def switch_case(self, ctx, url, to: discord.User):
        if not await Utils.is_in_channel(ctx):
            return

        await ctx.defer()
        case = Case.objects(url=url).first()

        if case is None:
            await ctx.send_followup("Case not found.")
            return

        if case.handler is None:
            await ctx.send_followup("This case is not taken by anyone.")
            return

        case.handler = to.id
        case.save()
        await ctx.send_followup(f"Case has been given to {to.name}")


def setup(client):
    client.add_cog(Judges(client))
