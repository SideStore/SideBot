"""prelimitary tags cog, will be updated later."""

import discord
from discord.app_commands import command as acommand, guild_only
from discord import app_commands

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

    @acommand()
    @guild_only()
    @app_commands.default_permissions(create_expressions=True)
    async def create(self, ctx: discord.Interaction, tag_name: str, content: str) -> None:
        """Create a tag."""
        if not ctx.guild:
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(title="400 Bad Request", description="This command can only be used in a guild."),
                ],
                ephemeral=True,
            )
        if isinstance(ctx.client, SideBot):
            tag = DBTag(tag_name, content, ctx.client.connection)
            tag.create(ctx.guild.id)
            return await ctx.response.send_message(
                embeds=[discord.Embed(title="201 Created", description="Tag created")],
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

    @acommand()
    @guild_only()
    @app_commands.default_permissions(manage_expressions=True)
    async def delete(self, ctx: discord.Interaction, tag_name: str) -> None:
        """Delete a tag."""
        if not ctx.guild:
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(title="400 Bad Request", description="This command can only be used in a guild."),
                ],
                ephemeral=True,
            )
        if isinstance(ctx.client, SideBot):
            tag = DBTag(tag_name, "", ctx.client.connection)
            tag.delete(ctx.guild.id)
            return await ctx.response.send_message(
                embeds=[discord.Embed(title="200 OK", description="Tag deleted")],
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

    @acommand()
    @guild_only()
    @app_commands.default_permissions(manage_expressions=True)
    async def update(self, ctx: discord.Interaction, tag_name: str, content: str) -> None:
        """Update a tag."""
        if not ctx.guild:
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(title="400 Bad Request", description="This command can only be used in a guild."),
                ],
                ephemeral=True,
            )
        if isinstance(ctx.client, SideBot):
            tag = DBTag(tag_name, content, ctx.client.connection)
            tag.update(ctx.guild.id)
            return await ctx.response.send_message(
                embeds=[discord.Embed(title="200 OK", description="Tag updated")],
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

    @acommand()
    @guild_only()
    async def tags(self, ctx: discord.Interaction) -> None:
        """Get all tags."""
        if not ctx.guild:
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(title="400 Bad Request", description="This command can only be used in a guild."),
                ],
                ephemeral=True,
            )
        if isinstance(ctx.client, SideBot):
            tags = DBTag.get_all(ctx.guild.id, ctx.client.connection)
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(title="Tags", description="\n".join([tag.tagname for tag in tags])),
                ],
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
