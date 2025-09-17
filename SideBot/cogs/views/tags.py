import arrow
from discord import Color, Interaction, Embed, ButtonStyle, TextStyle, ui, SelectOption
from discord.ui import View, Button, Modal, TextInput, Select

from ...models import AsyncTagManager, Tag


class ConfirmDeleteTag(View):
    def __init__(self, cog, tag: Tag | list[Tag]):
        super().__init__()
        self.cog = cog
        self.tag = tag

    @ui.button(label="Delete", style=ButtonStyle.red)
    async def confirm(self, inter: Interaction, button: Button):
        button.disabled = True
        button.label = "Deleted"
        button.style = ButtonStyle.success
        await self.cog.conn.delete(self.tag)
        if isinstance(self.tag, list):
            self.cog.logger.info(f"{inter.user.name!r} deleted {len(self.tag)} tags")
            await inter.response.edit_message(content=f"Deleted {len(self.tag)} tags!", view=self)
        else:
            self.cog.logger.info(f"{inter.user.name!r} deleted {self.tag.name!r}")
            await inter.response.edit_message(content=f"Deleted {self.tag.name!r}!", view=self)
        self.stop()


class TagButtonView(View):
    def __init__(self, buttons: list[dict[str, str]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buttons = buttons
        for button in self.buttons:
            label, url, emoji = button["label"], button["url"], button["emoji"]
            self.add_item(
                Button(
                    style=ButtonStyle.link,
                    label=label,
                    url=url,
                    emoji=emoji,
                )
            )


class CreateTagModal(Modal, title="Create new tag"):
    name = TextInput(
        label="Tag Name",
        placeholder="The name of the tag",
        style=TextStyle.short,
        required=True,
        min_length=1,
        max_length=50,
    )

    content = TextInput(
        label="Tag Content",
        placeholder="The content of the tag",
        style=TextStyle.long,
        required=True,
        min_length=1,
        max_length=2000,
    )

    display = TextInput(
        label="Tag Style",
        placeholder="'Style' of the tag, (embed, text)",
        default="embed",
        style=TextStyle.short,
        required=False,
    )

    color = TextInput(
        label="Tag Color",
        placeholder="The hex color for the embed",
        default="734ebe",
        style=TextStyle.short,
        required=False,
        min_length=6,
        max_length=6,
    )

    def __init__(self, cog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cog = cog

    async def on_submit(self, inter: Interaction):
        tag = Tag(
            self.name.value,
            self.content.value,
            inter.user.id,
            guild=inter.guild.id if inter.guild else None,
            display=self.display.value,
            color=int(self.color.value, 16),
        )
        await self.cog.conn.insert_model(tag)
        self.cog.logger.info(f"{inter.user.name!r} created {tag.name!r}")
        await inter.response.send_message(
            embed=Embed(title="Created Tag!", description=f"Created tag {tag.name!r}!"), ephemeral=True
        )

    async def on_error(self, inter: Interaction, error: Exception):
        await inter.response.send_message(f"Error creating tag!\n{error}", ephemeral=True)


class EditTagModal(Modal, title="Edit a tag"):
    content = CreateTagModal.content
    display = CreateTagModal.display
    color = CreateTagModal.color

    def __init__(self, cog, tag: Tag, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cog = cog
        self.tag = tag
        self.content.default = self.tag.content
        self.display.default = self.tag.display
        self.color.default = f"{self.tag.color:#08x}"[2:]

    async def on_submit(self, inter: Interaction):
        self.tag.content = self.content.value
        self.tag.display = self.display.value
        self.tag.color = int(self.color.value, 16)
        self.tag.updated = arrow.now()
        await self.cog.conn.update(self.tag)
        self.cog.logger.info(f"{inter.user.name!r} edited {self.tag.name!r}")
        await inter.response.send_message(
            embed=Embed(title="Updated Tag!", description=f"Updated tag {self.tag.name!r}!"), ephemeral=True
        )

    async def on_error(self, inter: Interaction, error: Exception):
        self.cog.logger.info(f"{inter.user.name!r} {self.tag.name!r} error: {error}")
        await inter.response.send_message(f"Error creating tag!\n{error}", ephemeral=True)


class AddTagButtonModal(Modal, title="Add url button to tag"):
    label = TextInput(
        label="Button Label",
        placeholder="Label text for the button",
        style=TextStyle.short,
        required=True,
        max_length=80,
    )

    url = TextInput(
        label="Button URL",
        placeholder="URL for the button",
        style=TextStyle.short,
        required=True,
        max_length=512,
    )

    emoji = TextInput(
        label="Button Emoji",
        placeholder="Emoji for the button (optional)",
        style=TextStyle.short,
        required=False,
        max_length=100,
    )

    def __init__(self, cog, tag: Tag, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cog = cog
        self.tag = tag

    async def on_submit(self, inter: Interaction):
        self.tag.buttons.append(
            {
                "label": self.label.value,
                "url": self.url.value,
                "emoji": self.emoji.value if self.emoji.value != "" else None,
            }
        )
        await self.cog.conn.update(self.tag)
        if 'Edit' in self.title:
            self.cog.logger.info(f"{inter.user.name!r} edited button {self.label.value!r} of {self.tag.name!r}")
        else:
            self.cog.logger.info(f"{inter.user.name!r} added button {self.label.value!r} to {self.tag.name!r}")
        await inter.response.send_message(f"Added button {self.label.value!r} to {self.tag.name!r}!", ephemeral=True)

    async def on_error(self, inter: Interaction, error: Exception):
        await inter.response.send_message(f"Error creating tag button!\n{error}", ephemeral=True)


class TagSelectButton(Select):
    def __init__(self, cog, tag: Tag, mult: bool = False, safe: bool = False):
        super().__init__()
        self.cog = cog
        self.tag = tag
        self.mult = mult
        if safe:
            self.options = [
                SelectOption(label=button["label"], description=button["url"]) for button in self.tag.buttons
            ]
        else:
            self.options = [
                SelectOption(label=button["label"], description=button["url"], emoji=button["emoji"])
                for button in self.tag.buttons
            ]
        super().__init__(
            placeholder=f"Choose button{'s' if mult else ''}",
            min_values=1,
            max_values=len(self.options) if mult else 1,
            options=self.options,
        )

    @property
    def selected(self):
        if self.mult:
            return [b for b in self.tag.buttons if b["label"] in self.values]
        return next(b for b in self.tag.buttons if b["label"] in self.values)

    async def callback(self, interaction: Interaction):
        self.disabled = True
        selected = self.selected
        if isinstance(selected, list):
            for button in selected:
                self.tag.buttons.remove(button)
            await self.cog.conn.update(self.tag)
            self.cog.logger.info(f"{interaction.user.name!r} deleted {len(selected)} buttons from {self.tag.name!r}")
            return await interaction.response.edit_message(content=f"Deleted {len(selected)} buttons!", view=None)
        else:
            self.tag.buttons.remove(selected)
            edit = AddTagButtonModal(self.cog, self.tag)
            edit.title = "Edit button for a tag"
            edit.label.default = selected["label"]
            edit.url.default = selected["url"]
            edit.emoji.default = selected["emoji"]
            self.cog.logger.info(f"{interaction.user.name!r} editing button {edit.label.default!r} on {self.tag.name!r}")
            return await interaction.response.send_modal(edit)


class TagEmbed(Embed):
    def __init__(self, tag: Tag, author: str):
        self.tag = tag
        updated = f" | Updated: {tag.updated.strftime('%Y/%m/%d %H:%M')}" if tag.created != tag.updated else ""
        super().__init__(title=self.tag.name, description=self.tag.content, color=Color(self.tag.color))
        self.set_footer(
            text=f"Used: {tag.used} | Created by {author} {tag.created.strftime('%Y/%m/%d %H:%M')}{updated}"
        )

