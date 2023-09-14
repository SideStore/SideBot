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
        cogs = list(Path("src/modules").glob("*.py"))
        for cog in cogs:
            name = cog.name.split('.')[0]
            if name == '__init__':
                continue
            print(f"Loading {name}")
            await self.load_extension(f"src.modules.{name}")

        guild = discord.Object(856315760224894986)
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
