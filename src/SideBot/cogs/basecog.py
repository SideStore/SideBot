from discord.ext.commands import Bot, Cog


class BaseCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    async def setup(cls, bot: Bot):
        print(f"Initialized {cls.__name__}")
        await bot.add_cog(cls(bot))
    
