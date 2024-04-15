"""A base cog to simplify various cog actions."""

import logging

from discord.ext.commands import Bot, Cog


class BaseCog(Cog):
    """A base cog to simplify various cog actions."""

    def __init__(self, bot: Bot) -> None:
        """Initialize the base cog with the bot."""
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @classmethod
    async def setup(cls, bot: Bot) -> None:
        """Initialize the cog and add it to the bot."""
        logging.getLogger(__name__).info("Initialized %s", cls.__name__)
        await bot.add_cog(cls(bot))
