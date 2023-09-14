from typing import Optional, Literal

from discord import Object, Interaction, Forbidden, NotFound, HTTPException
from discord.app_commands import command as acommand
from discord.app_commands import errors
from discord.ext.commands import Bot, Cog, command, Context, Greedy, guild_only, ExtensionNotLoaded, ExtensionAlreadyLoaded, ExtensionNotFound


class Developer(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.description = "This is for ny only"

    async def cog_before_invoke(self, ctx):
        try:
            await ctx.message.delete()
        except (Forbidden, NotFound, HTTPException) as err:
            print(err)
            return

    async def interaction_check(self, interaction: Interaction):
        return self.bot.owner_id == interaction.user.id

    @acommand()
    async def load(self, inter: Interaction, cog: str):
        try:
            await self.bot.load_extension(f"modules.{cog}")
            return await inter.response.send_message(f"Loaded {cog}!",
                                                           ephemeral=True)
        except (ExtensionAlreadyLoaded, ExtensionNotFound) as err:
            if isinstance(err, ExtensionAlreadyLoaded):
                msg = f"{cog} is already loaded!"
            else:
                msg = f"{cog} could not be found!"
            return await inter.response.send_message(f"{msg}\n{err}", ephemeral=True)
        except Exception as err:
            return await inter.response.send_message(f"Failed to load {cog}!"
                                                     f"\n{err}",
                                                     ephemeral=True)

    @acommand()
    async def unload(self, inter: Interaction, cog: str):
        if cog in ["developer", "admin"]:
            return await inter.response.send_message(f"Cowardly refusing to unload {cog}!", ephemeral=True)
        try:
            await self.bot.unload_extension(f"modules.{cog}")
            return await inter.response.send_message(f"Unloaded {cog}!", ephemeral=True)
        except ExtensionNotLoaded:
            return await inter.response.send_message(f"Failed to unload non-loaded {cog}!", ephemeral=True)
        except Exception as err:
            return await inter.response.send_message(f"{err}", ephemeral=True)

    @acommand()
    async def reload(self, inter: Interaction, cog: str):
        try:
            await self.bot.reload_extension(f"modules.{cog}")
            return await inter.response.send_message(f"Reloaded {cog}!",
                                                     ephemeral=True)
        except (ExtensionNotLoaded, ExtensionNotFound) as err:
            if isinstance(err, ExtensionNotLoaded):
                msg = f"Cannot reload {cog}! Did you forget to /load it?"
            else:
                msg = f"Could not find {cog} to reload!"
            return await inter.response.send_message(msg, ephemeral=True)
        except Exception as err:
            return await inter.response.send_message(f"Failed to reload {cog}!\n{err}", ephemeral=True)

    @command()
    @guild_only()
    async def sync(self, ctx: Context, guilds: Greedy[Object],
                   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        print(f"{guilds = }")
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            return await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}",
                delete_after=5
            )

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.", delete_after=5)

    @load.error
    @unload.error
    @reload.error
    async def app_command_error(self, inter: Interaction, err: errors.AppCommandError):
        if isinstance(err, errors.CheckFailure):
            if self.bot.owner_id != inter.user.id:
                return await inter.response.send_message("These commands are only for ny, they will never work for you.", ephemeral=True)
        else:
            return await inter.response.send_message(f"{err}", ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(Developer(bot))
