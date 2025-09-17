import logging
from typing import Literal

import discord
from discord import Forbidden, HTTPException, Interaction, NotFound, Object
from discord.app_commands import command as acommand
from discord.app_commands import errors
from discord.ext import commands
from discord.ext.commands import (
    AutoShardedBot,
    Bot,
    Context,
    ExtensionAlreadyLoaded,
    ExtensionNotFound,
    ExtensionNotLoaded,
    Greedy,
    command,
    guild_only,
)

from .. import SideBot
from .base import BaseCog


class Developer(BaseCog):
    "Developer cog for various actions useful during development."

    def __init__(self, bot: SideBot) -> None:
        super().__init__(bot)
        self.description = "A development cog for those who know :3"

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        try:
            await ctx.message.delete()
        except (Forbidden, NotFound, HTTPException):
            self.logger.exception(msg=None)
        return

    def interaction_check(self, interaction: Interaction) -> bool:
        "Ensure it's only the owner running these"
        return interaction.user.id == self.bot.owner_id

    @acommand()
    async def tester(self, inter: Interaction, cog: str):
        return await inter.response.send_message(f"Loaded {cog}!\n{discord.__version__}", ephemeral=True)

    @command()
    @guild_only()
    async def sync(
        self,
        ctx: Context[Bot | AutoShardedBot],
        guilds: Greedy[Object],
        spec: Literal["~", "*", "^"] | None = None,
    ) -> None:
        """Sync app commands to/from global/guild."""
        self.logger.debug("%s", guilds)
        if ctx.guild is None:
            await ctx.send("This command is only for guilds.", delete_after=5)
            return
        if not guilds:
            if ctx.guild.id is None:
                synced = await self.bot.tree.sync()
            else:
                guildid = discord.Object(ctx.guild.id)
                if spec == "~":
                    synced = await self.bot.tree.sync(guild=guildid)
                elif spec == "*":
                    self.bot.tree.copy_global_to(guild=guildid)
                    synced = await self.bot.tree.sync(guild=guildid)
                elif spec == "^":
                    self.bot.tree.clear_commands(guild=guildid)
                    await self.bot.tree.sync(guild=guildid)
                    synced = []
                else:
                    synced = await self.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}",
                delete_after=5,
            )

        ret = 0
        for guild in guilds:
            try:
                await self.bot.tree.sync(guild=guild)
            except HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(
            f"Synced the tree to {ret}/{len(guilds)}.",
            delete_after=5,
        )


setup = Developer.setup
