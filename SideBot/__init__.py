import logging

import discord
import aiosqlite

# from discord.ext import commands
from discord.ext.commands import Bot

from .utils import SideBotConfig


class SideBot(Bot):
    "Custom SideBot subclass of Bot to simplify startup"

    def __init__(self, config: SideBotConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        super().__init__(command_prefix="#!", intents=discord.Intents.all())
        self.owner_id = self.config.owner

    async def setup_hook(self) -> None:
        for cog in self.config.cogs:
            await self.load_extension(f"SideBot.cogs.{cog}")
        self.logger.info("We're running!")
        if self.user:
            self.logger.info(self.user)

    def run(self, *args, token: str | None = None, **kwargs) -> None:
        return super().run(token or self.config.token, *args, root_logger=True, **kwargs)

    async def close(self):
        await super().close()
