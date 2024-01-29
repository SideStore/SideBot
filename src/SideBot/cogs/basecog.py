"A base cog to simplify various cog actions" 
from discord.ext.commands import Bot, Cog


class BaseCog(Cog):
    "A base cog to simplify various cog actions" 

    def __init__(self, bot):
        self.bot = bot

    @classmethod
    async def setup(cls, bot: Bot):
        "The bot setup function for all Cogs"
        print(f"Initialized {cls.__name__}")
        await bot.add_cog(cls(bot))
