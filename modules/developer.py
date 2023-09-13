from discord import Interaction, Forbidden, NotFound, HTTPException
from discord.app_commands import command, describe
from discord.ext.commands import Bot, Cog, ExtensionNotLoaded, ExtensionAlreadyLoaded, ExtensionNotFound


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

    @command()
    async def load(self, interaction: Interaction, cog: str):
        try:
            await self.bot.load_extension(f"modules.{cog}")
            return await interaction.response.send_message(f"Loaded {cog}!",
                                                           ephemeral=True)
        except (ExtensionAlreadyLoaded, ExtensionNotFound) as err:
            return await interaction.response.send_message(f"Failed to load {cog}!"
                                                           f"\n{err}",
                                                    ephemeral=True)

    @command()
    async def unload(self, inter: Interaction, cog: str):
        if cog in ["developer", "admin"]:
            return await inter.response.send_message(f"Cowardly refusing to unload {cog}", ephemeral=True)
        try:
            await self.bot.unload_extension(f"modules.{cog}")
            return await inter.response.send_message(f"Unloaded {cog}!",
                                                     ephemeral=True)
        except ExtensionNotLoaded as err:
            return await inter.response.send_message(f"Failed to unload {cog}!"
                                                     f"\n{err}",
                                                     ephemeral=True)

    @command()
    async def reload(self, inter: Interaction, cog: str):
        try:
            await self.bot.reload_extension(f"modules.{cog}")
            return await inter.response.send_message(f"Reloaded {cog}!",
                                                     ephemeral=True)
        except (ExtensionNotLoaded, ExtensionNotFound) as err:
            return await inter.response.send_message(f"Failed to reload {cog}!"
                                                     f"\n{err}",
                                                     ephemeral=True)

async def setup(bot: Bot):
    await bot.add_cog(Developer(bot))
