from io import BytesIO

import discord
from discord.ext import commands
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from config import GUILD_ID, JUDGE_ROLE
from utils.models import Case
from utils.utils import Utils


class Judges(commands.Cog):

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
        if not await Utils.is_in_channel(ctx):
            return
        await ctx.defer()
        data = dict()

        guild = self.client.get_guild(GUILD_ID)
        # Grabs a list of judges and them adds it to the data dictionary with 0 assigned cases by default.
        judge_list = discord.utils.get(guild.roles, name=JUDGE_ROLE).members
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

        rows = list()
        # Loops through the data dictionary and formats it in rows for pandas.
        for key, value in data.items():
            # Quickly translates the id to a user object.
            user = await self.client.fetch_user(key)
            rows.append({'Name': user.name, 'Cases': value})

        # Creates a dataframe and sorts it descending.
        df = pd.DataFrame(rows)
        df = df.sort_values(by=['Cases'], ascending=False)
        # Resets the indexes on the dataframe
        df = df.reset_index(drop=True)
        # Create a bar plot based on the dataframe data and saves it as plot.png
        sns.set_style("darkgrid")
        plot = sns.barplot(data=df, x="Cases", y='Name')
        plot_image = BytesIO()
        plot.get_figure().savefig(plot_image, format='png')
        # Seeking at the beginning of the in memory file
        plot_image.seek(0)
        plt.clf()
        plt.close()
        # Sends an image of the plot
        msg = f"Total cases for the month: {df['Cases'].sum()}\n" \
              f"Judge with most cases: {df.iloc[df['Cases'].idxmax()]['Name']}\n" \
              f"Judge with the least cases: {df.iloc[df['Cases'].idxmin()]['Name']}\n" \
              f"Average cases per judge: {df['Cases'].mean()}"
        await ctx.send_followup(msg, file=discord.File(plot_image, filename='activity.png'))

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def cases(self, ctx, judge: discord.User, month: discord.Option(int, choices=Utils.MONTH_CHOICES), year: int):
        await ctx.defer()
        cases = Case.objects(year=year, month=month, handler=judge.id)

        if not cases:
            await ctx.send_followup(f"No data found for {judge.name} on {month}/{year}")
            return
        case_list = list()
        for case in cases:
            case_list.append(case.url)
        await ctx.send_followup('\n'.join(case_list))

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
