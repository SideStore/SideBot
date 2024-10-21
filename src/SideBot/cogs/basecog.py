"""A base cog to simplify various cog actions."""

import logging

from discord.ext.commands import Bot, Cog


class BaseCog(Cog):
    """A base cog to simplify various cog actions."""

    def __init__(self, bot: Bot) -> None:
        """Initialize the base cog with the bot."""
        self.bot = bot
        self.logger = logging.getLogger(__name__)
