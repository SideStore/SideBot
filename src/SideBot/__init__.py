"""Main module for the SideBot."""

# pylint: disable=C0103,C0114
import logging
import pathlib

import discord
import psycopg2
from discord.ext import commands
from discord.ext.commands import AutoShardedBot, Bot, when_mentioned_or


class SideBot(Bot):
    """Custom SideBot class to simplify start up."""

    def __init__(self, config: dict[str, str]) -> None:
        """Initialize the bot with the given configuration."""
        self.__tok = config.pop("DTOKEN")
        self.config = config
        self.logger = logging.getLogger(__name__)

        intents = discord.Intents.all()

        super().__init__(command_prefix=when_mentioned_or("##"), intents=intents)

        self.owner_id = int(self.config["OWNER"])
        self.conf_cogs = self.config["COGS"].split(",")
        self.connection = self.setup_connection()

    def setup_connection(self) -> psycopg2.extensions.connection:
        """Set up the database connection."""
        return psycopg2.connect(self.config["DATABASE_URL"])

    async def setup_hook(self) -> None:
        """Set up cogs and app commands."""
        for cog in self.conf_cogs:
            await self.load_extension(f"SideBot.cogs.{cog}")
        self.logger.debug(self.extensions)
        try:
            guild = discord.Object(self.config["GUILD"])
        except KeyError:
            self.logger.info("defaulting to sidestore guild")
            guild = discord.Object(856315760224894986)
        self.logger.debug(self.tree.get_commands())
        await self.tree.sync(guild=guild)
        self.logger.info("Set up hook done!")

    async def on_ready(self) -> None:
        """Handle bot ready status."""
        if self.user:
            self.logger.info("Logged in as %s (ID: %s)", self.user, self.user.id)
        else:
            self.logger.error("Error getting user")

    # pylint: disable=W0221
    async def on_command_error(self, ctx: commands.Context[Bot | AutoShardedBot], error: Exception) -> None:
        """Handle unhandled command errors."""
        self.logger.error(ctx)
        self.logger.error(error)

    def run(  # noqa: PLR0913
        self,
        token: str | None = None,
        *,
        reconnect: bool = True,
        log_handler: logging.Handler | None = None,
        log_level: int = logging.INFO,
        root_logger: bool = True,
    ) -> None:
        """Run the bot with the given token."""
        if token:
            return super().run(
                token,
                reconnect=reconnect,
                log_handler=log_handler,
                log_level=log_level,
                root_logger=root_logger,
            )
        return super().run(
            self.__tok,
            reconnect=reconnect,
            log_handler=log_handler,
            log_level=log_level,
            root_logger=root_logger,
        )

    @classmethod
    def from_env(cls, path: str = ".env") -> "SideBot":
        """Load the bot from a .env file with the proper configuration."""
        with pathlib.Path(path).open(encoding="utf-8") as env:
            conf = {
                k: v for line in env if (k := line.strip().split("=", 1)[0]) and (v := line.strip().split("=", 1)[1])
            }

        return cls(conf)
