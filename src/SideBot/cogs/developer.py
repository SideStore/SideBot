"""The developer cog for loading/reloading/unloading cogs and syncing app commands."""

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

from .basecog import BaseCog


class Developer(BaseCog):
    """Developer cog with developer only commands."""

    def __init__(self, bot: Bot) -> None:
        """Initialize the developer cog."""
        super().__init__(bot)
        self.description = "This is for ny only"

    async def cog_before_invoke(self, ctx: commands.Context[Bot | AutoShardedBot]) -> None:
        """Delete text command messages."""
        try:
            await ctx.message.delete()
        except (Forbidden, NotFound, HTTPException):
            self.logger.exception()
            return

    # pylint: disable=W0221
    def interaction_check(self, interaction: Interaction) -> bool:
        """Make sure i'm the only one running these commands."""
        return self.bot.owner_id == interaction.user.id

    @acommand()
    async def load(self, inter: Interaction, cog: str) -> None:
        """Load `cog`'s extension into the bot."""
        try:
            await self.bot.load_extension(f"SideBot.cogs.{cog}")
            return await inter.response.send_message(f"Loaded {cog}!", ephemeral=True)
        except (ExtensionAlreadyLoaded, ExtensionNotFound) as err:
            if isinstance(err, ExtensionAlreadyLoaded):
                msg = f"{cog} is already loaded!"
            else:
                msg = f"{cog} could not be found!"
            return await inter.response.send_message(f"{msg}\n{err}", ephemeral=True)
        except Exception as err:  # pylint: disable=W0718 # noqa: BLE001
            return await inter.response.send_message(
                f"Failed to load {cog}!\n{err}",
                ephemeral=True,
            )

    @acommand()
    async def unload(self, inter: Interaction, cog: str) -> None:
        """Unloads `cog`'s extension from the bot."""
        if cog in ["developer", "admin"]:
            return await inter.response.send_message(
                f"Cowardly refusing to unload {cog}!",
                ephemeral=True,
            )
        try:
            await self.bot.unload_extension(f"SideBot.cogs.{cog}")
            return await inter.response.send_message(f"Unloaded {cog}!", ephemeral=True)
        except ExtensionNotLoaded:
            return await inter.response.send_message(
                f"Failed to unload non-loaded {cog}!",
                ephemeral=True,
            )
        except Exception as err:  # pylint: disable=W0718 # noqa: BLE001
            return await inter.response.send_message(f"{err}", ephemeral=True)

    @acommand()
    async def reload(self, inter: Interaction, cog: str) -> None:
        """Reload `cog`'s extension file."""
        try:
            await self.bot.reload_extension(f"SideBot.cogs.{cog}")
            return await inter.response.send_message(f"Reloaded {cog}!", ephemeral=True)
        except (ExtensionNotLoaded, ExtensionNotFound) as err:
            if isinstance(err, ExtensionNotLoaded):
                msg = f"Cannot reload {cog}! Did you forget to /load it?"
            else:
                msg = f"Could not find {cog} to reload!"
            return await inter.response.send_message(msg, ephemeral=True)
        except Exception as err:  # pylint: disable=W0718 # noqa: BLE001
            return await inter.response.send_message(
                f"Failed to reload {cog}!\n{err}",
                ephemeral=True,
            )

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

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.", delete_after=5)

    @load.error
    @unload.error
    @reload.error
    async def app_command_error(self, inter: Interaction, err: errors.AppCommandError) -> None:
        """Handle app command errors."""
        if isinstance(err, errors.CheckFailure):
            if self.bot.owner_id != inter.user.id:
                return await inter.response.send_message(
                    "These commands are only for ny, they will never work.",
                    ephemeral=True,
                )
            return None

        return await inter.response.send_message(f"{err}", ephemeral=True)


setup = Developer.setup
