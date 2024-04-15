"""prelimitary tags cog, will be updated later."""

import discord
from discord.app_commands import command as acommand
from discord.app_commands import guild_only

from SideBot import SideBot
from SideBot.db.tags import Tag as DBTag

from .basecog import BaseCog


class Tags(BaseCog):
    """Tags cog with commands for tags."""

    @acommand()
    @guild_only()
    async def tag(self, ctx: discord.Interaction, tag_name: str) -> None:
        """Get a tag."""
        if not ctx.guild:
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(title="400 Bad Request", description="This command can only be used in a guild."),
                ],
                ephemeral=True,
            )
        if isinstance(ctx.client, SideBot):
            try:
                tag = DBTag.get(ctx.guild.id, tag_name, ctx.client.connection)
            except ValueError:
                return await ctx.response.send_message(
                    embeds=[discord.Embed(title="404 Not Found", description="Tag not found")],
                    ephemeral=True,
                )
            return await ctx.response.send_message(
                embeds=[discord.Embed(title=tag_name, description=tag.content)],
                ephemeral=True,
            )

        return await ctx.response.send_message(
            embeds=[
                discord.Embed(
                    title="501 Not Implemented",
                    description="Contact <@195864152856723456> if this happens :)",
                ),
            ],
            ephemeral=True,
        )


setup = Tags.setup
