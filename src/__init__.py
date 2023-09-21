# pylint: disable=C0114
from pathlib import Path

import discord
from discord.ext import commands


class SideBot(commands.Bot):
    "Custom SideBot class to simplify start up"
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('##'),
                         intents=intents)

        self.owner_id = 195864152856723456

    async def setup_hook(self) -> None:
        "Set up cogs and app commands"
        cogs = list(Path("src/modules").glob("*"))
        cogs = [c.name.split('.')[0] for c in cogs
                if (c.is_file() and c.name != "__init__.py" and c.name.endswith(".py"))
                or (c.is_dir() and c.name != '__pycache__')]
        for cog in cogs:
            print(f"Loading {cog}!")
            await self.load_extension(f"src.modules.{cog}")

        guild = discord.Object(949183273383395328)
        self.tree.clear_commands(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_ready(self):
        "Handle bot ready status"
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    # pylint: disable=W0221
    async def on_command_error(self, ctx, error):
        "Handle unhandled command errors"
        print(ctx)
        print(error)
