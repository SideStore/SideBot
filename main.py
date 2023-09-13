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

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_command_error(self, ctx, error):
        print(ctx)
        print(error)


SideBot().run(conf['DTOKEN'])

