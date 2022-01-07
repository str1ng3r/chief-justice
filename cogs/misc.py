from discord.ext import commands
import os


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client
        print('Misc module loaded.')

    # COMMANDS

    @commands.command()
    async def test(self, ctx):
        if str(ctx.channel) == 'bot-commands':
            await ctx.send("works")

    @commands.command()
    async def bonk(self, ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/792468749496221716/817309301236432917/unknown.png")

    @commands.command()
    async def fbiraid(self, ctx):
        await ctx.send("https://media1.tenor.com/images/93d11bc59526ce49f60766f0045d819b/tenor.gif?itemid=11500735")


def setup(client):
    client.add_cog(Misc(client))
