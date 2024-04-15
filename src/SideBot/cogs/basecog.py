"A base cog to simplify various cog actions"

from discord.ext.commands import Bot, Cog
import logging


class BaseCog(Cog):
    "A base cog to simplify various cog actions"

    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @classmethod
    async def setup(cls, bot: Bot):
        "The bot setup function for all Cogs"
        logging.getLogger(__name__).debug(f"Initialized {cls.__name__}")
        await bot.add_cog(cls(bot))
