"""Main module for the SideBot."""

# pylint: disable=C0103,C0114
import logging
import typing

import yaml
import asyncpg
import discord
from discord.ext import commands
from discord.ext.commands import AutoShardedBot, Bot, when_mentioned_or

from SideBot.db.tags import Tag

from .utils import ButtonLink, DiscordUser, BotConfig


class SideBot(Bot):
    """Custom SideBot class to simplify start up."""

    def __init__(self, config: dict[str, str]) -> None:
        """Initialize the bot with the given configuration."""
        self.config = BotConfig.from_dict(config)
        self.logger = logging.getLogger(__name__)

        intents = discord.Intents.all()

        super().__init__(
            command_prefix=when_mentioned_or("##"),
            intents=intents,
        )

        self.owner_id = self.config.owner
        self.conf_cogs = self.config.cogs

    async def setup_connection(self) -> asyncpg.Connection:
        """Set up the database connection."""
        return await asyncpg.connect(self.config.db_url)

    async def setup_hook(self) -> None:
        """Set up cogs and app commands."""
        for cog in self.config.cogs:
            await self.load_extension(f"SideBot.cogs.{cog}")
        self.logger.debug(self.extensions)
        self.logger.debug(self.tree.get_commands())
        self.logger.info("Set up hook done!")

    async def on_ready(self) -> None:
        """Handle bot ready status."""
        if self.user:
            self.logger.info(
                "Logged in as %s (ID: %s)",
                self.user,
                self.user.id,
            )
            self.connection: asyncpg.Connection = await self.setup_connection()
            self.logger.info("Connected to postgresql!")

            await Tag.write_schema(self.connection)

            await self.connection.set_type_codec(
                "discorduser",
                encoder=DiscordUser.to_tuple,
                decoder=DiscordUser.from_tuple,
                format="tuple",
            )

            await self.connection.set_type_codec(
                "buttonlink",
                encoder=ButtonLink.to_tuple,
                decoder=ButtonLink.from_tuple,
                format="tuple",
            )

        else:
            self.logger.error("Error getting user")

    # pylint: disable=W0221
    async def on_command_error(
        self,
        ctx: commands.Context[Bot | AutoShardedBot],
        error: Exception,
    ) -> None:
        """Handle unhandled command errors."""
        self.logger.error(ctx)
        self.logger.error(error)

    def run(
        self,
        *args: typing.Any,
        token: str | None = None,
        **kwargs: typing.Any,
    ) -> None:
        """Run the bot with the given token."""
        if token:
            return super().run(token, *args, root_logger=True, **kwargs)
        return super().run(self.config.token, *args, root_logger=True, **kwargs)

    @classmethod
    def from_yaml_file(cls, path: str = "conf.yaml") -> "SideBot":
        with open(path, "r") as f:
            return cls(yaml.safe_load(f))
