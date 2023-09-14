from pathlib import Path

import discord
from discord.ext import commands

with open(".env", "r") as env:
    conf = {k: v for line in env
            if (k := line.strip().split("=", 1)[0]) and \
               (v := line.strip().split("=", 1)[1])}


class SideBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.all()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('##'),
                         intents=intents)

        self.owner_id = 195864152856723456

    async def setup_hook(self) -> None:
        cogs = list(Path("modules").glob("*.py"))
        for cog in cogs:
            print(f"Loading {cog.name.split('.')[0]}")
            await self.load_extension(f"modules.{cog.name.split('.')[0]}")

        guild = discord.Object(856315760224894986)
        self.tree.clear_commands(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_command_error(self, ctx, error):
        print(ctx)
        print(error)


SideBot().run(conf['DTOKEN'])

