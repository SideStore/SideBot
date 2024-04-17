"""prelimitary tags cog, will be updated later."""

import datetime
import re
import traceback
import typing

import discord
from discord import app_commands
from discord.app_commands import command as acommand
from discord.app_commands import guild_only

from SideBot import SideBot
from SideBot.db.tags import Tag as DBTag
from SideBot.utils import ButtonLink, DiscordUser

from .basecog import BaseCog


class UpdateTagsModal(discord.ui.Modal, title="Update a Tag"):
    """Modal for updating tags."""

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
        tagobj: DBTag = await DBTag.get(interaction.guild.id, self.tagname.value, interaction.client.connection)
        tagobj.updated_at = datetime.datetime.now(tz=datetime.UTC)
        tagobj.content = self.content.value
        await tagobj.update()
        await interaction.response.send_message(
            embeds=[
                discord.Embed(
                    title="200 OK",
                    description="Tag updated",
                ),
            ],
            ephemeral=True,
        )
        return None

    @typing.no_type_check
    @typing.override
    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        /,
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
            interaction.guild.id,
            self.tagname.value,
            self.content.value,
            DiscordUser.from_dpy_user(interaction.user),
            datetime.datetime.now(tz=datetime.UTC),
            datetime.datetime.now(tz=datetime.UTC),
            [],
            0,
            None,
            interaction.client.connection,
        )
        await tagobj.create()
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
        self,
        interaction: discord.Interaction,
        error: Exception,
        /,
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

    def prepare_tag_view(self, button_links: list[ButtonLink]) -> discord.ui.View:
        """Prepare the tag view."""
        view = discord.ui.View()
        for button_link in button_links:
            custom_emojis = re.search(r"<:\d+>|<:.+?:\d+>|<a:.+:\d+>|[\U00010000-\U0010ffff]", button_link.label)
            if custom_emojis is not None:
                emoji = custom_emojis.group(0).strip()
                button_link.label = button_link.label.replace(emoji, "")
                button_link.label = button_link.label.strip()
            else:
                emoji = None
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label=button_link.label,
                    url=button_link.url,
                    emoji=emoji,
                ),
            )
        return view

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
            embed = discord.Embed(title=tag_name, description=tag.content, color=discord.Color(0x734EBE)).set_footer(
                text=f"Used count: {tag.used_count} | Created by {tag.author.name}"
                f" at {int(tag.created_at.timestamp())} | Last updated at {int(tag.updated_at.timestamp())}",
            )
            return await ctx.response.send_message(
                embeds=[embed],
                ephemeral=False,
                view=(self.prepare_tag_view(tag.button_links) if tag.button_links else discord.utils.MISSING),
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
            await tag.delete()
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
            return await ctx.response.send_modal(UpdateTagsModal())

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

    @acommand()
    @guild_only()
    async def add_button_link(self, ctx: discord.Interaction, tag_name: str, title: str, url: str) -> None:
        """Add a button link to a tag."""
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
            button_link = ButtonLink(title, url)
            tag.button_links.append(button_link)
            await tag.save()
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(title="200 OK", description="Button link added"),
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
    @app_commands.describe(idx="The index of the button link to remove (1-indexed)")
    async def remove_button_link(self, ctx: discord.Interaction, tag_name: str, idx: int) -> None:
        """Remove a button link from a tag."""
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
            del tag.button_links[idx - 1]
            await tag.save()
            return await ctx.response.send_message(
                embeds=[
                    discord.Embed(title="200 OK", description="Button link removed"),
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
