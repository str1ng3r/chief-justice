import discord


class Utils:
    MONTH_CHOICES = [discord.OptionChoice("January", 1), discord.OptionChoice("February", 2),
                     discord.OptionChoice("March", 3), discord.OptionChoice("April", 4), discord.OptionChoice("May", 5),
                     discord.OptionChoice("June", 6), discord.OptionChoice("July", 7),
                     discord.OptionChoice("August", 8),
                     discord.OptionChoice("September", 9), discord.OptionChoice("October", 10),
                     discord.OptionChoice("November", 11), discord.OptionChoice("December", 12)]

    @staticmethod
    async def is_in_channel(ctx: discord.ApplicationContext) -> bool:
        if str(ctx.channel) != "bot-commands":
            await ctx.respond("Not in bot-commands channel.")
            return False
        return True
