import logging
from typing import Self

from .. import SideBot
from discord.ext.commands import Cog


class BaseCog(Cog):
    "A base cog to simplify bot/logger set up"

    def __init__(self, bot: SideBot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__log_name__)

    @property
    def __log_name__(self):
        return f"SideBot.cogs.{self.__class__.__name__.lower()}"

    @classmethod
    async def setup(cls, bot: SideBot) -> Self:
        bc = cls(bot)
        await bot.add_cog(bc)
        bc.logger.info(f"Initialized {cls.__name__!r}!")
        return bc
