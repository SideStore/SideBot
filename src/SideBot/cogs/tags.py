"""prelimitary tags cog, will be updated later."""

import datetime
import traceback
import typing

import discord
from discord import app_commands
from discord.app_commands import command as acommand
from discord.app_commands import guild_only

from SideBot import SideBot
from SideBot.db.tags import DiscordUser
from SideBot.db.tags import Tag as DBTag

from .basecog import BaseCog


class CreateTagsModal(discord.ui.Modal, title="Create a Tag"):

    """Modal for creating tags."""

    tagname: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
        label="Tag Name",
        placeholder="Tag Name",
        style=discord.TextStyle.short,
        required=True,
        min_length=1,
        max_length=30,
    )
    content: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
        label="Content",
        placeholder="Content of the tag",
        style=discord.TextStyle.long,
        required=True,
        min_length=1,
        max_length=2000,
    )

    button1_title: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
        label="Button 1 Title",
        placeholder="Button 1 Title",
        style=discord.TextStyle.short,
        required=False,
        min_length=1,
        max_length=30,
    )
    button1_link: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
        label="Button 1 Link",
        placeholder="Button 1 Link",
        style=discord.TextStyle.short,
        required=False,
        min_length=1,
        max_length=2000,
    )

    @typing.override
    async def on_submit(self, interaction: discord.Interaction[discord.Client]) -> None:
        if not interaction.guild:
            return await interaction.response.send_message(
                embeds=[
                    discord.Embed(
                        title="400 Bad Request",
                        description="This command can only be used in a guild.",
                    ),
                ],
                ephemeral=True,
            )
        if not isinstance(interaction.client, SideBot):
            return await interaction.response.send_message(
                embeds=[
                    discord.Embed(
                        title="501 Not Implemented",
                        description="Contact <@195864152856723456> if this happens :)",
                    ),
                ],
                ephemeral=True,
            )
        tagobj: DBTag = DBTag(
            self.tagname.value,
            self.content.value,
            DiscordUser.from_dpy_user(interaction.user),
            datetime.datetime.now(tz=datetime.UTC),
            datetime.datetime.now(tz=datetime.UTC),
            [],
            0,
            interaction.client.connection,
        )
        if interaction.client.config.get("WRITE_SCHEMA", "false") == "true":
            await tagobj.finish()
        await tagobj.create(interaction.guild.id)
        await interaction.response.send_message(
            embeds=[
                discord.Embed(
                    title="201 Created",
                    description="Tag created",
                ),
            ],
            ephemeral=True,
        )
        return None

    @typing.no_type_check
    @typing.override
    async def on_error(
        self, interaction: discord.Interaction, error: Exception, /,
    ) -> None:
        await interaction.response.send_message(
            embeds=[
                discord.Embed(
                    title="500 Internal Server Error",
                    description="Something went wrong",
                ),
            ],
            ephemeral=True,
        )
        traceback.print_exception(type(error), error, error.__traceback__)


class Tags(BaseCog):

    """Tags cog with commands for tags."""

    @acommand()
    @guild_only()
    async def tag(self, ctx: discord.Interaction, tag_name: str) -> None:
        """Get a tag."""
        if not ctx.guild:
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(
                        title="400 Bad Request",
                        description="This command can only be used in a guild.",
                    ),
                ],
                ephemeral=True,
            )
        if isinstance(ctx.client, SideBot):
            try:
                tag = await DBTag.get(
                    ctx.guild.id,
                    tag_name,
                    ctx.client.connection,
                )
            except ValueError:
                return await ctx.response.send_message(
                    embeds=[
                        discord.Embed(
                            title="404 Not Found",
                            description="Tag not found",
                        ),
                    ],
                    ephemeral=True,
                )
            return await ctx.response.send_message(
                embeds=[discord.Embed(title=tag_name, description=tag.content)],
                ephemeral=False,
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
    async def create(
        self,
        ctx: discord.Interaction,
    ) -> None:
        """Create a tag."""
        if not ctx.guild:
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(
                        title="400 Bad Request",
                        description="This command can only be used in a guild.",
                    ),
                ],
                ephemeral=True,
            )
        if isinstance(ctx.client, SideBot):
            view: CreateTagsModal = CreateTagsModal()
            await ctx.response.send_modal(view)
            return None

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
                    discord.Embed(
                        title="400 Bad Request",
                        description="This command can only be used in a guild.",
                    ),
                ],
                ephemeral=True,
            )
        if isinstance(ctx.client, SideBot):
            tag = await DBTag.get(ctx.guild.id, tag_name, ctx.client.connection)
            await tag.delete(ctx.guild.id)
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(title="200 OK", description="Tag deleted"),
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

    @acommand()
    @guild_only()
    @app_commands.default_permissions(manage_expressions=True)
    async def update(
        self,
        ctx: discord.Interaction,
        tag_name: str,
        content: str,
    ) -> None:
        """Update a tag."""
        if not ctx.guild:
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(
                        title="400 Bad Request",
                        description="This command can only be used in a guild.",
                    ),
                ],
                ephemeral=True,
            )
        if isinstance(ctx.client, SideBot):
            tag = await DBTag.get(ctx.guild.id, tag_name, ctx.client.connection)
            await tag.update(ctx.guild.id, content)
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(title="200 OK", description="Tag updated"),
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

    @acommand()
    @guild_only()
    async def tags(self, ctx: discord.Interaction) -> None:
        """Get all tags."""
        if not ctx.guild:
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(
                        title="400 Bad Request",
                        description="This command can only be used in a guild.",
                    ),
                ],
                ephemeral=True,
            )
        if isinstance(ctx.client, SideBot):
            tags = DBTag.get_all(ctx.guild.id, ctx.client.connection)
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(
                        title="Tags",
                        description="\n".join(
                            [tag.tagname async for tag in tags],
                        ),
                    ),
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
