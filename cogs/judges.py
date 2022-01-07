import discord
from discord.ext import commands
from discord.commands import slash_command
from database_managers.JudgeManager import JudgeManager
from database_managers.CaseManager import CaseManager
from config import guild_id
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os


class Judges(commands.Cog):
    def __init__(self, client):
        self.client = client
        print('Judges module loaded.')

    @slash_command(guild_ids=[guild_id])
    async def judges(self, ctx):
        jm = JudgeManager()
        judge_list = await jm.get_all_judges()
        emb = discord.Embed(title="Judges", colour=0x2ecc71)
        async for judge in judge_list:
            emb.add_field(name=f"{judge['name']}", value=f"{judge['position']}", inline=True)
        await jm.close()
        await ctx.send(embed=emb)

    @commands.command()
    async def update_judges(self, ctx):
        if str(ctx.channel) == "bot-commands":
            jm = JudgeManager()
            await jm.remove_all_judges()
            judges_to_insert = list()
            # Gets the guild based on the guild ID
            guild = self.client.get_guild(guild_id)
            for role in guild.roles:
                if role.name == "Judge" or role.name == "Magistrate":
                    for judge in role.members:
                        judge_data = dict()
                        judge_data['name'] = f"{judge.name}#{judge.discriminator}"
                        judge_data['position'] = role.name
                        judge_data['user_id'] = judge.id
                        judges_to_insert.append(judge_data)
            await jm.add_multiple_judges(judges_to_insert)
            await jm.close()
            await ctx.send("Judge list updated!")

    @commands.command()
    async def activity(self, ctx, month: int, year: int):
        if str(ctx.channel) == "bot-commands":
            # Updates the list of judges
            await ctx.invoke(self.client.get_command("update_judges"))
            # Grabs a list of cases
            cm = CaseManager()
            cases = await cm.get_cases_year_month(year, month)
            if cases is None:
                await ctx.send("No data found for the specified month and year.")
                return 1
            data = dict()

            # Grabs a list of judges and them adds it to the data dictionary with 0 assigned cases by default.
            jm = JudgeManager()
            judge_list = await jm.get_all_judges()
            await jm.close()
            async for judge in judge_list:
                data[judge['user_id']] = 0
            # Loops through the cases and if it finds the handler of one in the data dictionary, it adds 1 to it.
            async for case in cases:
                if case['handler'] in data.keys():
                    data[case['handler']] = data[case['handler']] + 1

            rows = list()
            # Loops through the data dictionary and formats it in rows for pandas.
            for key, value in data.items():
                # Quickly translates the id to an user object.
                user = await self.client.fetch_user(key)
                rows.append({'Name': user.name, 'Cases': value})

            # Creates a dataframe and sorts it descending.
            df = pd.DataFrame(rows)
            df = df.sort_values(by=['Cases'], ascending=False)
            # Resets the indexes on the dataframe
            df = df.reset_index(drop=True)
            print(df)
            # Create a bar plot based on the dataframe data and saves it as plot.png
            sns.set_style("darkgrid")
            sns.barplot(data=df, x="Cases", y='Name')
            plt.savefig("plots/plot.png")
            plt.clf()
            plt.close()
            # Sends an image of the plot
            await ctx.send(file=discord.File('plots/plot.png'))
            os.remove('plots/plot.png')
            print("Sent plot.")
            await ctx.send(f"Total cases for the month: {df['Cases'].sum()}")
            # Gets the index of the row with the max cases and them shows the name.
            await ctx.send(f"Judge with most cases: {df.iloc[df['Cases'].idxmax()]['Name']}")
            await ctx.send(f"Judge with the least cases: {df.iloc[df['Cases'].idxmin()]['Name']}")
            await ctx.send(f"Average cases per judge: {df['Cases'].mean()}")
            await cm.close()

    @activity.error
    async def activity_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Correct usage: .activity [month as number] [year]")

    @commands.command()
    async def cases(self, ctx, judge: discord.User, month: int, year: int):
        if str(ctx.channel) != "bot-commands":
            return 1
        await ctx.send(f'Pulling cases for {judge.name} on {month}/{year}')
        cm = CaseManager()
        cases = await cm.get_cases_year_month(year, month, judge.id)
        await cm.close()
        if cases is None:
            await ctx.send(f"No data found for {judge.name} on {month}/{year}")
            return 1
        case_list = list()
        async for case in cases:
            case_list.append(case['url'])
        await ctx.send('\n'.join(case_list))

    @cases.error
    async def cases_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Correct usage: .cases [user @], [month as number] [year]")

    @commands.command()
    async def make_available(self, ctx, url: str):
        if str(ctx.channel) != "bot-commands":
            return 1
        cm = CaseManager()
        result = await cm.make_available(url)
        if result.matched_count == 0:
            await ctx.send("Case not found.")
            return 1
        await ctx.send("Case has been made available and will be visible upon refresh.")

    @commands.command()
    async def switch_case(self, ctx, url, to: discord.User):
        if str(ctx.channel) != "bot-commands":
            return 1
        cm = CaseManager()
        case = await cm.get_case_by_kv('url', url)
        if 'handler' not in case.keys():
            await ctx.send("Case is not taken by anyone.")
            return 1
        await cm.make_unavailable(case['name'], to.id)
        await ctx.send(f"Case has been given to {to.name}")


def setup(client):
    client.add_cog(Judges(client))
