# pylint: disable=C0103,C0114
import discord
import logging
from discord.ext.commands import Bot, when_mentioned_or


class SideBot(Bot):
    "Custom SideBot class to simplify start up"

    def __init__(self, config: dict):
        self.__tok = config.pop("DTOKEN")
        self.config = config
        self.logger = logging.getLogger(__name__)

        intents = discord.Intents.all()

        super().__init__(command_prefix=when_mentioned_or("##"), intents=intents)

        self.owner_id = self.config["OWNER"]
        self.conf_cogs = self.config["COGS"].split(",")

    async def setup_hook(self) -> None:
        "Set up cogs and app commands"
        for cog in self.conf_cogs:
            await self.load_extension(f"SideBot.cogs.{cog}")
        self.logger.debug(self.extensions)
        try:
            guild = discord.Object(self.config["GUILD"])
        except KeyError:
            guild = discord.Object(856315760224894986)
        self.tree.clear_commands(guild=guild)
        await self.tree.sync(guild=guild)
        self.logger.info("Set up hook done!")

    async def on_ready(self):
        "Handle bot ready status"
        if self.user:
            self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        else:
            self.logger.error("Error getting user")

    # pylint: disable=W0221
    async def on_command_error(self, ctx, error):
        "Handle unhandled command errors"
        self.logger.error(ctx)
        self.logger.error(error)

    def run(self, token: str | None = None, *args, **kwargs):
        if token:
            return super().run(token, *args, **kwargs)
        return super().run(self.__tok, *args, **kwargs)

    @classmethod
    def from_env(cls, path: str = ".env"):
        "Loads the bot from a .env file with the proper configuration"
        with open(path, "r", encoding="utf-8") as env:
            conf = {
                k: v
                for line in env
                if (k := line.strip().split("=", 1)[0])
                and (v := line.strip().split("=", 1)[1])
            }

        return cls(conf)
